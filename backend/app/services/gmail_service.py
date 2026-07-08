# backend/app/services/gmail_service.py
from googleapiclient.discovery import build
import base64
from email.mime.text import MIMEText

def get_client(creds):
    return build("gmail", "v1", credentials=creds)

async def list_inbox(creds, max_results=20):
    service = get_client(creds)
    res = service.users().messages().list(userId="me", labelIds=["INBOX"], maxResults=max_results).execute()
    return [_summarize(service, m["id"]) for m in res.get("messages", [])]

async def list_sent(creds, max_results=20):
    service = get_client(creds)
    res = service.users().messages().list(userId="me", labelIds=["SENT"], maxResults=max_results).execute()
    return [_summarize(service, m["id"]) for m in res.get("messages", [])]

async def get_email(creds, email_id):
    service = get_client(creds)
    return service.users().messages().get(userId="me", id=email_id, format="full").execute()

async def send_email(creds, to, subject, body):
    service = get_client(creds)
    msg = MIMEText(body)
    msg["to"] = to
    msg["subject"] = subject
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return service.users().messages().send(userId="me", body={"raw": raw}).execute()

def _summarize(service, msg_id):
    msg = service.users().messages().get(userId="me", id=msg_id, format="metadata",
                                          metadataHeaders=["From", "Subject", "Date"]).execute()
    headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
    return {
        "id": msg_id,
        "sender": headers.get("From", ""),
        "subject": headers.get("Subject", ""),
        "preview": msg.get("snippet", ""),
        "date": headers.get("Date", ""),
        "is_read": "UNREAD" not in msg.get("labelIds", []),
    }
async def start_watch(creds):
    service = get_client(creds)
    request_body = {
        "labelIds": ["INBOX"],
        "topicName": "projects/mail-copilot-agent/topics/gmail-notifications",
    }
    response = service.users().watch(userId="me", body=request_body).execute()
    return response
# backend/app/services/gmail_service.py
async def get_history_since(creds, start_history_id):
    service = get_client(creds)
    try:
        response = service.users().history().list(
            userId="me",
            startHistoryId=start_history_id,
            historyTypes=["messageAdded"],
        ).execute()
    except Exception as e:
        print(f"history.list error: {e}")
        return []

    new_message_ids = []
    for record in response.get("history", []):
        for added in record.get("messagesAdded", []):
            new_message_ids.append(added["message"]["id"])

    # Fetch summaries for each new message
    new_emails = [_summarize(service, msg_id) for msg_id in new_message_ids]
    return new_emails
# backend/app/services/gmail_service.py — add this function
async def search(creds, keyword=None, sender=None, date_from=None, date_to=None, read_status="all"):
    results = await list_inbox(creds, max_results=50)
    filtered = results
    if keyword:
        filtered = [e for e in filtered if keyword.lower() in e["subject"].lower() or keyword.lower() in e["preview"].lower()]
    if sender:
        filtered = [e for e in filtered if sender.lower() in e["sender"].lower()]
    if read_status == "unread":
        filtered = [e for e in filtered if not e["is_read"]]
    elif read_status == "read":
        filtered = [e for e in filtered if e["is_read"]]
    return filtered