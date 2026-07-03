"""
main.py — Entry Point: AI Agent Coordination & Decision Engine
=============================================================
Run this file to interact with the Code Generator Agent via CLI.

Usage:
    python main.py

Commands during interactive session:
    - Type any coding task to generate code
    - Type 'history' to see session summary
    - Type 'clear'   to reset memory and start fresh
    - Type 'quit'    to exit
"""

from agents.code_generator_agent import CodeGeneratorAgent


def print_banner():
    """Print a welcome banner."""
    print("\n" + "=" * 65)
    print("   AI AGENT COORDINATION & DECISION ENGINE")
    print("   Infosys Springboard Virtual Internship 7.0")
    print("   Agent: Code Generator (LangChain + Gemini)")
    print("=" * 65)
    print("\nCommands: 'history' | 'clear' | 'quit'")
    print("-" * 65)


def print_output(code: str):
    """Format and print the agent's generated code."""
    print("\n" + "─" * 65)
    print("  GENERATED CODE:")
    print("─" * 65)
    print(code)
    print("─" * 65 + "\n")


def main():
    """Main interactive loop for the Code Generator Agent."""
    print_banner()

    # Initialize the agent (loads model, memory, chain)
    agent = CodeGeneratorAgent()

    print("\nAgent initialized! Enter your coding task below.\n")

    while True:
        try:
            # Get user input
            task = input("You ➜  ").strip()

            # Handle special commands
            if not task:
                continue

            elif task.lower() == "quit":
                print("\nGoodbye! Agent shutting down.")
                break

            elif task.lower() == "history":
                print("\n" + agent.get_history_summary())

            elif task.lower() == "clear":
                agent.clear_memory()
                print("Session memory cleared. Fresh start!\n")

            else:
                # Run the agent — generate code for the task
                result = agent.run(task)
                print_output(result)

        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            break


if __name__ == "__main__":
    main()
