# 🤖 Multi-Agent Automated Code Review & Decision Engine

> **Infosys Springboard Virtual Internship 7.0**  
> Built with **LangChain · Groq (Llama 3) · FastAPI · ReportLab**

---

## 📌 Overview

A fully automated, multi-agent code review system. A central **Master Orchestrator (Decision Engine)** analyses the user's request, decides which review dimension is needed, and dispatches to a team of specialised reviewer agents. All findings are merged by an **Aggregator** into a structured health-scored report, exportable as a **PDF** or browsable in a dark-mode **Web Dashboard**.

---

## 🏗️ System Architecture

```
            ┌─────────────────────────┐
            │      Web Dashboard       │
            │  (paste code / upload)   │
            └────────────┬────────────┘
                         │  POST /api/review
                         ▼
         ┌───────────────────────────────┐
         │     Master Orchestrator        │
         │  · Keyword + LLM routing       │
         │  · Selects agent focus         │
         └──────────┬────────────────────┘
                    │
       ┌────────────┼────────────┬───────────────┐
       ▼            ▼            ▼               ▼
 ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────────┐
 │ Security │ │  Perf &  │ │ Quality  │ │  Docs &      │
 │  Agent   │ │ Complexity│ │  Agent   │ │  Tests Agent │
 └────┬─────┘ └────┬─────┘ └────┬─────┘ └──────┬───────┘
      │            │            │              │
  bandit        radon cc     pylint       docstring
  secrets       radon mi     naming       test-presence
  unsafe-fn     nested-loop  checker      checker
      │            │            │              │
      └────────────┴────────────┴──────────────┘
                         │
             ┌───────────────────────┐
             │      Aggregator        │
             │  · Merge findings      │
             │  · Score 0–100         │
             │  · Executive summary   │
             └───────────┬───────────┘
                         │
             ┌───────────────────────┐
             │    Report Renderer     │
             │  · HTML web view       │
             │  · PDF export          │
             └───────────────────────┘
```

---

## 🧠 Agents & Components

| Component | Role |
|---|---|
| **MasterOrchestrator** | Routes by keyword heuristic or LLM classification to `SECURITY / PERFORMANCE / QUALITY / DOCS / FULL` |
| **SecurityAgent** | Integrates `bandit`, regex secret scanner, and AST unsafe-function detector |
| **PerformanceAgent** | Uses `radon cc` (cyclomatic complexity), `radon mi` (maintainability index), and AST nested-loop depth |
| **QualityAgent** | Runs `pylint` and PEP 8 naming convention AST checker |
| **DocsTestAgent** | Checks public docstring coverage and unit-test file presence |
| **Aggregator** | Merges findings, computes health score (critical: −15, high: −8, medium: −4, low: −1), writes executive summary |
| **ReportRenderer** | Builds styled multi-section PDF from `FinalReviewReport` via `reportlab` |
| **FastAPI Server** | Serves REST API (`/api/review`, `/api/review/upload`, `/api/review/pdf`) and the web dashboard |

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| Agent / LLM | LangChain, Groq (Llama-3.3-70b, Llama-3.1-8b-instant) |
| Static Analysis | bandit, radon, pylint, AST (stdlib) |
| Data Contracts | Pydantic v2 |
| Web API | FastAPI, Uvicorn, Python-Multipart |
| PDF Export | ReportLab |
| Dashboard | HTML5, Vanilla CSS, JavaScript (CodeMirror editor) |
| Tests | pytest |

---

## 🚀 Setup & Usage

### 1 · Install dependencies
```bash
pip install -r requirements.txt
```

### 2 · Configure environment
Create `.env` in the project root:
```env
GROQ_API_KEY=your_groq_api_key_here
```

### 3a · Start the Web Dashboard (recommended)
```bash
uvicorn api.server:app --reload
```
Open **http://localhost:8000** in your browser.

### 3b · CLI mode
```bash
python main.py
```
Paste Python code, type `RUN` on a new line to start analysis, or `quit` to exit.

### 4 · Run tests
```bash
python -m pytest tests/ -v
```

---

## 📁 Project Structure

```
ai-agent-coordination-engine/
├── agents/
│   ├── reviewers/
│   │   ├── security_agent.py
│   │   ├── performance_agent.py
│   │   ├── quality_agent.py
│   │   └── docs_test_agent.py
│   ├── tools/
│   │   ├── bandit_scan_tool.py
│   │   ├── secret_pattern_tool.py
│   │   ├── unsafe_function_tool.py
│   │   ├── radon_complexity_tool.py
│   │   ├── nested_loop_tool.py
│   │   ├── pylint_scan_tool.py
│   │   ├── naming_convention_tool.py
│   │   ├── docstring_coverage_tool.py
│   │   ├── test_presence_tool.py
│   │   └── file_manager_tool.py   ← read-only
│   ├── utils/
│   │   └── llm_factory.py
│   ├── orchestrator.py
│   ├── aggregator.py
│   └── report_renderer.py
├── api/
│   └── server.py
├── web/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── models/
│   └── schemas.py
├── tests/
│   ├── test_tools.py
│   └── test_orchestrator.py
├── main.py
├── requirements.txt
├── .env
└── README.md
```

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 👤 Author

**SHAKTI VARDHAN SINGH**  
Infosys Springboard Virtual Internship 7.0  
Multi-Agent AI Systems | Python Full-Stack Track
