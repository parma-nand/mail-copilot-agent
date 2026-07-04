# backend/app/api/auth_routes.py
import os
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"  # keep this too, avoids a separate scope-mismatch issue

from fastapi import APIRouter, HTTPException
from google_auth_oauthlib.flow import Flow
from app.core.config import settings

router = APIRouter()

_stored_creds = {"creds": None}
_stored_flow = {"flow": None}   # <-- add this

def get_flow():
    return Flow.from_client_config(
        {"web": {"client_id": settings.google_client_id,
                 "client_secret": settings.google_client_secret,
                 "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                 "token_uri": "https://oauth2.googleapis.com/token",
                 "redirect_uris": [settings.redirect_uri]}},
        scopes=settings.scopes,
        redirect_uri=settings.redirect_uri,
    )

@router.get("/auth/login")
def login():
    flow = get_flow()
    auth_url, state = flow.authorization_url(prompt="consent", access_type="offline")
    _stored_flow["flow"] = flow          # <-- save this exact instance
    return {"auth_url": auth_url}

@router.get("/auth/callback")
def callback(code: str):
    flow = _stored_flow["flow"]          # <-- reuse the same instance
    if flow is None:
        raise HTTPException(400, "No pending login — visit /auth/login first")
    flow.fetch_token(code=code)
    _stored_creds["creds"] = flow.credentials
    _stored_flow["flow"] = None          # clear after use
    return {"status": "connected"}

def get_current_creds():
    if _stored_creds["creds"] is None:
        raise HTTPException(status_code=401, detail="Not authenticated — visit /auth/login first")
    return _stored_creds["creds"]