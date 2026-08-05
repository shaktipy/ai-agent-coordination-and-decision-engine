"""
main.py — CLI Entry Point: Multi-Agent Code Review & Decision Engine
===================================================================
Usage:
    python main.py
"""

import sys
import io

# Fix Windows console UnicodeEncodeError
if isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout.reconfigure(encoding='utf-8')

from agents.orchestrator import MasterOrchestrator
from agents.aggregator import Aggregator


def print_banner():
    print("\n" + "=" * 65)
    print("   MULTI-AGENT AUTOMATED CODE REVIEW SYSTEM")
    print("   Infosys Springboard Virtual Internship 7.0")
    print("=" * 65)


def print_report(report):
    print("\n" + "=" * 65)
    print(f"  CODE HEALTH SCORE: {report.overall_score}/100")
    print(f"  EXECUTIVE SUMMARY")
    print("=" * 65)
    print(report.executive_summary)
    print("=" * 65)

    for agent_rep in report.reports:
        print(f"\n  Agent: {agent_rep.agent_name}")
        print(f"  Status: {agent_rep.status}")
        print(f"  Summary: {agent_rep.summary}")
        if agent_rep.findings:
            print(f"  Findings ({len(agent_rep.findings)}):")
            for f in agent_rep.findings:
                line_str = f"Line {f.line_number}" if f.line_number else "Snippet"
                print(f"    [{f.severity.upper()}] {f.title} ({line_str})")
                print(f"      > {f.description}")
                print(f"      Fix: {f.suggestion}")
        else:
            print("  No issues detected.")
    print("=" * 65 + "\n")


def main():
    print_banner()
    print("\nInitializing Master Orchestrator...")
    orchestrator = MasterOrchestrator()
    aggregator = Aggregator()
    print("System Ready. Paste your Python code below.")
    print("Type 'RUN' on a new line to analyse. Type 'quit' to exit.\n")

    while True:
        try:
            lines = []
            while True:
                line = input()
                if line.strip().lower() == "quit":
                    print("Goodbye!")
                    return
                if line.strip() == "RUN":
                    break
                lines.append(line)

            code = "\n".join(lines).strip()
            if not code:
                print("No code provided. Please enter code before typing RUN.")
                continue

            print("\nRouting request...")
            focus = orchestrator.route_request(code)
            print(f"Decision Engine focus: {focus}")

            reports = orchestrator.run_review(code, "snippet.py", focus)
            report = aggregator.aggregate(reports)
            print_report(report)

        except KeyboardInterrupt:
            print("\nShutting down.")
            break
        except Exception as e:
            print(f"\n[Error] {e}")


if __name__ == "__main__":
    main()
