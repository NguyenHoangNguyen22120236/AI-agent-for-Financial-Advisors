from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base
from sqlalchemy.orm import Session
from pgvector.sqlalchemy import Vector

class ContactNote(Base):
    __tablename__ = 'contact_notes'

    id = Column(Integer, primary_key=True)
    contact_id = Column(Integer, ForeignKey('contacts.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    embedding = Column(Vector(1536))

    contact = relationship("Contact", back_populates="contact_notes")
    user = relationship("User")
    
    
    @classmethod
    def create(cls, db: Session, user_id: int, contact_id: int, content: str, embedding: list[float]) -> "ContactNote":
        note = cls(user_id=user_id, contact_id=contact_id, content=content, embedding=embedding)
        db.add(note)
        db.commit()
        db.refresh(note)
        return note


    @classmethod
    def get_by_contact(cls, db: Session, user_id: int, contact_id: int) -> list["ContactNote"]:
        return db.query(cls).filter(
            cls.contact_id == contact_id,
            cls.user_id == user_id
        ).order_by(cls.created_at.desc()).all()

    @classmethod
    def get_by_id(cls, db: Session, user_id: int, note_id: int) -> "ContactNote | None":
        return db.query(cls).filter(cls.id == note_id, cls.user_id == user_id).first()

    def delete(self, db: Session):
        db.delete(self)
        db.commit()
