'''from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base
from sqlalchemy.orm import Session

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    type = Column(String)
    status = Column(String, default="pending")
    task_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="tasks")
    
    @classmethod
    def create(cls, db: Session, user_id: int, type: str, task_metadata: dict = None) -> "Task":
        task = cls(user_id=user_id, type=type, task_metadata=task_metadata or {}, status="pending")
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    @classmethod
    def get_all_for_user(cls, db: Session, user_id: int):
        return db.query(cls).filter(cls.user_id == user_id).all()

    @classmethod
    def get_by_id(cls, db: Session, task_id: int, user_id: int):
        return db.query(cls).filter(cls.id == task_id, cls.user_id == user_id).first()

    def delete(self, db: Session):
        db.delete(self)
        db.commit()'''
        
        
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    type = Column(String)
    status = Column(String, default="pending")
    task_metadata = Column(JSON)
    external_reference = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="tasks")

    @classmethod
    def create(cls, db, user_id, type, task_metadata=None, external_reference=None):
        task = cls(user_id=user_id, type=type, status="pending",
                   task_metadata=task_metadata or {}, external_reference=external_reference)
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    @classmethod
    def get_pending_for_user(cls, db, user_id):
        return db.query(cls).filter_by(user_id=user_id, status="pending").all()


