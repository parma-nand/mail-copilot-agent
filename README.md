# mail-copilot-agent
AI-Powered Mail Web Application
# Mail Copilot Agent

An AI-powered webmail client where an assistant controls the UI directly — composing emails, searching/filtering the inbox, navigating to specific emails, and pre-filling context-aware replies — built for the Processity.ai hiring task.

## Demo

[Add screenshots or a short screen recording here showing the assistant controlling the UI]

## Tech Stack

- **Backend:** FastAPI, LangGraph, CopilotKit, Google Gmail API, Google Cloud Pub/Sub
- **Frontend:** Next.js (App Router), TypeScript, Tailwind CSS, CopilotKit React
- **Real-time sync:** Gmail `watch()` + Pub/Sub push notifications + WebSocket broadcast
- **Auth:** Google OAuth 2.0 (with PKCE)

## Architecture Overview
User → Next.js frontend ←──WebSocket──→ FastAPI backend ←──REST──→ Gmail API
↑
Pub/Sub webhook (real-time push)
↑
Gmail watch() notifications

- **Mail service layer** (`gmail_service.py`) wraps all Gmail API calls — list, get, send, search, watch, history — kept separate from route handlers so it can be tested or swapped independently.
- **Auth layer** (`auth_routes.py`) handles the OAuth 2.0 + PKCE flow. Credentials are currently stored **in-memory, single-user** for this MVP — see Trade-offs below.
- **Real-time sync** uses Gmail's `users.watch()` to register a Cloud Pub/Sub topic, which pushes notifications to a FastAPI webhook whenever the mailbox changes. The webhook calls `history.list()` to fetch what actually changed, then broadcasts new emails to connected frontend clients over a WebSocket — so the inbox updates without any polling or manual refresh.
- **AI assistant** uses LangGraph + CopilotKit's CoAgents pattern: a single shared `AgentState` (current view, open email, compose draft, filters, search results) is mutated directly by LangGraph tool calls and streamed live to the React frontend, so the assistant's actions are always reflected as real UI state changes — not just chat responses describing what it did.

## Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 20+ (LTS)
- A Google Cloud account
- [ngrok](https://ngrok.com/download) (for local real-time sync testing only)

### 1. Clone the repo
```bash
git clone <repo-url>
cd mail-copilot-agent
```

### 2. Set up Google Cloud (required before backend will run)

1. Create a project in [Google Cloud Console](https://console.cloud.google.com)
2. Enable the **Gmail API** (APIs & Services → Library → search "Gmail API" → Enable)
3. Enable the **Cloud Pub/Sub API** (same steps, search "Pub/Sub")
4. Configure the **OAuth consent screen**:
   - User Type: External
   - Add your test Gmail account under **Test users** (required — the app runs in Testing mode, so only listed accounts can log in)
5. Create **OAuth credentials** (APIs & Services → Credentials → Create Credentials → OAuth Client ID):
   - Application type: Web application
   - Authorized redirect URI: `http://localhost:8000/auth/callback`
   - Copy the generated **Client ID** and **Client Secret**
6. Create a **Pub/Sub topic** named `gmail-notifications`
7. Grant Gmail's service account publish rights on that topic:
   - Topic → Permissions → Add Principal → `gmail-api-push@system.gserviceaccount.com` → role **Pub/Sub Publisher**
8. Create a **push subscription** on that topic (you'll set its endpoint URL after starting ngrok — see step 5)

### 3. Backend setup

```bash
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

Edit `backend/.env`:
```env
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
REDIRECT_URI=http://localhost:8000/auth/callback
```

Run the backend:
```bash
uvicorn app.main:app --reload
```
Backend runs at `http://127.0.0.1:8000`. Swagger docs: `http://127.0.0.1:8000/docs`

### 4. Frontend setup

```bash
cd frontend
npm install
cp .env.example .env
```

Edit `frontend/.env`:
```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

Run the frontend:
```bash
npm run dev
```
Frontend runs at `http://localhost:3000`

### 5. Enable real-time sync locally (optional, for full functionality)

Pub/Sub needs a public HTTPS URL to push to, so local testing requires a tunnel:

```bash
ngrok http 8000
```

Copy the `https://....ngrok-free.app` (or `.dev`) forwarding URL, then:
1. Go to your Pub/Sub subscription in Google Cloud Console → Edit
2. Set Delivery type: **Push**
3. Endpoint URL: `https://<your-ngrok-url>/webhooks/gmail`
4. Save

**Note:** free ngrok URLs change every time you restart the tunnel — you'll need to update the subscription's endpoint URL each time, or use a paid ngrok plan with a reserved domain.

### 6. First-time login and activating sync

1. Visit `http://127.0.0.1:8000/auth/login`, copy the `auth_url` from the response, open it in a browser, and complete Google sign-in with your test account.
2. Call `POST http://127.0.0.1:8000/watch/start` (via Postman or curl) to activate real-time notifications.
3. Open `http://localhost:3000` — your inbox should load, and new emails will now appear live without refreshing.

## What's Implemented

- ✅ Inbox, Sent, Compose, and Email Detail views connected to real Gmail data
- ✅ Real-time inbox sync via Gmail `watch()` + Pub/Sub + WebSocket (no polling)
- ✅ OAuth 2.0 login flow with PKCE
- ✅ AI assistant that controls the UI directly (compose, search, navigate, context-aware reply) via LangGraph + CopilotKit shared state
- ✅ Basic filters (date, sender, keyword, read/unread) via UI and assistant commands

## Trade-offs and Known Limitations

These were deliberate simplifications made given the 5-day timeline — noted here rather than hidden:

- **In-memory, single-user credential storage.** OAuth tokens and the last-seen Gmail `historyId` are held in server memory (not a database), so they're lost on server restart and only support one logged-in user at a time. A production version would store encrypted refresh tokens per-user in a database, keyed to a session/JWT.
- **Gmail `watch()` expires after 7 days** and needs periodic renewal (e.g., a scheduled job calling `/watch/start` again). Not implemented — would add a cron/background task in production.
- **ngrok dependency for local real-time sync.** Pub/Sub requires a public HTTPS endpoint; local development relies on ngrok tunneling. A deployed version would register a stable production URL directly.
- **WebSocket broadcast is single-process, in-memory.** The connection manager only tracks clients connected to the current server process — won't scale horizontally without a shared pub/sub layer (e.g., Redis) between instances.
- **MIME parsing for email bodies** handles the common case (direct body or a single `text/plain` part) but doesn't recursively walk deeply nested multipart MIME structures — some complex HTML-heavy emails may not render their full body correctly.

## What I'd Improve With More Time

- Persistent, encrypted, multi-user credential storage (database-backed sessions instead of in-memory)
- Automatic Gmail watch renewal before the 7-day expiration
- Recursive MIME parsing for fully robust email body rendering (including attachments)
- Deployed backend with a stable public URL, removing the ngrok dependency
- Redis-backed WebSocket broadcast for horizontal scaling
- More comprehensive filter support (labels, attachments, thread-aware search)
- Unit/integration tests for the Gmail service layer and LangGraph tools

## Project Structure