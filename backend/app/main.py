# backend/app/main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth_routes, mail_routes, webhook_routes
from app.core.websocket_manager import manager

app = FastAPI(title="Mail Copilot Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router, tags=["auth"])
app.include_router(mail_routes.router, tags=["mail"])
app.include_router(webhook_routes.router, tags=["webhooks"])

@app.get("/")
def health():
    return {"status": "ok"}

@app.websocket("/ws/mail")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)