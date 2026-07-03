# 🤖 AI Agent Coordination & Decision Engine

> **Infosys Springboard Virtual Internship 7.0** — Multi-Agent Coding Assistant System  
> Built with **LangChain** + **Google Gemini 1.5 Flash**

---

## 📌 Project Overview

A multi-agent AI system where specialized agents collaborate to assist developers with coding tasks. Each agent has a defined role, and a central **Decision Engine (Orchestrator)** coordinates them based on the user's request.

```
User Input
    ↓
Decision Engine (Orchestrator)
    ↓
┌──────────────────────────────────────────────┐
│  Code Generator → Code Reviewer → Test Writer → Doc Agent  │
└──────────────────────────────────────────────┘
    ↓
Final Output (code + review + tests + docs)
```

---

## ✅ Progress Tracker

| Agent | Status | Description |
|-------|--------|-------------|
| 🟢 Code Generator Agent | **Done** | Generates Python code from task descriptions |
| 🔴 Code Reviewer Agent | Upcoming | Reviews code for bugs & improvements |
| 🔴 Test Writer Agent | Upcoming | Generates unit tests |
| 🔴 Documentation Agent | Upcoming | Writes docstrings & README sections |
| 🔴 Decision Engine | Upcoming | Orchestrates all agents intelligently |

---

## 🧠 Agent 1: Code Generator Agent

### What it does
Takes a **natural language task description** and generates **clean, well-commented Python code** using LangChain's chain architecture.

### Key LangChain Concepts Used
| Concept | What it does |
|---------|-------------|
| `ChatGoogleGenerativeAI` | Connects LangChain to Google Gemini LLM |
| `ChatPromptTemplate` | Defines agent role (system) + formats user input |
| `MessagesPlaceholder` | Injects conversation memory into the prompt |
| `ConversationBufferMemory` | Stores full chat history for multi-turn context |
| `StrOutputParser` | Parses LLM response to clean string |
| `chain = prompt \| llm \| parser` | LangChain pipe operator — chains steps together |

### Architecture Flow
```
Task Description (str)
       ↓
memory.load_memory_variables()   ← Load past conversation
       ↓
ChatPromptTemplate                ← Format: system + history + task
       ↓
ChatGoogleGenerativeAI (Gemini)   ← LLM generates code
       ↓
StrOutputParser                   ← Clean string output
       ↓
memory.save_context()             ← Save turn to memory
       ↓
Generated Code (str)
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | Google Gemini 1.5 Flash |
| Agent Framework | LangChain |
| Language | Python 3.10+ |
| Memory | LangChain ConversationBufferMemory |
| Config | python-dotenv |

---

## 🚀 Setup & Run

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/ai-agent-coordination-engine.git
cd ai-agent-coordination-engine
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Your API Key
Create a `.env` file in the root directory:
```
GEMINI_API_KEY=your_actual_api_key_here
```
> Get your free key at: https://aistudio.google.com/app/apikey

### 4. Run the Agent
```bash
python main.py
```

### 5. Example Interaction
```
You ➜  Write a binary search function with edge case handling
# Agent generates code...

You ➜  Now add a version that searches in a rotated sorted array
# Agent REMEMBERS previous code and refines it (memory in action!)

You ➜  history    # See session summary
You ➜  clear      # Reset memory
You ➜  quit       # Exit
```

---

## 📁 Project Structure

```
ai-agent-coordination-engine/
│
├── agents/
│   └── code_generator_agent.py   ← Agent 1: Code Generator (LangChain + Gemini)
│
├── main.py                        ← CLI entry point (interactive session)
├── requirements.txt               ← Python dependencies
├── .env                           ← API key (NOT pushed to GitHub)
├── .gitignore                     ← Protects .env from being committed
└── README.md                      ← This file
```

---

## 🔮 Upcoming (Next Weeks)

- **Week 2**: Code Reviewer Agent — reviews generated code for bugs & improvements
- **Week 3**: Test Writer Agent — generates pytest unit tests automatically
- **Week 4**: Documentation Agent — writes docstrings and README sections
- **Week 5**: Decision Engine — smart orchestrator (LangChain Router/Sequential chains)
- **Week 6**: Web UI (Streamlit/Flask) — full demo interface

---

## 👤 Author

**[Your Name]**  
Infosys Springboard Virtual Internship 7.0  
Multi-Agent AI System | Python Full-Stack Track
