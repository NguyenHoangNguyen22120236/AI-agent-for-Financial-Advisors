from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import base64
from email.mime.text import MIMEText
from sqlalchemy.orm import Session
from app.models.user import User
import os
from dotenv import load_dotenv
from app.models.email import Email
from app.services.embedding import generate_embedding
from google.oauth2.credentials import Credentials
from datetime import datetime

load_dotenv()


def send_email(to: str, subject: str, body: str, db: Session = None, user_id: int = None) -> str:
    # 1. Get user's token from database
    user = db.query(User).filter_by(id=user_id).first()
    if not user or not user.google_access_token:
        raise Exception("User not authenticated with Google")

    # 2. Create Google Credentials
    creds = Credentials(
        token=user.google_access_token,
        refresh_token=user.google_refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    )

    # 3. Build Gmail API client
    service = build("gmail", "v1", credentials=creds)

    # 4. Create email message
    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject
    raw_message = {"raw": base64.urlsafe_b64encode(message.as_bytes()).decode()}

    # 5. Send email
    try:
        response = service.users().messages().send(userId="me", body=raw_message).execute()
        return f"Email sent to {to} with ID: {response['id']}"
    except Exception as e:
        raise Exception(f"Failed to send email: {e}")


def propose_times_email(
    to: str,
    available_times: list,
    body: str = "",
    db: Session = None,
    user_id: int = None,
    subject: str = "Proposed meeting times",
    **kwargs
) -> str:
    """
    Send an email with a list of available meeting times.

    Args:
        to (str): Recipient's email address
        available_times (list): List of ISO 8601 datetime strings (or human-readable)
        body (str): Additional custom body text (optional)
        db (Session): SQLAlchemy session (for user auth)
        user_id (int): User sending the email

    Returns:
        str: Result message
    """
    # 1. Format the available times
    if not available_times:
        raise ValueError("No available times provided.")

    times_formatted = "\n".join(
        [f"- {t}" for t in available_times]
    )

    # 2. Compose the email body
    full_body = body.strip() + "\n\nHere are my available times:\n" + times_formatted
    full_body = full_body.strip()

    # 3. Optionally allow overriding subject via kwargs
    subject = kwargs.get("subject", subject)

    # 4. Reuse send_email to actually send
    return send_email(
        to=to,
        subject=subject,
        body=full_body,
        db=db,
        user_id=user_id
    )


def build_gmail_service(access_token: str):
    return build("gmail", "v1", credentials={"token": access_token})


def list_recent_messages(service, max_results=100):
    results = service.users().messages().list(
        userId="me",
        labelIds=["INBOX", "IMPORTANT"],
        maxResults=max_results,
        q="-category:promotions -category:social -in:spam -in:trash"
    ).execute()
    return results.get("messages", [])


def extract_message_body(service, msg_id):
    msg = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
    parts = msg["payload"].get("parts", [])
    for part in parts:
        if part.get("mimeType") == "text/plain":
            return part["body"].get("data", "")
    return ""


def sync_gmail_emails(user, db):
    creds = Credentials(token=user.google_access_token)
    service = build("gmail", "v1", credentials=creds)
    messages = list_recent_messages(service)

    for m in messages:
        # Check if this message_id already exists for this user
        existing = db.query(Email).filter_by(user_id=user.id, message_id=m["id"]).first()
        if existing:
            continue  # Skip if already in database
        
        # Get full metadata
        metadata = service.users().messages().get(userId="me", id=m["id"], format="metadata").execute()
        headers = metadata.get("payload", {}).get("headers", [])

        def extract_header(name):
            return next((h["value"] for h in headers if h["name"].lower() == name.lower()), None)

        sender = extract_header("From")
        recipient = extract_header("To")
        subject = extract_header("Subject")
        timestamp = int(metadata.get("internalDate", 0)) // 1000  # convert ms to seconds
        received_at = datetime.fromtimestamp(timestamp)

        content = extract_message_body(service, m["id"])
        if not content:
            continue

        embedding = generate_embedding(content)

        # Use your class method
        Email.create(
            db=db,
            user_id=user.id,
            sender=sender,
            recipient=recipient,
            subject=subject,
            body=content,
            message_id=m["id"],
            received_at=received_at,
            embedding=embedding
        )