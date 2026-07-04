# backend/app/api/auth_routes.py
from fastapi import APIRouter
from google_auth_oauthlib.flow import Flow
from app.core.config import settings

router = APIRouter()

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
    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")
    return {"auth_url": auth_url}

@router.get("/auth/callback")
def callback(code: str):
    flow = get_flow()
    flow.fetch_token(code=code)
    creds = flow.credentials
    # store creds.refresh_token + access_token in DB keyed to a session/user
    # for day 1, even an encrypted server-side file/session is fine
    return {"status": "connected"}