"""
api/server.py — FastAPI Backend Server with Memory and LangGraph integrations
"""

import os
import tempfile
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from models.schemas import FinalReviewReport
from agents.orchestrator import MasterOrchestrator
from agents.aggregator import Aggregator
from agents.report_renderer import render_report_to_pdf
from agents.utils.memory_manager import MemoryManager

app = FastAPI(title="Development of Enterprise Workflow Platform with Decision Automation System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_LAST_REPORT: Optional[FinalReviewReport] = None
orchestrator = MasterOrchestrator()
aggregator = Aggregator()
memory_manager = MemoryManager()


class ReviewRequest(BaseModel):
    code: str
    filename: Optional[str] = ""
    query: Optional[str] = ""
    session_id: Optional[str] = "default_session"


@app.post("/api/review", response_model=FinalReviewReport)
async def review_code(req: ReviewRequest):
    global _LAST_REPORT
    try:
        session_id = req.session_id or "default_session"
        query_str = req.query or ""

        # Check if the user is instructing the agent to remember something
        remember_note = MemoryManager.extract_remember_note(query_str)
        if remember_note:
            memory_manager.add_learning(remember_note)

        # Retrieve memory contexts
        short_term_list = memory_manager.get_short_term(session_id)
        short_term_context = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in short_term_list])
        long_term_context = memory_manager.get_long_term_summary()

        # Run review via LangGraph workflow
        reports = orchestrator.run_review(
            code=req.code,
            filename=req.filename or "snippet.py",
            query=query_str,
            short_term_context=short_term_context,
            long_term_context=long_term_context
        )
        final_report = aggregator.aggregate(reports)
        _LAST_REPORT = final_report

        # Update memories
        memory_manager.record_review_to_long_term(final_report)
        memory_manager.add_to_short_term(session_id, "user", query_str or "Analyze code")
        memory_manager.add_to_short_term(session_id, "assistant", final_report.executive_summary)

        return final_report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/review/upload", response_model=FinalReviewReport)
async def review_upload(
    file: UploadFile = File(...),
    query: Optional[str] = Form(""),
    session_id: Optional[str] = Form("default_session")
):
    global _LAST_REPORT
    try:
        content = await file.read()
        code_str = content.decode("utf-8", errors="replace")
        query_str = query or ""

        remember_note = MemoryManager.extract_remember_note(query_str)
        if remember_note:
            memory_manager.add_learning(remember_note)

        short_term_list = memory_manager.get_short_term(session_id)
        short_term_context = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in short_term_list])
        long_term_context = memory_manager.get_long_term_summary()

        reports = orchestrator.run_review(
            code=code_str,
            filename=file.filename,
            query=query_str,
            short_term_context=short_term_context,
            long_term_context=long_term_context
        )
        final_report = aggregator.aggregate(reports)
        _LAST_REPORT = final_report

        memory_manager.record_review_to_long_term(final_report)
        memory_manager.add_to_short_term(session_id, "user", query_str or f"Uploaded {file.filename}")
        memory_manager.add_to_short_term(session_id, "assistant", final_report.executive_summary)

        return final_report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/review/pdf")
async def download_pdf():
    global _LAST_REPORT
    if _LAST_REPORT is None:
        raise HTTPException(status_code=400, detail="No report generated yet.")
    temp_dir = tempfile.gettempdir()
    pdf_path = os.path.join(temp_dir, f"report_{_LAST_REPORT.report_id}.pdf")
    try:
        render_report_to_pdf(_LAST_REPORT, pdf_path)
        return FileResponse(pdf_path, media_type="application/pdf", filename="code_review_report.pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {e}")


@app.get("/api/health")
async def health_check():
    """Simple health-check ping endpoint."""
    return {"status": "ok", "service": "Enterprise Workflow Platform"}


@app.get("/api/history")
async def get_history():
    """Return long-term memory summary for the dashboard history tab."""
    try:
        data = memory_manager.get_full_long_term()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not read history: {e}")


# Serve the web dashboard
web_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web")
if os.path.exists(web_path):
    app.mount("/", StaticFiles(directory=web_path, html=True), name="web")

