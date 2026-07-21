"""
main.py — Entry Point: AI Agent Coordination & Decision Engine
=============================================================
Run this file to interact with the Master Orchestrator via CLI.

The orchestrator automatically routes tasks to:
- CodeGeneratorAgent : Generates Python code from task descriptions.
- ToolAgent          : ReAct agent with enterprise tool integrations.

Usage:
    python main.py

Commands during interactive session:
    - Type any task/question and the orchestrator handles routing
    - Type 'quit'     to exit
"""

import sys
import io

# Fix Windows console UnicodeEncodeError for emojis
if isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout.reconfigure(encoding='utf-8')

from agents.code_generator_agent import CodeGeneratorAgent
from agents.tool_agent import ToolAgent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# We can import _build_llm from tool_agent to use for the router
from agents.tool_agent import _build_llm


# ── Banner & UI helpers ────────────────────────────────────────────────────────

def print_banner():
    """Print the main welcome banner."""
    print("\n" + "=" * 65)
    print("   AI AGENT COORDINATION & DECISION ENGINE")
    print("   Infosys Springboard Virtual Internship 7.0")
    print("=" * 65)


def print_session_header():
    """Print the interactive session header."""
    print(f"\n{'=' * 65}")
    print(f"  Active Agent: Master Orchestrator (Auto-Routing)")
    print(f"  Commands: 'quit' to exit")
    print(f"{'=' * 65}\n")


def print_output(label: str, content: str):
    """Format and print agent output."""
    print(f"\n{'=' * 65}")
    print(f"  {label}:")
    print(f"{'=' * 65}")
    print(content)
    print(f"{'=' * 65}\n")


class MasterOrchestrator:
    def __init__(self):
        print("\n[Loading] Initializing Code Generator Agent...")
        self.code_agent = CodeGeneratorAgent()
        
        print("\n[Loading] Initializing Tool Agent with enterprise tools...")
        self.tool_agent = ToolAgent(provider="groq", verbose=True)
        
        print("\n[Loading] Initializing Router LLM...")
        self.llm = _build_llm("groq", "llama-3.1-8b-instant", 0.0)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", 
             "You are an intelligent router for a multi-agent system. "
             "Your job is to classify the user's task into one of two categories:\n"
             "1. 'CODE': The user wants to write, generate, modify, debug, or explain programming code.\n"
             "2. 'TOOL': The user wants to calculate something, search the web, check the date/time, manage files, fetch APIs, or ask a general knowledge question.\n"
             "Output EXACTLY the word 'CODE' or 'TOOL' and nothing else."
            ),
            ("human", "{task}")
        ])
        self.router_chain = self.prompt | self.llm | StrOutputParser()
        print("[Router Init] ✅ Master Orchestrator ready\n")

    def run(self):
        print_session_header()
        
        while True:
            try:
                user_input = input("You ➜  ").strip()

                if not user_input:
                    continue
                elif user_input.lower() == "quit":
                    print("\nGoodbye! Shutting down.")
                    break
                elif user_input.lower() in ("history", "clear", "tools", "log", "switch"):
                    # Handle some of the old legacy commands explicitly or just route them
                    print("\n[System] Note: 'switch' is no longer needed. History and tool commands can be asked directly!")
                    continue

                # Classify the task
                decision = self.router_chain.invoke({"task": user_input}).strip().upper()
                
                if "CODE" in decision:
                    print("\n[Orchestrator] 🔀 Task classified as CODE. Routing to Code Generator Agent...")
                    result = self.code_agent.run(user_input)
                    print_output("GENERATED CODE", result)
                else:
                    print("\n[Orchestrator] 🔀 Task classified as TOOL. Routing to Tool Agent...")
                    result = self.tool_agent.run(user_input)
                    print_output("AGENT ANSWER", result)

            except KeyboardInterrupt:
                print("\n\nInterrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n[Error] Orchestrator encountered an error: {e}")

# ── Main Entry Point ───────────────────────────────────────────────────────────

def main():
    """Main entry point — initialize orchestrator and run."""
    print_banner()
    print("\nWelcome! This engine automatically coordinates multiple AI agents.")
    print("Simply type your request, and the Orchestrator will route it to the right agent.\n")
    
    orchestrator = MasterOrchestrator()
    orchestrator.run()

if __name__ == "__main__":
    main()
