from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True,index=True)
    full_name = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    mobile_number = Column(String(15), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean(), default=False)
    is_verified = Column(Boolean(), default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    verification_code = relationship("VerificationCode", back_populates="user")