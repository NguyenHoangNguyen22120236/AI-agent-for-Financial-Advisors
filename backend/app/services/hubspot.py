from hubspot import HubSpot
from hubspot.crm.contacts import SimplePublicObjectInput as ContactInput, ApiException as ContactApiException
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.contact import Contact
from app.models.contact_note import ContactNote
from app.services.embedding import generate_embedding
import requests
from bs4 import BeautifulSoup


def create_contact(
    user_id: int,
    email: str,
    name: str = "",
    phone: str = "",
    company: str = "",
    db: Session = None
) -> str:
    user = db.query(User).filter_by(id=user_id).first()
    if not user or not user.hubspot_access_token:
        raise Exception("HubSpot account not connected.")

    client = HubSpot(access_token=user.hubspot_access_token)

    properties = {
        "email": email,
        "firstname": name,
        "phone": phone,
        "company": company
    }
    contact_input = ContactInput(properties=properties)

    try:
        result = client.crm.contacts.basic_api.create(simple_public_object_input=contact_input)
        return f"Contact {email} created in HubSpot with ID: {result.id}"
    except Exception as e:
        raise Exception(f"Failed to create contact: {str(e)}")


# Legacy note creation using Engagements API (because notes scope is unavailable)
def add_note_to_hubspot(user_id: int, contact_vid: int, content: str, db: Session = None) -> str:
    user = db.query(User).filter_by(id=user_id).first()
    if not user or not user.hubspot_access_token:
        raise Exception("HubSpot account not connected.")

    url = "https://api.hubapi.com/engagements/v1/engagements"
    headers = {
        "Authorization": f"Bearer {user.hubspot_access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "engagement": {"active": True, "type": "NOTE"},
        "associations": {"contactIds": [contact_vid]},
        "metadata": {"body": content}
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"Failed to add note: {response.text}")

    return f"Note added to contact {contact_vid}"


def sync_hubspot_data(user: User, db: Session):
    if not user.hubspot_access_token:
        return

    client = HubSpot(access_token=user.hubspot_access_token)

    # Sync contacts
    try:
        contacts_response = client.crm.contacts.basic_api.get_page(limit=100)
        for c in contacts_response.results:
            hs_id = c.id
            properties = c.properties
            email = properties.get("email")
            name = properties.get("firstname", "") + " " + properties.get("lastname", "")
            phone = properties.get("phone")
            company = properties.get("company")

            # Avoid duplicates
            existing = db.query(Contact).filter_by(user_id=user.id, hubspot_id=hs_id).first()
            if existing:
                continue

            Contact.create(
                db,
                user_id=user.id,
                hubspot_id=hs_id,
                email=email,
                name=name,
                phone=phone,
                company=company,
            )
    except ContactApiException as e:
        print("HubSpot contact sync failed:", e)

    # Sync notes via Engagements API (legacy)
    try:
        url = "https://api.hubapi.com/engagements/v1/engagements/paged"
        headers = {"Authorization": f"Bearer {user.hubspot_access_token}"}
        has_more = True
        offset = 0

        while has_more:
            params = {"limit": 100, "offset": offset}
            res = requests.get(url, headers=headers, params=params).json()

            for engagement in res.get("results", []):
                if engagement.get("engagement", {}).get("type") != "NOTE":
                    continue

                content = engagement.get("metadata", {}).get("body", "")
                cleaned_content = strip_html(content)
                                
                if not cleaned_content:
                    continue

                embedding = generate_embedding(cleaned_content)
                associations = engagement.get("associations", {}).get("contactIds", [])

                for contact_vid in associations:
                    contact = db.query(Contact).filter_by(user_id=user.id, hubspot_id=str(contact_vid)).first()
                    if contact:
                        existing_note = db.query(ContactNote).filter_by(user_id=user.id, contact_id=contact.id, content=content).first()
                        if not existing_note:
                            ContactNote.create(
                                db=db,
                                user_id=user.id,
                                contact_id=contact.id,
                                content=cleaned_content,
                                embedding=embedding
                            )

            has_more = res.get("hasMore", False)
            offset = res.get("offset", 0)

    except Exception as e:
        print("HubSpot notes sync failed:", e)


def strip_html(html: str) -> str:
    """Remove HTML tags and return plain text."""
    return BeautifulSoup(html, "html.parser").get_text().strip()


from hubspot.crm.contacts import ApiException as ContactApiException

def find_contact(
    user_id: int,
    email: str = "",
    name: str = "",
    db: Session = None
) -> dict:
    print(f"Finding contact for user {user_id} with email '{email}' and name '{name}'")
    """
    Find a contact in HubSpot by email or name.

    Args:
        user_id (int): Owner of the access token.
        email (str): Contact email to look up.
        name (str): Contact name (best effort).
        db (Session): SQLAlchemy session.

    Returns:
        dict: Contact info if found, else empty dict.
    """
    user = db.query(User).filter_by(id=user_id).first()
    if not user or not user.hubspot_access_token:
        raise Exception("HubSpot account not connected.")

    client = HubSpot(access_token=user.hubspot_access_token)

    # Try by email first (exact)
    if email:
        try:
            contact = client.crm.contacts.basic_api.get_by_id(email)
            return {
                "contact_id": contact.id,
                "email": contact.properties.get("email"),
                "name": contact.properties.get("firstname", "") + " " + contact.properties.get("lastname", ""),
                "phone": contact.properties.get("phone", ""),
                "company": contact.properties.get("company", "")
            }
        except ContactApiException as e:
            # Not found by email
            print(f"HubSpot contact not found by email '{email}': {e}")

    # Try by name (search API, best effort)
    if name:
        search_body = {
            "filterGroups": [{
                "filters": [
                    {"propertyName": "firstname", "operator": "CONTAINS_TOKEN", "value": name.split()[0]}
                ]
            }],
            "properties": ["email", "firstname", "lastname", "phone", "company"],
            "limit": 5
        }
        try:
            search = client.crm.contacts.search_api.do_search(public_object_search_request=search_body)
            print('search.results:', search.results)  # For debugging
            for contact in search.results:
                first = (contact.properties.get("firstname") or "").strip().lower()
                last = (contact.properties.get("lastname") or "").strip().lower()
                search_first = name.split()[0].strip().lower()
                search_last = name.split()[-1].strip().lower() if len(name.split()) > 1 else ""

                print(f"DEBUG - HubSpot contact: first='{first}', last='{last}'")  # For debugging

                if first != search_first:
                    continue
                if search_last and last != search_last:
                    continue
                # Found!
                return {
                    "contact_id": contact.id,
                    "email": contact.properties.get("email"),
                    "name": f"{contact.properties.get('firstname', '')} {contact.properties.get('lastname', '')}",
                    "phone": contact.properties.get("phone", ""),
                    "company": contact.properties.get("company", "")
                }
        except ContactApiException as e:
            print(f"HubSpot search failed: {e}")

    # Not found
    return {}
