"""
Code Generator Agent — AI Agent Coordination & Decision Engine
=============================================================
Agent 1 of the Multi-Agent Coding Assistant System.

This agent takes a natural language task description from the user and
generates clean, well-commented Python code using LangChain + Groq/Gemini.

Supported LLM Providers:
    - Groq  (default) — Free, fast, generous quota. Works in India. ✅
    - Gemini           — Google Gemini via AI Studio key.

Architecture:
    User Input (task description)
         ↓
    CodeGeneratorAgent.run()
         ↓
    [chat_history: list of HumanMessage/AIMessage]
         ↓
    [ChatPromptTemplate: system role + history + user task]
         ↓
    [Groq / Gemini LLM via LangChain]
         ↓
    [StrOutputParser: cleans response]
         ↓
    Generated Code Output

Author: <Your Name>
Project: Infosys Springboard Virtual Internship 7.0
"""

import os
from dotenv import load_dotenv

# ── LangChain core imports ─────────────────────────────────────────────────────
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage

# Load environment variables from .env file
load_dotenv()


# ── Constants ──────────────────────────────────────────────────────────────────
GROQ_API_KEY   = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# System prompt — defines the agent's role, behavior, and rules
SYSTEM_PROMPT = """You are an expert Python Code Generator Agent, part of a 
Multi-Agent Coding Assistant System.

Your ONLY job is to generate clean, working Python code based on the user's 
task description. You are specialized, focused, and highly skilled at this task.

Rules you MUST follow:
1. Generate ONLY Python code — no other languages unless explicitly asked
2. Always include brief, helpful comments explaining key logic
3. Follow PEP8 style conventions
4. Add a docstring to every function you write
5. Handle basic edge cases in your code
6. Do NOT include lengthy explanations outside the code — use comments inside it
7. If the task is unclear, write code for the most logical interpretation

Output format:
- Start directly with the code (no preamble like "Here is the code:")
- End with a brief # Usage example in comments showing how to call the function
"""


def _build_llm(provider: str, model: str, temperature: float):
    """
    Factory function — returns the correct LangChain LLM based on provider.

    LangChain's beauty: both Groq and Gemini have the SAME interface.
    We just swap the class, the chain code stays identical!

    Args:
        provider   : "groq" or "gemini"
        model      : model name string
        temperature: creativity level (0.0 – 1.0)

    Returns:
        A LangChain chat model instance
    """
    if provider == "groq":
        # Groq — free tier, fast inference, India-friendly
        # Free key: https://console.groq.com
        from langchain_groq import ChatGroq
        return ChatGroq(
            model=model,
            groq_api_key=GROQ_API_KEY,
            temperature=temperature,
        )

    elif provider == "gemini":
        # Google Gemini — via AI Studio key
        # Free key: https://aistudio.google.com/app/apikey
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=model,
            google_api_key=GEMINI_API_KEY,
            temperature=temperature,
        )

    else:
        raise ValueError(f"Unknown provider '{provider}'. Use 'groq' or 'gemini'.")


class CodeGeneratorAgent:
    """
    LangChain-based Code Generator Agent.

    Supports both Groq and Gemini as LLM backends.
    Maintains a conversation history (list of HumanMessage / AIMessage objects)
    so the agent can remember and refine previously generated code within a session.

    Attributes:
        provider     : "groq" or "gemini"
        llm          : LangChain LLM instance (Groq or Gemini)
        chat_history : List[BaseMessage] — in-memory conversation store
        chain        : LangChain chain (prompt | llm | parser)
    """

    def __init__(
        self,
        provider: str = "groq",
        model: str = "llama-3.1-8b-instant",
        temperature: float = 0.2,
    ):
        """
        Initialize the Code Generator Agent.

        Args:
            provider   : LLM provider — "groq" (default) or "gemini"
            model      : Model name for the provider.
                         Groq models  : "llama-3.1-8b-instant", "llama3-8b-8192", "mixtral-8x7b-32768"
                         Gemini models: "gemini-2.0-flash", "gemini-1.5-pro"
            temperature: 0.0 = deterministic, 1.0 = creative. Low = better for code.
        """
        self.provider = provider

        # ── Step 1: Build the LLM via factory function ─────────────────────────
        self.llm = _build_llm(provider, model, temperature)

        # ── Step 2: In-memory conversation history ─────────────────────────────
        # Plain Python list of HumanMessage / AIMessage objects.
        # Modern LangChain approach — no deprecated Memory classes needed.
        #   HumanMessage → user's input (the coding task)
        #   AIMessage    → agent's response (generated code)
        self.chat_history: list = []

        # ── Step 3: Build the Prompt Template ──────────────────────────────────
        # Structure:
        #   ("system", ...)        → agent's role + rules (always first)
        #   MessagesPlaceholder    → full chat_history injected here
        #   ("human", "{task}")    → current user task
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{task}"),
        ])

        # ── Step 4: Build the LangChain Chain ──────────────────────────────────
        # Pipe operator ( | ) chains steps:
        #   prompt  → formats messages for the LLM
        #   llm     → sends to Groq/Gemini, gets AI response
        #   parser  → converts AIMessage object → plain string
        self.chain = self.prompt | self.llm | StrOutputParser()

        print(f"[Agent Init] Code Generator Agent ready")
        print(f"[Agent Init] Provider: {provider.upper()} | Model: {model} | Temp: {temperature}")

    def run(self, task: str) -> str:
        """
        Generate Python code for the given task description.

        Steps:
        1. Invoke LangChain chain with current task + full chat history
        2. Append both user message and AI response to chat_history
        3. Return the generated code string

        Args:
            task: Natural language description of what code to generate

        Returns:
            str: Generated Python code with comments
        """
        if not task.strip():
            return "Error: Please provide a task description."

        print(f"\n[Agent Running] Task: {task[:60]}{'...' if len(task) > 60 else ''}")
        print(f"[Memory] Turns in history: {len(self.chat_history) // 2}")

        # Invoke the LangChain chain — passes task + history to LLM
        result = self.chain.invoke({
            "task": task,
            "chat_history": self.chat_history,
        })

        # Manually save this turn to history
        self.chat_history.append(HumanMessage(content=task))
        self.chat_history.append(AIMessage(content=result))

        return result

    def clear_memory(self):
        """Clear conversation history — start a fresh session."""
        self.chat_history.clear()
        print("[Memory] Cleared. Starting fresh session.")

    def get_history_summary(self) -> str:
        """Return a readable summary of tasks handled in this session."""
        if not self.chat_history:
            return "No tasks handled yet in this session."

        turns = len(self.chat_history) // 2
        summary = f"Session History ({turns} task(s) handled):\n"
        for i, msg in enumerate(self.chat_history):
            if isinstance(msg, HumanMessage):
                task_num = (i // 2) + 1
                preview = msg.content[:80] + ("..." if len(msg.content) > 80 else "")
                summary += f"  Task {task_num}: {preview}\n"
        return summary


# ── Standalone test — run this file directly to test the agent ─────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  CODE GENERATOR AGENT — Standalone Test")
    print("  Provider: Groq (llama-3.1-8b-instant)")
    print("=" * 60)

    # Check Groq API key
    if not GROQ_API_KEY or "your" in GROQ_API_KEY.lower():
        print("\n[ERROR] Please set GROQ_API_KEY in .env file!")
        print("Get your FREE key at: https://console.groq.com")
        exit(1)

    # Initialize agent with Groq
    agent = CodeGeneratorAgent(
        provider="groq",
        model="llama-3.1-8b-instant",  # fast + free
        temperature=0.2,
    )

    # ── Test 1: Basic code generation ─────────────────────────────────────────
    print("\n--- Test 1: Prime Number Checker ---")
    task1 = "Write a function to check if a number is prime. Include test cases."
    output1 = agent.run(task1)
    print("\nGenerated Code:")
    print("-" * 40)
    print(output1)

    # ── Test 2: Memory test — follow-up instruction ────────────────────────────
    print("\n--- Test 2: Memory Follow-up (refine previous code) ---")
    task2 = "Now modify the above function to find all primes up to N using the Sieve of Eratosthenes."
    output2 = agent.run(task2)
    print("\nRefined Code:")
    print("-" * 40)
    print(output2)

    # ── Session summary ────────────────────────────────────────────────────────
    print("\n--- Session Summary ---")
    print(agent.get_history_summary())
