from sqlalchemy import Column, Integer, Text, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base
from sqlalchemy.orm import Session

class Instruction(Base):
    __tablename__ = 'instructions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    condition = Column(Text)
    action = Column(Text)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="instructions")

    
    @classmethod
    def create(cls, db: Session, user_id: int, condition: str, action: str, active: bool = True) -> "Instruction":
        instruction = cls(
            user_id=user_id,
            condition=condition,
            action=action,
            active=active,
        )
        db.add(instruction)
        db.commit()
        db.refresh(instruction)
        return instruction

    @classmethod
    def get_all(cls, db: Session, user_id: int, only_active: bool = False) -> list["Instruction"]:
        query = db.query(cls).filter(cls.user_id == user_id)
        if only_active:
            query = query.filter(cls.active == True)
        return query.order_by(cls.created_at.desc()).all()

    @classmethod
    def get_by_id(cls, db: Session, user_id: int, instruction_id: int) -> "Instruction | None":
        return db.query(cls).filter(cls.id == instruction_id, cls.user_id == user_id).first()

    def deactivate(self, db: Session):
        self.active = False
        db.commit()
        db.refresh(self)

    def delete(self, db: Session):
        db.delete(self)
        db.commit()
