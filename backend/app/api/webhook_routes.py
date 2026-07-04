# backend/app/api/webhook_routes.py
import base64
import json
from fastapi import APIRouter, Request
from app.services import gmail_service
from app.api.auth_routes import get_current_creds, _last_history_id
from app.core.websocket_manager import manager

router = APIRouter()

@router.post("/webhooks/gmail")
async def gmail_webhook(request: Request):
    body = await request.json()
    message = body.get("message", {})
    data_encoded = message.get("data")

    if not data_encoded:
        return {"status": "no data"}

    decoded = base64.b64decode(data_encoded).decode("utf-8")
    payload = json.loads(decoded)
    new_history_id = payload.get("historyId")

    print("Gmail notification received:", payload)

    try:
        creds = get_current_creds()
    except Exception:
        print("No active credentials — skipping history fetch")
        return {"status": "ok"}

    last_id = _last_history_id["id"]
    if last_id and new_history_id:
        new_emails = await gmail_service.get_history_since(creds, last_id)
        if new_emails:
            print(f"Broadcasting {len(new_emails)} new email(s)")
            await manager.broadcast({"type": "new_emails", "emails": new_emails})

    _last_history_id["id"] = new_history_id
    return {"status": "ok"}