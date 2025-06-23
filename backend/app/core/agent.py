import json
from app.models.task import Task
from app.core.tool_agent import call_tool, tool_schemas
from app.models.instruction import Instruction
from app.models.email import Email
import os
from dotenv import load_dotenv

load_dotenv()

from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def event_matches_task(event, task):
    # For demo: match by email thread_id or subject, expand as needed
    meta = task.task_metadata or {}
    if meta.get("recipient") and event.get("sender") == meta.get("recipient"):
        return True
    return False


def continue_task(task, event, db):
    meta = task.task_metadata or {}
    reply_content = event.get("body", "")
    # 1. Build messages for LLM (prior proposal + reply)
    messages = [
        {"role": "system", "content": "You are an AI scheduling assistant. Only create an event after the recipient confirms a time."},
        {"role": "assistant", "content": meta.get("proposal_message", "")},  # The email you sent
        {"role": "user", "content": reply_content}
    ]
    # 2. Call LLM with tool_schemas enabled
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        functions=tool_schemas
    )
    choice = response.choices[0]
    if choice.finish_reason == "function_call":
        fn = choice.message.function_call
        tool_name = fn.name
        args = json.loads(fn.arguments)
        args["db"] = db
        args["user_id"] = task.user_id
        call_tool(tool_name, args)
        task.status = "completed"
        db.commit()
        return {"result": f"{tool_name} completed and task marked as complete."}
    else:
        # LLM says it can't proceed
        return {"result": "No action taken, waiting for more info."}


def instruction_matches_event(instr, event):
    # Naive, but works for MVP
    return instr.condition.lower() in str(event).lower()


def perform_instruction_action(instr, event, db):
    # Let the LLM pick the right tool to call
    # For demo, parse known actions
    action = instr.action.lower()
    if "create contact" in action:
        call_tool("create_contact", {
            "name": event.get("sender_name", ""),
            "email": event.get("sender")
        })
    if "send email" in action:
        call_tool("send_email", {
            "to": event.get("sender"),
            "subject": "Thank you for being a client",
            "body": "We're excited to work with you!"
        })
        

def handle_integration_event(event, db):
    user_id = event.get("user_id")

    # 1. Resume pending tasks
    for task in Task.get_pending_for_user(db, user_id):
        if event_matches_task(event, task):
            return continue_task(task, event, db)

    # 2. Ongoing instructions
    instructions = db.query(Instruction).filter_by(user_id=user_id, active=True).all()
    for instr in instructions:
        if instruction_matches_event(instr, event):
            perform_instruction_action(instr, event, db)
    return {"status": "processed"}
