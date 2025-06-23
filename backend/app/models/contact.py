from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base
from sqlalchemy.orm import Session

class Contact(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    hubspot_id = Column(String, unique=True)
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    company = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="contacts")
    contact_notes = relationship("ContactNote", back_populates="contact")

    @classmethod
    def create(cls, db: Session, user_id: int, name: str, email: str = None,
               phone: str = None, company: str = None,
               hubspot_id: str = None) -> "Contact":
        contact = cls(
            user_id=user_id,
            name=name,
            email=email,
            phone=phone,
            company=company,
            hubspot_id=hubspot_id
        )
        db.add(contact)
        db.commit()
        db.refresh(contact)
        return contact

    @classmethod
    def get_all_for_user(cls, db: Session, user_id: int) -> list["Contact"]:
        return db.query(cls).filter(cls.user_id == user_id).all()

    @classmethod
    def get_by_id(cls, db: Session, user_id: int, contact_id: int) -> "Contact | None":
        return db.query(cls).filter(cls.user_id == user_id, cls.id == contact_id).first()

    @classmethod
    def get_by_email(cls, db: Session, user_id: int, email: str) -> "Contact | None":
        return db.query(cls).filter(cls.user_id == user_id, cls.email == email).first()

    def update(self, db: Session, **kwargs) -> "Contact":
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
        db.commit()
        db.refresh(self)
        return self

    def delete(self, db: Session):
        db.delete(self)
        db.commit()
