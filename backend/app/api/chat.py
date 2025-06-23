from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from sqlalchemy.sql import text

from app.db.session import get_db
from app.services.embedding import generate_embedding
from app.models.task import Task
from app.models.instruction import Instruction
from app.models.chat_session import ChatSession, ChatMessage

from app.schemas.chat import ChatInput

from app.core.tool_agent import call_tool, tool_schemas
import json
import os
from dotenv import load_dotenv

load_dotenv()

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

chat_router = APIRouter(prefix="/chat", tags=["Chat"])

@chat_router.post("/")
def chat(input: ChatInput, db: Session = Depends(get_db)):
    print("Received chat input:", input)
    user_id = input.user_id
    user_message = input.message
    session_id = input.session_id

    # 1. Find or create chat session
    session = None
    if session_id:
        session = db.query(ChatSession).filter_by(id=session_id, user_id=user_id).first()
    if not session:
        session = ChatSession(user_id=user_id)
        db.add(session)
        db.commit()
        db.refresh(session)
        session_id = session.id

    # 2. Load chat history
    history = (
        db.query(ChatMessage)
        .filter_by(session_id=session_id)
        .order_by(ChatMessage.created_at)
        .all()
    )
    messages = []
    if not history:  # New session, inject system/context as first messages
        # Generate context from RAG sources
        query_embedding = generate_embedding(user_message)
        emails = db.execute(text("""
            SELECT subject, sender, recipient, body FROM emails
            WHERE user_id = :user_id
            ORDER BY embedding <#> (:embedding)::vector
            LIMIT 5
        """), {"user_id": user_id, "embedding": query_embedding}).fetchall()
        formatted_emails = [
            f"From: {row.sender}\nTo: {row.recipient}\nSubject: {row.subject}\n\n" +
            base64.urlsafe_b64decode(row.body).decode("utf-8", errors="ignore")
            for row in emails
        ]
        notes = db.execute(text("""
            SELECT content FROM contact_notes
            WHERE user_id = :user_id
            ORDER BY embedding <#> (:embedding)::vector
            LIMIT 5
        """), {"user_id": user_id, "embedding": query_embedding}).fetchall()
        instructions = db.query(Instruction).filter_by(user_id=user_id, active=True).all()
        context = "\n\n".join(
            formatted_emails +
            [row[0] for row in notes] +
            [f"Instruction: {i.condition} → {i.action}" for i in instructions]
        )
        messages = [
            {"role": "system", "content": "You are an AI assistant for financial advisors."},
            {"role": "system", "content": "You have access to recent emails and CRM notes. Use them to answer questions."},
            {"role": "system", "content": f"Context data:\n\n{context}"}
        ]

        print('context messages:', context)
    # Always append chat history (from DB)
    messages += [
        {"role": m.role, "content": m.content} if m.role != "function" else
        {"role": "function", "name": m.name, "content": m.content}
        for m in history
    ]

    # 3. Add current user message to history
    messages.append({"role": "user", "content": user_message})
    db.add(ChatMessage(session_id=session_id, role="user", content=user_message))
    db.commit()

    tool_call_results = []

    while True:
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
            args["user_id"] = user_id

            # -- CRITICAL LOGIC --
            # If this is a proposal to external contact (e.g., propose_times_email or send_email with available times)
            if tool_name in ["propose_times_email"]:
                result = call_tool(tool_name, args)
                # Save a "pending" scheduling task and stop the loop (do NOT create the event yet)
                pending_task = Task.create(
                    db=db,
                    user_id=user_id,
                    type="schedule_meeting",
                    status="waiting_for_response",
                    task_metadata={
                        "contact_email": args.get("to"),
                        "proposed_times": args.get("available_times"),
                        "session_id": session_id,
                        "context": messages,
                        "last_tool": tool_name
                    }
                )
                safe_args = dict(args)
                safe_args.pop("db", None)
                tool_call_results.append({"tool": tool_name, "args": safe_args, "result": result})

                # Log tool call to chat history
                msg_content = json.dumps(result)
                messages.append({"role": "function", "name": tool_name, "content": msg_content})
                db.add(ChatMessage(session_id=session_id, role="function", name=tool_name, content=msg_content))
                db.commit()

                return {
                    "response": (
                        f"I've proposed times to {args.get('to')}. I'll continue scheduling when they reply."
                    ),
                    "tool_calls": tool_call_results,
                    "session_id": session_id,
                    "pending_task_id": pending_task.id
                }

            # Otherwise, continue as before
            result = call_tool(tool_name, args)
            safe_args = dict(args)
            safe_args.pop("db", None)
            Task.create(
                db=db,
                user_id=user_id,
                type=tool_name,
                task_metadata={"args": safe_args, "result": result}
            )
            tool_call_results.append({"tool": tool_name, "args": safe_args, "result": result})

            # Add tool call to messages and persist to history
            msg_content = json.dumps(result)
            messages.append({"role": "function", "name": tool_name, "content": msg_content})
            db.add(ChatMessage(session_id=session_id, role="function", name=tool_name, content=msg_content))
            db.commit()
            continue

        else:
            db.add(ChatMessage(session_id=session_id, role="assistant", content=choice.message.content))
            db.commit()
            return {
                "response": choice.message.content,
                "tool_calls": tool_call_results,
                "session_id": session_id
            }


import base64
from email import message_from_bytes

def extract_body_from_gmail_message(msg_data):
    msg_str = base64.urlsafe_b64decode(msg_data['raw'])
    mime_msg = message_from_bytes(msg_str)
    
    if mime_msg.is_multipart():
        for part in mime_msg.walk():
            content_type = part.get_content_type()
            if content_type == 'text/plain':
                return part.get_payload(decode=True).decode('utf-8', errors='ignore')
    else:
        return mime_msg.get_payload(decode=True).decode('utf-8', errors='ignore')