"""
main.py — Entry Point: Development of Enterprise Workflow Platform with Decision Automation System
===================================================================
Usage:
    python main.py
"""

import sys
import io
import uvicorn

# Fix Windows console UnicodeEncodeError
if isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout.reconfigure(encoding='utf-8')

def print_banner():
    print("\n" + "=" * 65)
    print("   DEVELOPMENT OF ENTERPRISE WORKFLOW PLATFORM WITH DECISION AUTOMATION SYSTEM")
    print("   Infosys Springboard Virtual Internship 7.0")
    print("=" * 65)
    print("\nStarting the Web Dashboard and API Server...")
    print("Dashboard will be available at: http://localhost:8000")
    print("=" * 65 + "\n")

def main():
    print_banner()
    # Run the FastAPI server using uvicorn
    uvicorn.run("api.server:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
