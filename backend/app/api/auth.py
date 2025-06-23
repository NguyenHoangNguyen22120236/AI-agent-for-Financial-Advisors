from fastapi import APIRouter, Depends, Request
from app.services.google_oauth import get_auth_url, get_flow
from app.services.hubspot_oauth import get_hubspot_auth_url
from app.models.user import User
from app.db.session import get_db
from sqlalchemy.orm import Session
import os
import requests
from fastapi import BackgroundTasks
from app.services.email import sync_gmail_emails
from app.services.hubspot import sync_hubspot_data

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.get("/google/login")
def google_login():
    return {"auth_url": get_auth_url()}


@auth_router.get("/google/callback")
def google_callback(request: Request, db: Session = Depends(get_db), background_tasks: BackgroundTasks = None):
    code = request.query_params.get("code")
    flow = get_flow()
    flow.fetch_token(code=code)

    credentials = flow.credentials
    id_info = requests.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={"Authorization": f"Bearer {credentials.token}"}
    ).json()

    email = id_info["email"]
    user = User.get_or_create(db, email=email)
    user.update_google_tokens(db, credentials.token, credentials.refresh_token)
    
    # Run Gmail sync in background
    background_tasks.add_task(sync_gmail_emails, user, db)

    return {"message": f"Google account connected for {email}"}


@auth_router.get("/hubspot/login")
def hubspot_login():
    return {"auth_url": get_hubspot_auth_url()}


@auth_router.get("/hubspot/callback")
def hubspot_callback(request: Request, db: Session = Depends(get_db), background_tasks: BackgroundTasks = None):
    code = request.query_params.get("code")

    # 1. Exchange authorization code for access token
    res = requests.post("https://api.hubapi.com/oauth/v1/token", data={
        "grant_type": "authorization_code",
        "client_id": os.getenv("HUBSPOT_CLIENT_ID"),
        "client_secret": os.getenv("HUBSPOT_CLIENT_SECRET"),
        "redirect_uri": os.getenv("HUBSPOT_REDIRECT_URI"),
        "code": code
    }, headers={
        "Content-Type": "application/x-www-form-urlencoded"
    })

    if res.status_code != 200:
        raise Exception("Failed to get token from HubSpot")

    tokens = res.json()
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    # 2. Get user email using correct endpoint
    me = requests.get(
        f"https://api.hubapi.com/oauth/v1/access-tokens/{access_token}"
    ).json()

    email = me.get("user")
    if not email:
        raise Exception("HubSpot did not return a user email")

    # 3. Store user and tokens
    user = User.get_or_create(db, email=email)
    user.update_hubspot_tokens(db, access_token, refresh_token)

    # 4. Optionally, sync HubSpot data here if needed
    background_tasks.add_task(sync_hubspot_data, user, db)
    return {"message": f"HubSpot connected for {email}"}

