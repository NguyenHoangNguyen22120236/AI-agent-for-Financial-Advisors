from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from .base import Base
from sqlalchemy.orm import Session
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    google_access_token = Column(Text)
    google_refresh_token = Column(Text)
    hubspot_access_token = Column(Text)
    hubspot_refresh_token = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    emails = relationship("Email", back_populates="user")
    tasks = relationship("Task", back_populates="user")
    contacts = relationship("Contact", back_populates="user")
    contact_notes = relationship("ContactNote", back_populates="user")
    instructions = relationship("Instruction", back_populates="user")
    calendar_events = relationship("CalendarEvent", back_populates="user")
    
    
    @classmethod
    def get_by_email(cls, db: Session, email: str) -> "User | None":
        return db.query(cls).filter(cls.email == email).first()

    @classmethod
    def create(cls, db: Session, email: str) -> "User":
        user = cls(email=email)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @classmethod
    def get_or_create(cls, db: Session, email: str) -> "User":
        user = cls.get_by_email(db, email)
        if user is None:
            user = cls.create(db, email)
        return user

    def update_google_tokens(self, db: Session, access_token: str, refresh_token: str):
        self.google_access_token = access_token
        self.google_refresh_token = refresh_token
        db.commit()
        db.refresh(self)

    def update_hubspot_tokens(self, db: Session, access_token: str, refresh_token: str):
        self.hubspot_access_token = access_token
        self.hubspot_refresh_token = refresh_token
        db.commit()
        db.refresh(self)