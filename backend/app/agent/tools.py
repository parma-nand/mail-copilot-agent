# backend/app/agent/tools.py
from langchain_core.tools import tool
from langgraph.types import Command
from app.services import gmail_service
from app.api.auth_routes import get_current_creds


@tool
async def search_emails(keyword: str = None, sender: str = None,
                         date_from: str = None, date_to: str = None,
                         read_status: str = "all"):
    """Search the user's inbox with the given filters."""
    creds = get_current_creds()
    results = await gmail_service.search(creds, keyword, sender, date_from, date_to, read_status)
    return Command(update={
        "search_results": results,
        "active_filters": {"keyword": keyword, "sender": sender,
                            "date_from": date_from, "date_to": date_to,
                            "read_status": read_status},
        "current_view": "inbox",
        "last_action": f"searched: {keyword or sender or 'recent'}"
    })


@tool
async def start_compose(to: str = "", subject: str = "", body: str = ""):
    """Open the compose view and pre-fill the email fields (to, subject, body)."""
    return Command(update={
        "current_view": "compose",
        "compose_draft": {"to": to, "subject": subject, "body": body, "cc": "", "in_reply_to": None},
        "last_action": f"started compose to {to}" if to else "started compose"
    })


@tool
async def send_email_tool(to: str, subject: str, body: str):
    """Send an email with the given recipient, subject, and body."""
    creds = get_current_creds()
    await gmail_service.send_email(creds, to, subject, body)
    return Command(update={
        "current_view": "inbox",
        "compose_draft": {"to": "", "subject": "", "body": "", "cc": "", "in_reply_to": None},
        "last_action": f"sent email to {to}"
    })


@tool
async def open_email(email_id: str):
    """Open a specific email by its id in the detail view."""
    return Command(update={
        "current_view": "detail",
        "open_email_id": email_id,
        "last_action": f"opened email {email_id}"
    })


@tool
async def apply_filters(date_from: str = None, date_to: str = None,
                         sender: str = None, keyword: str = None,
                         read_status: str = "all"):
    """Apply filters to the inbox view."""
    creds = get_current_creds()
    results = await gmail_service.search(creds, keyword, sender, date_from, date_to, read_status)
    return Command(update={
        "search_results": results,
        "active_filters": {"date_from": date_from, "date_to": date_to,
                            "sender": sender, "keyword": keyword,
                            "read_status": read_status},
        "current_view": "inbox",
        "last_action": "applied filters"
    })


@tool
async def prefill_reply(open_email_id: str):
    """Pre-fill a reply based on the currently open email. Requires the id of the currently open email."""
    creds = get_current_creds()
    email = await gmail_service.get_email(creds, open_email_id)
    headers = {h["name"]: h["value"] for h in email["payload"]["headers"]}
    original_subject = headers.get("Subject", "")
    original_from = headers.get("From", "")

    reply_subject = original_subject if original_subject.lower().startswith("re:") else f"Re: {original_subject}"

    return Command(update={
        "current_view": "compose",
        "compose_draft": {
            "to": original_from,
            "subject": reply_subject,
            "body": "",
            "cc": "",
            "in_reply_to": open_email_id
        },
        "last_action": f"prefilled reply to {original_from}"
    })