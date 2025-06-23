import os
from urllib.parse import urlencode

from dotenv import load_dotenv

load_dotenv()

def get_hubspot_auth_url():
    base_url = "https://app.hubspot.com/oauth/authorize"
    query = {
        "client_id": os.getenv("HUBSPOT_CLIENT_ID"),
        "redirect_uri": os.getenv("HUBSPOT_REDIRECT_URI"),
        "scope": "crm.objects.contacts.read crm.objects.contacts.write",
    }
    return f"{base_url}?{urlencode(query)}"
