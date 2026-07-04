# backend/app/agent/tools.py
from langchain_core.tools import tool
from langgraph.types import Command
from app.services import gmail_service

@tool
async def search_emails(keyword: str = None, sender: str = None,
                         date_from: str = None, date_to: str = None,
                         read_status: str = "all"):
    """Search the user's inbox with the given filters."""
    results = await gmail_service.search(keyword, sender, date_from, date_to, read_status)
    return Command(update={
        "search_results": results,
        "active_filters": {"keyword": keyword, "sender": sender,
                            "date_from": date_from, "date_to": date_to,
                            "read_status": read_status},
        "current_view": "inbox",
        "last_action": f"searched: {keyword or sender or 'recent'}"
    })