from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta

from app.database import Base 
from app.config import settings

class VerificationCode(Base):
    __tablename__ = 'verification_code'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    code = Column(String(5), nullable=False)
    created_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))
    is_used = Column(Boolean(), default=False)

    #Relationships
    user = relationship("User", back_populates="verification_code") #Define a one-to-many relationship with the User model

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.expires_at:
            self.expires_at = datetime.now() + timedelta(minutes=settings.VERIFICATION_CODE_EXPIRE_MINUTES)
    
    @property
    def is_expired(self):
        return datetime.now() > self.expires_at