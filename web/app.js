// app.js — Nexus Code Reviewer Dashboard
// Enterprise Workflow Platform · Infosys Springboard 7.0

document.addEventListener('DOMContentLoaded', () => {
    // ── State ────────────────────────────────────────────────────
    let mode = 'paste';
    let selectedFile = null;
    let lastReport = null;

    // ── Session ID ───────────────────────────────────────────────
    let sessionId = localStorage.getItem('review_session_id');
    if (!sessionId) {
        sessionId = 'session_' + Math.random().toString(36).substring(2, 9);
        localStorage.setItem('review_session_id', sessionId);
    }

    // ── CodeMirror Editor ────────────────────────────────────────
    const editor = CodeMirror.fromTextArea(document.getElementById('code-editor'), {
        mode: 'python',
        theme: 'darcula',
        lineNumbers: true,
        indentUnit: 4,
        viewportMargin: Infinity,
        extraKeys: {
            'Ctrl-Enter': () => triggerRun()
        }
    });
    editor.setValue(
        `# Example: paste your Python code here\n\ndef vulnerable_fn(data):\n    api_key = "sk-ABCDEFGH1234567890"\n    eval(data)                         # unsafe\n    for i in range(1000):\n        for j in range(1000):          # O(n²) nested loop\n            pass\n`
    );

    // ── DOM References ───────────────────────────────────────────
    const btnPaste      = document.getElementById('btn-mode-paste');
    const btnUpload     = document.getElementById('btn-mode-upload');
    const pasteArea     = document.getElementById('paste-area');
    const uploadArea    = document.getElementById('upload-area');
    const dropZone      = document.getElementById('drop-zone');
    const fileInput     = document.getElementById('file-input');
    const fileInfo      = document.getElementById('file-info');
    const fileNameEl    = fileInfo.querySelector('.file-name');
    const btnRemove     = document.getElementById('btn-remove-file');
    const btnRun        = document.getElementById('btn-run');
    const btnLoader     = document.getElementById('btn-loader');
    const emptyState    = document.getElementById('empty-state');
    const skeletonWrap  = document.getElementById('skeleton-wrapper');
    const reportContent = document.getElementById('report-content');
    const scoreVal      = document.getElementById('score-val');
    const execText      = document.getElementById('exec-summary-text');
    const accordion     = document.getElementById('agent-accordion');
    const btnPdf        = document.getElementById('btn-pdf');
    const agentProgress = document.getElementById('agent-progress');
    const findingsTotal = document.getElementById('findings-count-total');

    // Results / History tabs
    const tabResults    = document.getElementById('tab-results');
    const tabHistory    = document.getElementById('tab-history');
    const resultsPaneEl = document.getElementById('results-pane');
    const historyPane   = document.getElementById('history-pane');

    // ── Input Mode Toggle ────────────────────────────────────────
    btnPaste.addEventListener('click', () => {
        mode = 'paste';
        setActiveTab(btnPaste, btnUpload);
        pasteArea.classList.add('active');
        uploadArea.classList.remove('active');
    });

    btnUpload.addEventListener('click', () => {
        mode = 'upload';
        setActiveTab(btnUpload, btnPaste);
        uploadArea.classList.add('active');
        pasteArea.classList.remove('active');
    });

    function setActiveTab(on, off) {
        on.classList.add('active');
        off.classList.remove('active');
    }

    // ── File Upload ──────────────────────────────────────────────
    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', e => {
        e.preventDefault();
        dropZone.style.borderColor = 'var(--accent)';
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.style.borderColor = '';
    });

    dropZone.addEventListener('drop', e => {
        e.preventDefault();
        dropZone.style.borderColor = '';
        if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]);
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files[0]) handleFile(fileInput.files[0]);
    });

    btnRemove.addEventListener('click', e => {
        e.stopPropagation();
        selectedFile = null;
        fileInfo.style.display = 'none';
        fileInput.value = '';
    });

    function handleFile(f) {
        selectedFile = f;
        fileNameEl.textContent = f.name;
        fileInfo.style.display = 'flex';
    }

    // ── Results / History Tab Switching ─────────────────────────
    tabResults.addEventListener('click', () => {
        tabResults.classList.add('active');
        tabHistory.classList.remove('active');
        resultsPaneEl.style.display = 'flex';
        historyPane.classList.remove('active');
    });

    tabHistory.addEventListener('click', async () => {
        tabHistory.classList.add('active');
        tabResults.classList.remove('active');
        resultsPaneEl.style.display = 'none';
        historyPane.classList.add('active');
        await loadHistory();
    });

    // ── Keyboard Shortcut: Ctrl+Enter ────────────────────────────
    document.addEventListener('keydown', e => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            triggerRun();
        }
    });

    // ── Score Progress Ring ──────────────────────────────────────
    function setProgress(pct) {
        const circle = document.querySelector('.progress-ring__circle');
        const r = circle.r.baseVal.value;
        const circ = 2 * Math.PI * r;
        circle.style.strokeDasharray = `${circ} ${circ}`;
        circle.style.strokeDashoffset = circ - (pct / 100) * circ;

        let color;
        if (pct >= 80) {
            color = '#10B981';
        } else if (pct >= 50) {
            color = '#F59E0B';
        } else {
            color = '#EF4444';
        }
        circle.setAttribute('stroke', color);
        // Score number stays white — only ring colour changes
    }

    // ── Agent Progress Animation ─────────────────────────────────
    const agentSteps = {
        security:    document.getElementById('step-security'),
        performance: document.getElementById('step-performance'),
        quality:     document.getElementById('step-quality'),
        docs:        document.getElementById('step-docs'),
    };

    let progressInterval = null;

    function startProgressAnimation() {
        const steps = Object.values(agentSteps);
        let idx = 0;
        steps.forEach(s => {
            s.classList.remove('running', 'done');
        });
        agentProgress.classList.add('visible');

        progressInterval = setInterval(() => {
            if (idx > 0) {
                steps[idx - 1].classList.remove('running');
                steps[idx - 1].classList.add('done');
                steps[idx - 1].querySelector('.agent-step-icon').textContent = '✓';
            }
            if (idx < steps.length) {
                steps[idx].classList.add('running');
                idx++;
            } else {
                clearInterval(progressInterval);
            }
        }, 900);
    }

    function stopProgressAnimation(success) {
        clearInterval(progressInterval);
        const steps = Object.values(agentSteps);
        steps.forEach(s => {
            s.classList.remove('running');
            if (success) {
                s.classList.add('done');
                s.querySelector('.agent-step-icon').textContent = '✓';
            }
        });
        setTimeout(() => {
            agentProgress.classList.remove('visible');
        }, 1200);
    }

    // ── Run Analysis ─────────────────────────────────────────────
    function triggerRun() {
        if (btnRun.disabled) return;
        btnRun.click();
    }

    btnRun.addEventListener('click', async () => {
        // UI: loading state
        btnRun.disabled = true;
        document.querySelectorAll('.btn-text').forEach(el => el.style.display = 'none');
        btnLoader.style.display = 'block';

        // Hide report, show skeleton
        emptyState.style.display = 'none';
        reportContent.style.display = 'none';
        skeletonWrap.classList.add('visible');

        // Start agent progress animation
        startProgressAnimation();

        const query = document.getElementById('chat-input').value;
        let report = null;

        try {
            if (mode === 'paste') {
                const res = await fetch('/api/review', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        code: editor.getValue(),
                        query,
                        session_id: sessionId
                    })
                });
                if (!res.ok) throw new Error(await res.text());
                report = await res.json();
            } else {
                if (!selectedFile) {
                    alert('Please select a file first.');
                    return;
                }
                const fd = new FormData();
                fd.append('file', selectedFile);
                fd.append('query', query);
                fd.append('session_id', sessionId);
                const res = await fetch('/api/review/upload', { method: 'POST', body: fd });
                if (!res.ok) throw new Error(await res.text());
                report = await res.json();
            }

            stopProgressAnimation(true);
            lastReport = report;
            render(report);

        } catch (err) {
            stopProgressAnimation(false);
            skeletonWrap.classList.remove('visible');
            emptyState.style.display = 'flex';
            alert(`❌ Error: ${err.message}`);
        } finally {
            btnRun.disabled = false;
            document.querySelectorAll('.btn-text').forEach(el => el.style.display = 'inline');
            btnLoader.style.display = 'none';
        }
    });

    // ── Render Report ─────────────────────────────────────────────
    function render(report) {
        skeletonWrap.classList.remove('visible');
        emptyState.style.display = 'none';
        reportContent.style.display = 'flex';

        // Score
        scoreVal.textContent = report.overall_score;
        setProgress(report.overall_score);

        // Executive summary
        execText.textContent = report.executive_summary;

        // Total findings count
        const totalFindings = report.reports.reduce((acc, r) => acc + r.findings.length, 0);
        findingsTotal.textContent = `${totalFindings} total finding${totalFindings !== 1 ? 's' : ''}`;

        // Build accordion
        accordion.innerHTML = '';
        report.reports.forEach(rep => buildAccordionItem(rep));
    }

    // ── Accordion Item ────────────────────────────────────────────
    const agentMeta = {
        'Security Review Agent':          { icon: '🔒', color: '#EF4444', bg: 'rgba(239,68,68,0.12)' },
        'Performance & Complexity Agent': { icon: '⚡', color: '#F59E0B', bg: 'rgba(245,158,11,0.12)' },
        'Code Quality Agent':             { icon: '✨', color: '#3B82F6', bg: 'rgba(59,130,246,0.12)' },
        'Docs & Tests Agent':             { icon: '📚', color: '#10B981', bg: 'rgba(16,185,129,0.12)' },
    };

    function buildAccordionItem(rep) {
        const hasCritical = rep.findings.some(f => f.severity === 'critical');
        const hasHigh     = rep.findings.some(f => f.severity === 'high');
        const hasMedium   = rep.findings.some(f => f.severity === 'medium');

        const badgeClass = rep.findings.length === 0
            ? 'clean'
            : hasCritical ? 'critical'
            : hasHigh     ? 'high'
            : hasMedium   ? 'medium' : '';

        const badgeText = rep.findings.length === 0
            ? '✓ Clean'
            : `${rep.findings.length} finding${rep.findings.length !== 1 ? 's' : ''}`;

        const meta = agentMeta[rep.agent_name] || { icon: '🤖', color: '#64748B', bg: 'rgba(100,116,139,0.12)' };

        const item = document.createElement('div');
        item.className = `accordion-item${hasCritical ? ' has-critical' : hasHigh ? ' has-high' : ''}`;

        item.innerHTML = `
            <div class="accordion-header">
                <span class="accordion-title">
                    <span class="agent-icon" style="background:${meta.bg}; color:${meta.color}">${meta.icon}</span>
                    ${rep.agent_name}
                </span>
                <div class="accordion-meta">
                    <span class="findings-badge ${badgeClass}">${badgeText}</span>
                    <svg class="chevron" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg>
                </div>
            </div>
            <div class="accordion-content">
                <div class="agent-summary">${esc(rep.summary)}</div>
                ${rep.findings.length ? findingsTable(rep.findings) : '<p style="color:var(--text-secondary);font-size:0.88rem;text-align:center;padding:12px">No issues found by this agent 🎉</p>'}
            </div>`;

        const header = item.querySelector('.accordion-header');
        const content = item.querySelector('.accordion-content');
        const chevron = item.querySelector('.chevron');

        header.addEventListener('click', () => {
            const isOpen = content.classList.toggle('open');
            chevron.style.transform = isOpen ? 'rotate(180deg)' : '';
        });

        // Auto-open if has critical/high findings
        if (hasCritical || hasHigh) {
            content.classList.add('open');
            chevron.style.transform = 'rotate(180deg)';
        }

        accordion.appendChild(item);
    }

    // ── Findings Table ────────────────────────────────────────────
    function findingsTable(findings) {
        const rows = findings.map(f => `
            <tr>
                <td><span class="severity-tag ${f.severity}">${f.severity}</span></td>
                <td><span class="line-no">${f.line_number != null ? `L${f.line_number}` : '—'}</span></td>
                <td>
                    <strong>${esc(f.title)}</strong><br>
                    <small style="color:var(--text-secondary);line-height:1.4">${esc(f.description)}</small>
                </td>
                <td>
                    <div class="finding-sugg" style="position:relative">
                        ${esc(f.suggestion)}
                        <button class="copy-btn" onclick="copyText(this, ${JSON.stringify(f.suggestion)})">Copy</button>
                    </div>
                </td>
            </tr>`).join('');

        return `<table class="findings-table">
            <thead><tr>
                <th style="width:85px">Severity</th>
                <th style="width:50px">Line</th>
                <th>Issue</th>
                <th>Suggestion</th>
            </tr></thead>
            <tbody>${rows}</tbody>
        </table>`;
    }

    // ── History Tab ───────────────────────────────────────────────
    async function loadHistory() {
        const reviewsEl  = document.getElementById('hist-reviews');
        const issuesEl   = document.getElementById('hist-issues');
        const issuesList = document.getElementById('hist-issues-list');
        const learnsList = document.getElementById('hist-learnings-list');

        try {
            const res = await fetch('/api/history');
            if (!res.ok) throw new Error('Failed to fetch history');
            const data = await res.json();

            reviewsEl.textContent = data.past_reviews_count ?? 0;
            issuesEl.textContent  = (data.recurring_issues ?? []).length;

            // Recurring issues
            const issues = data.recurring_issues ?? [];
            if (issues.length > 0) {
                issuesList.innerHTML = issues.map(i => `<li>${esc(i)}</li>`).join('');
            } else {
                issuesList.innerHTML = '<div class="history-empty">No recurring issues detected yet.</div>';
            }

            // Learnings
            const learns = data.learnings ?? [];
            if (learns.length > 0) {
                learnsList.innerHTML = learns.map(l => `<li>${esc(l)}</li>`).join('');
            } else {
                learnsList.innerHTML = '<div class="history-empty">Use "remember …" in the query box to persist notes.</div>';
            }

        } catch (e) {
            issuesList.innerHTML = `<div class="history-empty" style="color:var(--red)">Could not load history: ${e.message}</div>`;
        }
    }

    // ── PDF Export ────────────────────────────────────────────────
    btnPdf.addEventListener('click', () => {
        btnPdf.textContent = '⏳ Generating…';
        btnPdf.disabled = true;
        const win = window.open('/api/review/pdf', '_blank');
        if (win) {
            setTimeout(() => {
                btnPdf.textContent = '↓ Export PDF';
                btnPdf.disabled = false;
            }, 2500);
        } else {
            btnPdf.textContent = '↓ Export PDF';
            btnPdf.disabled = false;
        }
    });

    // ── Utilities ─────────────────────────────────────────────────
    function esc(s) {
        return String(s)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }
});

// Global: copy-to-clipboard (accessible from inline onclick)
window.copyText = function(btn, text) {
    navigator.clipboard.writeText(text).then(() => {
        const original = btn.textContent;
        btn.textContent = '✓ Copied';
        btn.style.background = 'var(--green)';
        btn.style.color = '#fff';
        setTimeout(() => {
            btn.textContent = original;
            btn.style.background = '';
            btn.style.color = '';
        }, 1800);
    }).catch(() => {
        btn.textContent = 'Failed';
    });
};
