from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base
from sqlalchemy.orm import Session

class CalendarEvent(Base):
    __tablename__ = 'calendar_events'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    event_id = Column(String, unique=True)
    title = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    attendees = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="calendar_events")

    # Create new calendar event
    @classmethod
    def create(cls, db: Session, user_id: int, title: str, start_time: datetime, end_time: datetime, attendees: list, event_id: str = None) -> "CalendarEvent":
        event = cls(
            user_id=user_id,
            event_id=event_id,
            title=title,
            start_time=start_time,
            end_time=end_time,
            attendees=attendees,
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    # Get all upcoming events for a user
    @classmethod
    def get_all_upcoming(cls, db: Session, user_id: int) -> list["CalendarEvent"]:
        return (
            db.query(cls)
            .filter(cls.user_id == user_id, cls.start_time >= datetime.utcnow())
            .order_by(cls.start_time.asc())
            .all()
        )

    # Get by internal ID or Google event ID
    @classmethod
    def get_by_event_id(cls, db: Session, user_id: int, event_id: str):
        return db.query(cls).filter(cls.user_id == user_id, cls.event_id == event_id).first()

    # Delete the event
    def delete(self, db: Session):
        db.delete(self)
        db.commit()