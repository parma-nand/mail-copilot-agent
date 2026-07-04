# backend/app/api/mail_routes.py
from fastapi import APIRouter, Depends
from app.services import gmail_service
# creds dependency: pull from session/db for the logged-in user
from app.api.auth_routes import get_current_creds
from app.api.auth_routes import get_current_creds, _last_history_id

router = APIRouter()

@router.get("/inbox")
async def inbox(creds=Depends(get_current_creds)):
    return await gmail_service.list_inbox(creds)

@router.get("/sent")
async def sent(creds=Depends(get_current_creds)):
    return await gmail_service.list_sent(creds)

@router.get("/email/{email_id}")
async def email_detail(email_id: str, creds=Depends(get_current_creds)):
    return await gmail_service.get_email(creds, email_id)

@router.post("/send")
async def send(payload: dict, creds=Depends(get_current_creds)):
    return await gmail_service.send_email(creds, payload["to"], payload["subject"], payload["body"])

@router.post("/watch/start")
async def start_watch_route(creds=Depends(get_current_creds)):
    result = await gmail_service.start_watch(creds)
    _last_history_id["id"] = result["historyId"]
    return result