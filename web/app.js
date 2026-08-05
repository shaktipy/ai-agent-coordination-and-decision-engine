// app.js — Code Reviewer Dashboard

document.addEventListener('DOMContentLoaded', () => {
    let mode = 'paste';
    let selectedFile = null;

    const editor = CodeMirror.fromTextArea(document.getElementById('code-editor'), {
        mode: 'python', theme: 'darcula', lineNumbers: true, indentUnit: 4, viewportMargin: Infinity
    });
    editor.setValue(`# Example: paste Python code here\n\ndef vulnerable_fn(data):\n    api_key = "sk-ABCDEFGH1234567890"\n    eval(data)\n    for i in range(1000):\n        for j in range(1000):\n            pass\n`);

    const btnPaste = document.getElementById('btn-mode-paste');
    const btnUpload = document.getElementById('btn-mode-upload');
    const pasteArea = document.getElementById('paste-area');
    const uploadArea = document.getElementById('upload-area');
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const fileInfo = document.getElementById('file-info');
    const fileNameEl = fileInfo.querySelector('.file-name');
    const btnRemove = document.getElementById('btn-remove-file');
    const btnRun = document.getElementById('btn-run');
    const btnLoader = document.getElementById('btn-loader');
    const emptyState = document.getElementById('empty-state');
    const reportContent = document.getElementById('report-content');
    const scoreVal = document.getElementById('score-val');
    const execText = document.getElementById('exec-summary-text');
    const accordion = document.getElementById('agent-accordion');
    const btnPdf = document.getElementById('btn-pdf');

    btnPaste.addEventListener('click', () => {
        mode = 'paste';
        btnPaste.classList.add('active'); btnUpload.classList.remove('active');
        pasteArea.classList.add('active'); uploadArea.classList.remove('active');
    });
    btnUpload.addEventListener('click', () => {
        mode = 'upload';
        btnUpload.classList.add('active'); btnPaste.classList.remove('active');
        uploadArea.classList.add('active'); pasteArea.classList.remove('active');
    });

    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.style.borderColor = 'var(--accent)'; });
    dropZone.addEventListener('dragleave', () => { dropZone.style.borderColor = 'var(--border-color)'; });
    dropZone.addEventListener('drop', e => {
        e.preventDefault(); dropZone.style.borderColor = 'var(--border-color)';
        if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]);
    });
    fileInput.addEventListener('change', () => { if (fileInput.files[0]) handleFile(fileInput.files[0]); });
    btnRemove.addEventListener('click', e => { e.stopPropagation(); selectedFile = null; fileInfo.style.display = 'none'; fileInput.value = ''; });

    function handleFile(f) {
        selectedFile = f; fileNameEl.textContent = f.name; fileInfo.style.display = 'flex';
    }

    function setProgress(pct) {
        const circle = document.querySelector('.progress-ring__circle');
        const r = circle.r.baseVal.value;
        const circ = r * 2 * Math.PI;
        circle.style.strokeDasharray = `${circ} ${circ}`;
        circle.style.strokeDashoffset = circ - (pct / 100) * circ;
        circle.setAttribute('stroke', pct >= 80 ? '#10B981' : pct >= 50 ? '#F59E0B' : '#EF4444');
    }

    btnRun.addEventListener('click', async () => {
        btnRun.disabled = true;
        document.querySelector('.btn-text').style.display = 'none';
        btnLoader.style.display = 'block';

        const focus = document.querySelector('input[name="focus"]:checked').value;
        let report = null;
        try {
            if (mode === 'paste') {
                const res = await fetch('/api/review', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code: editor.getValue(), focus })
                });
                if (!res.ok) throw new Error(await res.text());
                report = await res.json();
            } else {
                if (!selectedFile) { alert('Please select a file first.'); return; }
                const fd = new FormData();
                fd.append('file', selectedFile);
                fd.append('focus', focus);
                const res = await fetch('/api/review/upload', { method: 'POST', body: fd });
                if (!res.ok) throw new Error(await res.text());
                report = await res.json();
            }
            render(report);
        } catch (err) {
            alert(`Error: ${err.message}`);
        } finally {
            btnRun.disabled = false;
            document.querySelector('.btn-text').style.display = 'inline';
            btnLoader.style.display = 'none';
        }
    });

    function render(report) {
        emptyState.style.display = 'none';
        reportContent.style.display = 'flex';
        scoreVal.textContent = report.overall_score;
        setProgress(report.overall_score);
        execText.textContent = report.executive_summary;
        accordion.innerHTML = '';
        report.reports.forEach(rep => {
            const hasCritical = rep.findings.some(f => f.severity === 'critical');
            const hasHigh = rep.findings.some(f => f.severity === 'high');
            const badgeClass = rep.findings.length === 0 ? 'clean' : hasCritical ? 'critical' : hasHigh ? 'high' : '';
            const badgeText = rep.findings.length === 0 ? 'Clean ✓' : `${rep.findings.length} findings`;
            const item = document.createElement('div');
            item.className = 'accordion-item';
            item.innerHTML = `
                <div class="accordion-header">
                    <span class="accordion-title">${rep.agent_name}</span>
                    <div class="accordion-meta">
                        <span class="findings-badge ${badgeClass}">${badgeText}</span>
                        <svg class="chevron" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
                    </div>
                </div>
                <div class="accordion-content">
                    <div class="agent-summary">${rep.summary}</div>
                    ${rep.findings.length ? findingsTable(rep.findings) : ''}
                </div>`;
            item.querySelector('.accordion-header').addEventListener('click', () => {
                const c = item.querySelector('.accordion-content');
                c.classList.toggle('open');
                item.querySelector('.chevron').style.transform = c.classList.contains('open') ? 'rotate(180deg)' : '';
            });
            accordion.appendChild(item);
        });
    }

    function findingsTable(findings) {
        const rows = findings.map(f => `
            <tr>
                <td><span class="severity-tag ${f.severity}">${f.severity}</span></td>
                <td class="line-no">${f.line_number ?? 'Snippet'}</td>
                <td><strong>${f.title}</strong><br><small style="color:var(--text-secondary)">${f.description}</small></td>
                <td><div class="finding-sugg">${esc(f.suggestion)}</div></td>
            </tr>`).join('');
        return `<table class="findings-table">
            <thead><tr><th style="width:90px">Severity</th><th style="width:55px">Line</th><th>Issue</th><th>Suggestion</th></tr></thead>
            <tbody>${rows}</tbody>
        </table>`;
    }

    function esc(s) {
        return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
    }

    btnPdf.addEventListener('click', () => window.open('/api/review/pdf', '_blank'));
});
