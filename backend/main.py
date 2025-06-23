from fastapi import FastAPI
from app.api.auth import auth_router
from app.api.chat import chat_router
from app.api.tasks import tasks_router
from app.api.webhook import webhook_router
#from app.api.webhooks.hubspot import hubspot_router
#from app.api.webhooks.gmail import gmail_router
#from app.api.webhooks.calendar import calendar_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(tasks_router)
app.include_router(webhook_router)
#app.include_router(hubspot_router)
#app.include_router(gmail_router)
#app.include_router(calendar_router)



# http://localhost:8000/auth/hubspot/login
