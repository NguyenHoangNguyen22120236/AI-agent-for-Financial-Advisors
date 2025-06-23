from typing import List, Dict, Any
from app.services.email import send_email, propose_times_email
from app.services.calendar import create_event, find_free_times, get_upcoming_meetings
from app.services.hubspot import create_contact, add_note_to_hubspot, find_contact
from app.models.instruction import Instruction
from sqlalchemy.orm import Session

# Tool function registry
TOOLS = {
    "send_email": send_email,
    "create_event": create_event,
    "create_contact": create_contact,
    "add_note_to_hubspot": add_note_to_hubspot,
    "add_instruction": lambda condition, action, user_id, db=None: add_instruction(condition, action, user_id, db),
    "find_contact": find_contact,
    "find_free_times": find_free_times,
    "get_upcoming_meetings": get_upcoming_meetings,
    "propose_times_email": propose_times_email,
}

# Tool schemas for OpenAI API
tool_schemas = [
    {
        "name": "send_email",
        "description": "Send an email via Gmail",
        "parameters": {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Email address of the recipient"},
                "subject": {"type": "string", "description": "Subject of the email"},
                "body": {"type": "string", "description": "Body of the email"}
            },
            "required": ["to", "subject", "body"]
        }
    },
    {
        "name": "create_event",
        "description": "Create a Google Calendar event",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "integer"},
                "title": {"type": "string"},
                "start_time": {"type": "string", "description": "ISO 8601 start time"},
                "end_time": {"type": "string", "description": "ISO 8601 end time"},
                "attendees": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of email addresses"
                }
            },
            "required": ["user_id", "title", "start_time", "end_time", "attendees"]
        }
    },
    {
        "name": "create_contact",
        "description": "Create a contact in HubSpot",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "email": {"type": "string"},
                "phone": {"type": "string"},
                "company": {"type": "string"}
            },
            "required": ["email"]
        }
    },
    {
        "name": "add_note_to_hubspot",
        "description": "Attach a note to a HubSpot contact",
        "parameters": {
            "type": "object",
            "properties": {
                "contact_id": {"type": "string"},
                "content": {"type": "string"}
            },
            "required": ["contact_id", "content"]
        }
    },
    {
        "name": "add_instruction",
        "description": "Add a new ongoing automation rule",
        "parameters": {
            "type": "object",
            "properties": {
                "condition": {
                    "type": "string",
                    "description": "Trigger condition, e.g. 'email from unknown sender'"
                },
                "action": {
                    "type": "string",
                    "description": "Action to take, e.g. 'create contact and note in HubSpot'"
                }
            },
            "required": ["condition", "action"]
        }
    },
    {
        "name": "find_contact",
        "description": "Finds a contact by name or email in HubSpot/CRM.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "email": {"type": "string"}
            }
        }
    },
    {
        "name": "find_free_times",
        "description": "Finds available times for a meeting.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "integer"},
                "date_range": {"type": "string"}
            },
            "required": ["user_id"]
        }
    },
    {
        "name": "get_upcoming_meetings",
        "description": "Gets upcoming meetings for a contact.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "integer"},
                "contact_email": {"type": "string"}
            },
            "required": ["user_id", "contact_email"]
        }
    },
    {
        "name": "propose_times_email",
        "description": "Send an email with available meeting times.",
        "parameters": {
            "type": "object",
            "properties": {
                "to": {"type": "string"},
                "available_times": {"type": "array", "items": {"type": "string"}},
                "body": {"type": "string"}
            },
            "required": ["to", "available_times", "body"]
        }
    }
]

def add_instruction(condition: str, action: str, user_id: int, db: Session = None):
    instruction = Instruction(condition=condition, action=action, user_id=user_id, active=True)
    db.add(instruction)
    db.commit()
    return f"Instruction added: when '{condition}', do '{action}'."

def call_tool(tool_name: str, args: Dict[str, Any]) -> Any:
    try:
        tool_func = TOOLS[tool_name]
    except KeyError:
        raise ValueError(f"Unknown tool: {tool_name}")

    try:
        return tool_func(**args)
    except TypeError as e:
        raise ValueError(f"Invalid arguments for `{tool_name}`: {e}")
