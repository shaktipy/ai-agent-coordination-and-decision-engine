# 🤖 AI Agent Coordination & Decision Engine

> **Infosys Springboard Virtual Internship 7.0** — Multi-Agent System  
> Built with **LangChain** + **Google Gemini** + **Groq (Llama 3)**

---

## 📌 Project Overview

A multi-agent AI system where specialized agents collaborate to assist developers and execute tasks. A central **Master Orchestrator (Decision Engine)** evaluates user queries and routes them to the appropriate agent.

```
                    User Input
                        ↓
         Master Orchestrator (Router LLM)
                        ↓
       ┌─────────────────┴─────────────────┐
       ▼                                   ▼
┌──────────────┐                   ┌──────────────┐
│     CODE     │                   │     TOOL     │
│  Generator   │                   │    Agent     │
│    Agent     │                   │   (ReAct)    │
└──────────────┘                   └──────┬───────┘
                                          │
                  ┌───────────────┬───────┼───────────────┬───────────────┐
                  ▼               ▼       ▼               ▼               ▼
            ┌───────────┐   ┌──────────┐┌───────────┐   ┌──────────┐    ┌───────────┐
            │Web Search │   │Calculator││ Datetime  │   │   File   │    │    API    │
            │   Tool    │   │   Tool   ││   Tool    │   │ Manager  │    │ Connector │
            └───────────┘   └──────────┘└───────────┘   └──────────┘    └───────────┘
```

---

## ✅ Progress Tracker

| Agent / Component | Status | Description |
|---|---|---|
| 🟢 **Code Generator Agent** | **Done** | Generates, modifies, and explains Python code with multi-turn memory. |
| 🟢 **Tool Agent (ReAct)** | **Done** | A ReAct agent integrated with enterprise tools to query external APIs, execute math, search the web, manage local files, and check datetime. |
| 🟢 **Master Orchestrator** | **Done** | An LLM-based router that dynamically classifies inputs to route tasks to the CODE or TOOL agent. |
| 🔴 **Code Reviewer / Test Writer** | Upcoming | Planned future enhancements. |

---

## 🧠 Components & Agents

### 1. Master Orchestrator (Decision Engine)
- **Role**: Entry point for all user requests.
- **How it works**: Uses a high-speed router chain (powered by Groq / Llama 3) to analyze queries and output either `CODE` or `TOOL`.
- **File**: [main.py](file:///c:/Users/msi/OneDrive/Desktop/AI-agent-coordination-engine/main.py)

### 2. Code Generator Agent
- **Role**: Handles developer tasks like writing code, debugging, or explanation.
- **Implementation**: Utilizes LangChain prompts, conversation memory (`ConversationBufferMemory`), and Gemini LLM.
- **File**: [code_generator_agent.py](file:///c:/Users/msi/OneDrive/Desktop/AI-agent-coordination-engine/agents/code_generator_agent.py)

### 3. Tool Agent (ReAct)
- **Role**: Executes dynamic actions using external tools.
- **Implementation**: Structured using a ReAct architecture that binds a suite of enterprise tools to the LLM.
- **File**: [tool_agent.py](file:///c:/Users/msi/OneDrive/Desktop/AI-agent-coordination-engine/agents/tool_agent.py)
- **Enterprise Tools**:
  - **Web Search**: Queries Google/DuckDuckGo for real-time information ([web_search_tool.py](file:///c:/Users/msi/OneDrive/Desktop/AI-agent-coordination-engine/agents/tools/web_search_tool.py)).
  - **Calculator**: Securely evaluates math expressions ([calculator_tool.py](file:///c:/Users/msi/OneDrive/Desktop/AI-agent-coordination-engine/agents/tools/calculator_tool.py)).
  - **Datetime**: Returns current date, time, or relative dates ([datetime_tool.py](file:///c:/Users/msi/OneDrive/Desktop/AI-agent-coordination-engine/agents/tools/datetime_tool.py)).
  - **File Manager**: Safely creates, reads, and updates local workspace files ([file_manager_tool.py](file:///c:/Users/msi/OneDrive/Desktop/AI-agent-coordination-engine/agents/tools/file_manager_tool.py)).
  - **API Connector**: Sends HTTP requests (GET/POST) to external endpoints ([api_connector_tool.py](file:///c:/Users/msi/OneDrive/Desktop/AI-agent-coordination-engine/agents/tools/api_connector_tool.py)).

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| LLMs | Google Gemini 1.5 Flash, Groq Llama 3.1 8B |
| Agent Framework | LangChain |
| Language | Python 3.10+ |
| Memory | LangChain ConversationBufferMemory |
| Configuration | python-dotenv |

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

### 3. Setup Environment Variables
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Run the Engine
```bash
python main.py
```

### 5. Interaction Examples
- **Code task routing**:
  `You ➜ Write a Python class representing a bank account.`
  *(Orchestrator routes to Code Generator)*
- **Tool task routing**:
  `You ➜ Search the web for latest space news or calculate (234 * 12) + 98.`
  *(Orchestrator routes to Tool Agent)*

---

## 📁 Project Structure

```
ai-agent-coordination-engine/
├── agents/
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── api_connector_tool.py
│   │   ├── calculator_tool.py
│   │   ├── datetime_tool.py
│   │   ├── file_manager_tool.py
│   │   └── web_search_tool.py
│   ├── __init__.py
│   ├── code_generator_agent.py
│   ├── tool_agent.py
│   └── tool_orchestrator.py
├── tests/
│   └── __init__.py
├── main.py                        ← Main Entry Point / CLI Orchestrator
├── requirements.txt
├── .env                           ← API keys config (Git ignored)
├── .gitignore
├── LICENSE
└── README.md                      ← This documentation file
```

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 👤 Author

**SHAKTI VARDHAN SINGH**  
Infosys Springboard Virtual Internship 7.0  
Multi-Agent AI System | Python Full-Stack Track
