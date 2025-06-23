from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.agent import handle_integration_event
from app.db.session import get_db

webhook_router = APIRouter(prefix="/tasks", tags=["Webhooks"])

@webhook_router.post("/webhook")
def integration_event(payload: dict, db: Session = Depends(get_db)):
    return handle_integration_event(payload, db)