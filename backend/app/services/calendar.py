from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from sqlalchemy.orm import Session
from app.models.user import User
from typing import List
from datetime import datetime, timedelta
import pytz

import os
from dotenv import load_dotenv

load_dotenv()


def create_event(
    user_id: int,
    title: str,
    start_time: str,
    end_time: str,
    attendees: List[str],
    db: Session = None
) -> str:
    # Step 1: Retrieve user's tokens
    user = db.query(User).filter_by(id=user_id).first()
    if not user or not user.google_access_token:
        raise Exception("Google account not connected.")

    # Step 2: Set up Google credentials
    creds = Credentials(
        token=user.google_access_token,
        refresh_token=user.google_refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    )

    # Step 3: Build Google Calendar client
    service = build("calendar", "v3", credentials=creds)

    # Step 4: Build event body
    event = {
        "summary": title,
        "start": {"dateTime": start_time, "timeZone": "UTC"},
        "end": {"dateTime": end_time, "timeZone": "UTC"},
        "attendees": [{"email": email} for email in attendees],
    }

    try:
        created_event = service.events().insert(calendarId="primary", body=event, sendUpdates="all").execute()
        return f"Event '{title}' created with ID: {created_event['id']}"
    except Exception as e:
        raise Exception(f"Failed to create event: {e}")


def find_free_times(
    user_id: int,
    date_range: str = "today",
    db: Session = None,
    **kwargs
) -> list:
    """
    Returns available timeslots for the user's calendar.

    Args:
        user_id (int): User's ID.
        date_range (str): e.g., "today", "next week", or explicit date "2024-06-25".
        db (Session): SQLAlchemy DB session.

    Returns:
        List of ISO8601-formatted datetime strings representing free slots.
    """
    user = db.query(User).filter_by(id=user_id).first()
    if not user or not user.google_access_token:
        raise Exception("Google account not connected.")

    creds = Credentials(
        token=user.google_access_token,
        refresh_token=user.google_refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    )
    service = build("calendar", "v3", credentials=creds)

    # Date range calculation
    tz = pytz.UTC
    now = datetime.now(tz)
    if date_range == "today":
        start = now.replace(hour=8, minute=0, second=0, microsecond=0)
        end = now.replace(hour=18, minute=0, second=0, microsecond=0)
    elif date_range == "next week":
        start = (now + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)
        end = (now + timedelta(days=7)).replace(hour=18, minute=0, second=0, microsecond=0)
    else:  # Try to parse as date
        try:
            start = datetime.fromisoformat(date_range).replace(hour=8, minute=0, second=0, microsecond=0, tzinfo=tz)
            end = start.replace(hour=18)
        except Exception:
            raise ValueError("Invalid date_range format.")

    # Get busy slots from Google Calendar
    body = {
        "timeMin": start.isoformat(),
        "timeMax": end.isoformat(),
        "timeZone": "UTC",
        "items": [{"id": "primary"}],
    }
    freebusy = service.freebusy().query(body=body).execute()
    busy_times = freebusy['calendars']['primary']['busy']

    # Calculate free slots (simple version: 1-hour slots, not in busy)
    slots = []
    slot = start
    while slot < end:
        slot_end = slot + timedelta(hours=1)
        overlap = any(
            slot < datetime.fromisoformat(busy['end']) and slot_end > datetime.fromisoformat(busy['start'])
            for busy in busy_times
        )
        if not overlap:
            slots.append(slot.isoformat())
        slot = slot_end
    return slots


def get_upcoming_meetings(
    user_id: int,
    contact_email: str,
    db: Session = None,
    **kwargs
) -> list:
    """
    Get upcoming meetings with a contact from Google Calendar.

    Args:
        user_id (int): User's ID.
        contact_email (str): The contact's email.
        db (Session): SQLAlchemy DB session.

    Returns:
        List of dicts with meeting info.
    """
    user = db.query(User).filter_by(id=user_id).first()
    if not user or not user.google_access_token:
        raise Exception("Google account not connected.")

    creds = Credentials(
        token=user.google_access_token,
        refresh_token=user.google_refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    )
    service = build("calendar", "v3", credentials=creds)

    now = datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(
        calendarId='primary', timeMin=now, maxResults=20, singleEvents=True, orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    meetings = []
    for event in events:
        attendees = [a['email'] for a in event.get('attendees', []) if 'email' in a]
        if contact_email in attendees:
            meetings.append({
                "title": event.get("summary"),
                "start_time": event["start"].get("dateTime"),
                "end_time": event["end"].get("dateTime"),
                "id": event.get("id"),
            })
    return meetings
