from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.database.session import Base


class OTP(Base):
    __tablename__ = "otps"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, index=True)
    otp_hash = Column(String(255), nullable=False)
    purpose = Column(String(50), nullable=False)  # "register", "forgot_password"
    payload_json = Column(Text, nullable=True)  # JSON metadata (e.g. pending registration name, password_hash)
    reset_token = Column(String(255), nullable=True, index=True)
    reset_token_expires_at = Column(DateTime(timezone=True), nullable=True)
    attempts_left = Column(Integer, default=5, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
