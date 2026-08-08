"""
agents/utils/memory_manager.py — Memory Manager for Short-Term and Long-Term Memory
"""

import os
import json
from typing import Dict, List, Any

MEMORY_FILE = "long_term_memory.json"

class MemoryManager:
    def __init__(self, storage_path: str = MEMORY_FILE):
        self.storage_path = storage_path
        # Short-term memory: Dict mapping session_id -> list of chat messages/turns
        self.short_term_db: Dict[str, List[Dict[str, Any]]] = {}
        self._init_long_term()

    def _init_long_term(self):
        if not os.path.exists(self.storage_path):
            initial_data = {
                "user_preferences": {},
                "past_reviews_count": 0,
                "recurring_issues": [],
                "learnings": []
            }
            self._write_long_term(initial_data)

    def _read_long_term(self) -> Dict[str, Any]:
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {
                "user_preferences": {},
                "past_reviews_count": 0,
                "recurring_issues": [],
                "learnings": []
            }

    def _write_long_term(self, data: Dict[str, Any]):
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error writing long term memory: {e}")

    def get_long_term_summary(self) -> str:
        data = self._read_long_term()
        summary_lines = []
        if data.get("user_preferences"):
            summary_lines.append(f"User Preferences: {json.dumps(data['user_preferences'])}")
        if data.get("learnings"):
            summary_lines.append("Key Learnings/Past Notes:")
            for item in data["learnings"]:
                summary_lines.append(f"- {item}")
        if data.get("recurring_issues"):
            summary_lines.append("Recurring Issues Detected previously:")
            for issue in data["recurring_issues"]:
                summary_lines.append(f"- {issue}")
        summary_lines.append(f"Total reviews run: {data.get('past_reviews_count', 0)}")
        return "\n".join(summary_lines)

    def record_review_to_long_term(self, final_report: Any):
        data = self._read_long_term()
        data["past_reviews_count"] = data.get("past_reviews_count", 0) + 1
        
        # Extract critical/high findings from ALL agents to long-term memory
        findings_summary = []
        for rep in getattr(final_report, "reports", []):
            agent_label = getattr(rep, "agent_name", "Unknown Agent")
            for finding in getattr(rep, "findings", []):
                if getattr(finding, "severity", "").lower() in ("critical", "high"):
                    findings_summary.append(f"{agent_label}: {finding.title}")

        if findings_summary:
            # Keep unique list of recurring issues while preserving order
            current_issues = data.get("recurring_issues", [])
            for finding in findings_summary:
                if finding not in current_issues:
                    current_issues.append(finding)
            # Limit to last 20
            data["recurring_issues"] = current_issues[-20:]

        self._write_long_term(data)

    def add_learning(self, note: str):
        data = self._read_long_term()
        learnings = data.get("learnings", [])
        if note not in learnings:
            learnings.append(note)
        # Limit to last 20
        data["learnings"] = learnings[-20:]
        self._write_long_term(data)

    @staticmethod
    def extract_remember_note(query: str) -> str | None:
        """Detect 'remember' anywhere in the query and extract the note.
        
        Supports patterns like:
          - "remember always use type hints"
          - "please remember to check for SQL injection"
          - "can you remember this: never use eval"
        """
        q = query.strip().lower()
        if not q:
            return None

        # "remember ..." at the start
        if q.startswith("remember "):
            return query.strip()[len("remember "):].strip() or None

        # "... remember ..." anywhere else — extract everything after "remember"
        import re
        match = re.search(r'\bremember\s+(.+)', query.strip(), re.IGNORECASE | re.DOTALL)
        if match:
            note = match.group(1).strip()
            return note if note else None

        return None

    # Short-Term Memory Methods
    def get_short_term(self, session_id: str) -> List[Dict[str, Any]]:
        return self.short_term_db.setdefault(session_id, [])

    def add_to_short_term(self, session_id: str, role: str, content: str):
        history = self.get_short_term(session_id)
        history.append({"role": role, "content": content})
        # Keep only last 10 messages for context efficiency
        self.short_term_db[session_id] = history[-10:]

    def get_full_long_term(self) -> Dict[str, Any]:
        """Return the entire long-term memory dict for the history API."""
        return self._read_long_term()

