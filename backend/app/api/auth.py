from fastapi import APIRouter, Depends, Request, BackgroundTasks
from app.services.google_oauth import get_auth_url, get_flow
from app.services.hubspot_oauth import get_hubspot_auth_url
from app.models.user import User
from app.db.session import get_db
from sqlalchemy.orm import Session
import os
import requests
from app.services.email import sync_gmail_emails
from app.services.hubspot import sync_hubspot_data
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from app.utils.jwt import create_access_token, decode_access_token
from fastapi.responses import RedirectResponse


from dotenv import load_dotenv

load_dotenv()

auth_router = APIRouter(prefix="/auth", tags=["Auth"])

from fastapi import Header, HTTPException, Depends

def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth header")
    
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return payload["sub"]  # return email


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

    # Create JWT
    token = create_access_token({"sub": email})
    background_tasks.add_task(sync_gmail_emails, user, db)

    # Redirect to frontend with token in query param
    frontend_url = os.getenv("FRONTEND_URL")
    return RedirectResponse(url=f"{frontend_url}/auth/callback?token={token}")


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
    frontend_url = os.getenv("FRONTEND_URL")
    return RedirectResponse(url=f"{frontend_url}")


@auth_router.get("/me")
def get_me(user_email: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        return {"user": None}

    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "hubspot_connected": user.hubspot_access_token is not None,
        }
    }


@auth_router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return {"detail": "Logged out"}