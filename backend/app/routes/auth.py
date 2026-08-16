import os
import json
import time
import secrets
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.database.session import get_db
from app.models.student import Student
from app.models.skill import StudentSkill
from app.models.evidence import Evidence
from app.models.otp import OTP
from app.schemas.student import (
    RegisterOtpRequest,
    VerifyRegisterOtpRequest,
    ForgotPasswordOtpRequest,
    VerifyResetOtpRequest,
    ResetPasswordRequest,
    ResendOtpRequest,
    OtpResponse,
    StudentLoginResponse,
    StudentDetailRead,
)
from app.core.security import (
    hash_password,
    verify_password,
    validate_password_strength,
    PASSWORD_VALIDATION_ERROR_MSG,
    create_access_token,
)
from app.services.email_service import EmailService

router = APIRouter(prefix="/auth", tags=["Authentication & OTP"])

OTP_EXPIRATION_MINUTES = 10
RESET_TOKEN_EXPIRATION_MINUTES = 15
RESEND_COOLDOWN_SECONDS = 60


def _generate_otp_code() -> str:
    """Generate a cryptographically secure 6-digit numeric OTP."""
    return str(secrets.randbelow(900000) + 100000)


def _is_expired(dt: Optional[datetime]) -> bool:
    """Safely check if a datetime is expired regardless of timezone-naive/aware formats."""
    if dt is None:
        return True
    now_utc = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt < now_utc


@router.get("/email-status", summary="Check Configured Email Providers")
def check_email_status() -> dict:
    """Diagnostic endpoint reporting active email providers in production without exposing secrets."""
    status = EmailService.get_provider_status()
    return {
        "status": "ok",
        "live_email_configured": status["has_live_provider"],
        "providers_detected": status["configured_providers"],
        "sender": status["sender_email"],
        "setup_guide": {
            "option_1_resend": "Set RESEND_API_KEY and EMAIL_FROM in Vercel Environment Variables.",
            "option_2_gmail_smtp": "Set SMTP_HOST=smtp.gmail.com, SMTP_PORT=587, SMTP_USER=<email>, SMTP_PASSWORD=<16-digit-app-password>, EMAIL_FROM=SkillBridge <<email>> in Vercel.",
            "option_3_brevo": "Set BREVO_API_KEY and EMAIL_FROM in Vercel Environment Variables.",
        }
    }


@router.post("/register-otp", response_model=OtpResponse, summary="Send Email OTP for New Account Registration")
def send_register_otp(payload: RegisterOtpRequest, db: Session = Depends(get_db)) -> OtpResponse:
    """Validate registration details and send a secure 6-digit OTP to the user's Gmail/email address."""
    name_clean = " ".join(payload.name.strip().split())
    email_clean = payload.email.strip().lower()
    password_clean = payload.password.strip()

    if not name_clean:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Full Name is required.",
        )

    if not email_clean or "@" not in email_clean:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A valid email address is required.",
        )

    # 1. Validate password strength
    is_valid_pwd, pwd_error = validate_password_strength(password_clean)
    if not is_valid_pwd:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=pwd_error,
        )

    # 2. Validate password confirmation if provided
    if payload.confirm_password is not None:
        if password_clean != payload.confirm_password.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match.",
            )

    # 3. Check duplicate account in PostgreSQL
    existing = db.query(Student).filter(
        (func.lower(Student.email) == email_clean) |
        (func.lower(Student.name) == name_clean.lower())
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account already exists. Please log in instead.",
        )

    # 4. Invalidate any previous unused registration OTPs for this email
    db.query(OTP).filter(
        OTP.email == email_clean,
        OTP.purpose == "register",
        OTP.is_used == False,
    ).delete(synchronize_session=False)

    # 5. Generate secure OTP code and expiration
    otp_code = _generate_otp_code()
    now_utc = datetime.now(timezone.utc)
    expires_at = now_utc + timedelta(minutes=OTP_EXPIRATION_MINUTES)

    otp_record = OTP(
        email=email_clean,
        otp_hash=hash_password(otp_code),
        purpose="register",
        payload_json=json.dumps({
            "name": name_clean,
            "password_hash": hash_password(password_clean),
        }),
        expires_at=expires_at,
        attempts_left=5,
        is_used=False,
    )
    db.add(otp_record)
    db.commit()

    # 6. Deliver real OTP to Gmail/Email
    is_sent, delivery_info = EmailService.send_otp_email(email_clean, otp_code, "register")

    return OtpResponse(
        message="Verification code sent to your email. Please check your inbox and spam folder.",
        email=email_clean,
        cooldown_seconds=RESEND_COOLDOWN_SECONDS,
    )



@router.post("/verify-register-otp", response_model=StudentLoginResponse, summary="Verify OTP and Create Account")
def verify_register_otp(payload: VerifyRegisterOtpRequest, db: Session = Depends(get_db)) -> StudentLoginResponse:
    """Verify the 6-digit OTP code sent to Gmail and create the permanent user record in PostgreSQL."""
    email_clean = payload.email.strip().lower()
    otp_input = payload.otp.strip()

    if not otp_input:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please enter the 6-digit verification code.",
        )

    # Find the active registration OTP record
    otp_record = (
        db.query(OTP)
        .filter(
            OTP.email == email_clean,
            OTP.purpose == "register",
            OTP.is_used == False,
        )
        .order_by(OTP.created_at.desc())
        .first()
    )

    if not otp_record or _is_expired(otp_record.expires_at):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This OTP has expired. Please request a new OTP.",
        )

    # Check brute-force attempts limit
    if otp_record.attempts_left <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Too many invalid attempts. Please request a new OTP.",
        )

    # Verify OTP hash
    if not verify_password(otp_input, otp_record.otp_hash):
        otp_record.attempts_left -= 1
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP. Please try again.",
        )

    # Mark OTP as used
    otp_record.is_used = True

    # Parse saved payload (name & password hash)
    payload_data = json.loads(otp_record.payload_json or "{}")
    student_name = payload_data.get("name", "Student")
    password_hash = payload_data.get("password_hash")

    # Double-check duplicate before final INSERT
    existing = db.query(Student).filter(Student.email == email_clean).first()
    if existing:
        db.commit()
        token = create_access_token(existing.id)
        return StudentLoginResponse(
            student=existing,
            token=token,
            message="Account verified successfully.",
            last_screen=existing.last_screen or "dashboard",
        )

    # Insert verified student into PostgreSQL
    new_student = Student(
        name=student_name,
        email=email_clean,
        university="SkillBridge Academic Network",
        graduation_year=2027,
        password_hash=password_hash,
        last_screen="dashboard",
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    new_student.skills = []
    new_student.evidence = []

    token = create_access_token(new_student.id)
    return StudentLoginResponse(
        student=new_student,
        token=token,
        message=f"Account created successfully. Welcome to SkillBridge, {new_student.name}!",
        last_screen="dashboard",
    )


@router.post("/forgot-password-otp", response_model=OtpResponse, summary="Request Password Reset OTP")
def send_forgot_password_otp(payload: ForgotPasswordOtpRequest, db: Session = Depends(get_db)) -> OtpResponse:
    """Send a secure 6-digit password reset OTP to the registered Gmail address."""
    email_clean = payload.email.strip().lower()

    if not email_clean:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Please enter your registered Gmail/email address.",
        )

    # Check if student exists in PostgreSQL
    student = db.query(Student).filter(
        (func.lower(Student.email) == email_clean) |
        (func.lower(Student.name) == email_clean)
    ).first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account found with this email. Please create an account first.",
        )

    # Invalidate previous unused forgot-password OTPs for this email
    db.query(OTP).filter(
        OTP.email == student.email,
        OTP.purpose == "forgot_password",
        OTP.is_used == False,
    ).delete(synchronize_session=False)

    otp_code = _generate_otp_code()
    now_utc = datetime.now(timezone.utc)
    expires_at = now_utc + timedelta(minutes=OTP_EXPIRATION_MINUTES)

    otp_record = OTP(
        email=student.email,
        otp_hash=hash_password(otp_code),
        purpose="forgot_password",
        expires_at=expires_at,
        attempts_left=5,
        is_used=False,
    )
    db.add(otp_record)
    db.commit()

    # Deliver real OTP
    is_sent, delivery_info = EmailService.send_otp_email(student.email, otp_code, "forgot_password")

    return OtpResponse(
        message="Password reset code sent to your email. Please check your inbox and spam folder.",
        email=student.email,
        cooldown_seconds=RESEND_COOLDOWN_SECONDS,
    )



@router.post("/verify-reset-otp", response_model=OtpResponse, summary="Verify Password Reset OTP")
def verify_reset_otp(payload: VerifyResetOtpRequest, db: Session = Depends(get_db)) -> OtpResponse:
    """Verify the password reset OTP and generate a single-use password reset token."""
    email_clean = payload.email.strip().lower()
    otp_input = payload.otp.strip()

    if not otp_input:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please enter the 6-digit verification code.",
        )

    now_utc = datetime.now(timezone.utc)

    otp_record = (
        db.query(OTP)
        .filter(
            OTP.email == email_clean,
            OTP.purpose == "forgot_password",
            OTP.is_used == False,
        )
        .order_by(OTP.created_at.desc())
        .first()
    )

    if not otp_record or _is_expired(otp_record.expires_at):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This OTP has expired. Please request a new OTP.",
        )

    if otp_record.attempts_left <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Too many invalid attempts. Please request a new OTP.",
        )

    if not verify_password(otp_input, otp_record.otp_hash):
        otp_record.attempts_left -= 1
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP. Please try again.",
        )

    # Invalidate OTP code and generate time-limited reset token
    otp_record.is_used = True
    reset_token = secrets.token_urlsafe(32)
    otp_record.reset_token = reset_token
    otp_record.reset_token_expires_at = now_utc + timedelta(minutes=RESET_TOKEN_EXPIRATION_MINUTES)
    db.commit()

    return OtpResponse(
        message="OTP verified successfully.",
        email=email_clean,
        reset_token=reset_token,
    )


@router.post("/reset-password", response_model=OtpResponse, summary="Reset Password in PostgreSQL")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)) -> OtpResponse:
    """Update user's password in PostgreSQL after verified OTP authorization."""
    email_clean = payload.email.strip().lower()
    new_password = payload.new_password.strip()

    # 1. Validate password strength
    is_valid_pwd, pwd_error = validate_password_strength(new_password)
    if not is_valid_pwd:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=pwd_error,
        )

    # 2. Check password confirmation
    if payload.confirm_password is not None:
        if new_password != payload.confirm_password.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match.",
            )

    # 3. Verify reset token
    otp_record = (
        db.query(OTP)
        .filter(
            OTP.email == email_clean,
            OTP.reset_token == payload.reset_token,
        )
        .first()
    )

    if not otp_record or _is_expired(otp_record.reset_token_expires_at):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset session. Please request a new OTP.",
        )

    # 4. Find student and update password in PostgreSQL
    student = db.query(Student).filter(Student.email == email_clean).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account found with this email. Please create an account first.",
        )

    student.password_hash = hash_password(new_password)

    # Invalidate reset token so it cannot be reused
    otp_record.reset_token = None
    otp_record.reset_token_expires_at = None

    db.commit()

    return OtpResponse(
        message="Password updated successfully. Please log in with your new password.",
        email=email_clean,
    )



@router.post("/resend-otp", response_model=OtpResponse, summary="Resend OTP with Cooldown Enforcement")
def resend_otp(payload: ResendOtpRequest, db: Session = Depends(get_db)) -> OtpResponse:
    """Resend a fresh 6-digit OTP code enforcing rate-limiting cooldown."""
    email_clean = payload.email.strip().lower()
    purpose = payload.purpose if payload.purpose in ("register", "forgot_password") else "register"

    if not email_clean:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email address is required.",
        )

    now_utc = datetime.now(timezone.utc)

    # Check cooldown against recent OTP
    recent_otp = (
        db.query(OTP)
        .filter(
            OTP.email == email_clean,
            OTP.purpose == purpose,
        )
        .order_by(OTP.created_at.desc())
        .first()
    )

    if recent_otp and recent_otp.created_at:
        # Calculate time elapsed
        created_at = recent_otp.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        elapsed = (now_utc - created_at).total_seconds()
        if elapsed < RESEND_COOLDOWN_SECONDS:
            remaining = int(RESEND_COOLDOWN_SECONDS - elapsed)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Please wait {remaining} seconds before requesting a new OTP.",
            )

    # If purpose is forgot_password, check student exists
    if purpose == "forgot_password":
        student = db.query(Student).filter(Student.email == email_clean).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No account found with this email. Please create an account first.",
            )

    # Invalidate previous OTPs
    if recent_otp:
        recent_otp.is_used = True

    # Generate new OTP
    otp_code = _generate_otp_code()
    expires_at = now_utc + timedelta(minutes=OTP_EXPIRATION_MINUTES)

    new_otp = OTP(
        email=email_clean,
        otp_hash=hash_password(otp_code),
        purpose=purpose,
        payload_json=recent_otp.payload_json if recent_otp else None,
        expires_at=expires_at,
        attempts_left=5,
        is_used=False,
    )
    db.add(new_otp)
    db.commit()

    # Deliver real OTP
    is_sent, delivery_info = EmailService.send_otp_email(email_clean, otp_code, purpose)

    return OtpResponse(
        message="A new verification code has been sent to your email. Please check your inbox and spam folder.",
        email=email_clean,
        cooldown_seconds=RESEND_COOLDOWN_SECONDS,
    )

