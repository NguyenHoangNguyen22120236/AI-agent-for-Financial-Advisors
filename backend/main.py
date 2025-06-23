from fastapi import FastAPI
from app.api.auth import auth_router
from app.api.chat import chat_router
from app.api.tasks import tasks_router
from app.api.webhook import webhook_router

import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL")],  # Or ["*"] for all origins (not recommended for production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key="your-random-secret-key",  # Replace with your actual secret!
    max_age=86400,  # How many seconds the session should last (1 day)
)

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(tasks_router)
app.include_router(webhook_router)
