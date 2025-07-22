from pathlib import Path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError

# ── Config ────────────────────────────────────────────────────────────────────
SCOPES = ["https://www.googleapis.com/auth/calendar"]
ROOT_DIR = Path(__file__).resolve().parent.parent  # adjust if layout differs
CREDENTIALS_FILE = ROOT_DIR / "credentials.json"   # Google client‑secret JSON
TOKEN_FILE       = ROOT_DIR / "token.json"         # OAuth token (auto‑created)

# ── Helpers ───────────────────────────────────────────────────────────────────
def get_calendar_service():
    """
    Return an authenticated Google Calendar service instance.
    Re‑authenticates automatically if the saved token is missing, corrupt,
    or expired without a refresh token.
    """
    creds = None

    # 1️⃣  Try to load saved credentials -------------------------------------------------
    if TOKEN_FILE.exists():
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except (ValueError, UnicodeDecodeError):
            # Corrupt/invalid token – delete and start fresh
            TOKEN_FILE.unlink(missing_ok=True)
            creds = None

    # 2️⃣  Refresh or run OAuth flow ------------------------------------------------------
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError:
                creds = None  # fall through to OAuth flow below

        if not creds:
            # Interactive browser flow (runs once, then token is cached)
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Persist the new/updated token in UTF‑8 JSON
        TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")

    # 3️⃣  Build the Calendar service -----------------------------------------------------
    return build("calendar", "v3", credentials=creds)

# ── CRUD wrappers ─────────────────────────────────────────────────────────────
def list_events(max_results: int = 10):
    service = get_calendar_service()
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    return events_result.get("items", [])

def create_event(event: dict):
    service = get_calendar_service()
    created_event = (
        service.events()
        .insert(calendarId="primary", body=event)
        .execute()                               # fixed typo
    )
    return created_event

def update_event(event_id: str, event: dict):
    service = get_calendar_service()
    return (
        service.events()
        .update(calendarId="primary", eventId=event_id, body=event)
        .execute()
    )

def delete_event(event_id: str):
    service = get_calendar_service()
    service.events().delete(calendarId="primary", eventId=event_id).execute()
    return True
