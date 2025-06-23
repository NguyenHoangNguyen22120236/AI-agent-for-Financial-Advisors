from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime
from sqlalchemy.orm import Session
from pgvector.sqlalchemy import Vector

class Email(Base):
    __tablename__ = 'emails'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    sender = Column(String)
    recipient = Column(String)
    subject = Column(String)
    body = Column(Text)
    message_id = Column(String, unique=True)
    received_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    embedding = Column(Vector(1536))

    user = relationship("User", back_populates="emails")
    
    
    @classmethod
    def create(cls, db: Session, user_id: int, sender: str, recipient: str, subject: str, body: str,
               message_id: str, received_at: datetime, embedding: Vector) -> "Email":
        email = cls(
            user_id=user_id,
            sender=sender,
            recipient=recipient,
            subject=subject,
            body=body,
            message_id=message_id,
            received_at=received_at,
            embedding=embedding  # Assuming embedding will be set later
        )
        db.add(email)
        db.commit()
        db.refresh(email)
        return email

    @classmethod
    def get_by_message_id(cls, db: Session, message_id: str) -> "Email | None":
        return db.query(cls).filter(cls.message_id == message_id).first()

    @classmethod
    def get_recent_emails(cls, db: Session, user_id: int, limit: int = 10) -> list["Email"]:
        return (
            db.query(cls)
            .filter(cls.user_id == user_id)
            .order_by(cls.received_at.desc())
            .limit(limit)
            .all()
        )

    @classmethod
    def search_by_keyword(cls, db: Session, user_id: int, keyword: str, limit: int = 10) -> list["Email"]:
        return (
            db.query(cls)
            .filter(cls.user_id == user_id, cls.body.ilike(f"%{keyword}%"))
            .order_by(cls.received_at.desc())
            .limit(limit)
            .all()
        )