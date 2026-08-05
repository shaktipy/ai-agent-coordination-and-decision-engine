"""
api/server.py — FastAPI Backend Server
"""

import os
import tempfile
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Literal, Optional

from models.schemas import FinalReviewReport
from agents.orchestrator import MasterOrchestrator
from agents.aggregator import Aggregator
from agents.report_renderer import render_report_to_pdf

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


class ReviewRequest(BaseModel):
    code: str
    filename: Optional[str] = ""
    focus: Literal["SECURITY", "PERFORMANCE", "QUALITY", "DOCS", "FULL"] = "FULL"


@app.post("/api/review", response_model=FinalReviewReport)
async def review_code(req: ReviewRequest):
    global _LAST_REPORT
    try:
        reports = orchestrator.run_review(req.code, req.filename or "snippet.py", req.focus)
        final_report = aggregator.aggregate(reports)
        _LAST_REPORT = final_report
        return final_report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/review/upload", response_model=FinalReviewReport)
async def review_upload(
    file: UploadFile = File(...),
    focus: Literal["SECURITY", "PERFORMANCE", "QUALITY", "DOCS", "FULL"] = Form("FULL")
):
    global _LAST_REPORT
    try:
        content = await file.read()
        code_str = content.decode("utf-8", errors="replace")
        reports = orchestrator.run_review(code_str, file.filename, focus)
        final_report = aggregator.aggregate(reports)
        _LAST_REPORT = final_report
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


# Serve the web dashboard
web_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web")
if os.path.exists(web_path):
    app.mount("/", StaticFiles(directory=web_path, html=True), name="web")
