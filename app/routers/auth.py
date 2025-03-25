from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreatePassword, UserVerify
from app.utils.security import verify_password, get_password_hash, create_access_token
from app.utils.verification import create_verification_code
from app.utils.email import send_verification_email
from app.utils.verification import verify_code
from app.middleware.authentification import get_current_user
from app.config import settings

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(),db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_verified:
        raise HTTPException(
            status_code= status.HTTP_403_FORBIDDEN,
            detail="Email not verified"
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub" : user.email, "user_id": user.id},
        expires_delta=access_token_expires
    )

    return{"access_token" : access_token, "token_type": "bearer"}

@router.post("/set-password")
async def set_password(password_data: UserCreatePassword, current_user: User = Depends(get_current_user), db: Session=Depends(get_db)):
    if current_user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password already set"
        )
    current_user.hashed_password= get_password_hash(password_data.password)
    db.commit()

    return {"message": "Password set successfully"}

@router.post("/verify")
async def verify_account(verification_data: UserVerify, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.is_verified:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail = "Account already verified"
        )
    is_valid = verify_code(
        db=db,
        user_id= current_user.id,
        code=verification_data.verification_code
    )

    if not is_valid: 
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code"
        )
    
    current_user.is_verified = True
    current_user.is_active = True
    db.commit()

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user.email, "user_id": current_user.id},
        expires_delta= access_token_expires
    )

    return{
        "message": "Account verified successfully",
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/resend-code")
async def resend_verification_code(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account aleardy verified"
        )
    
    verification = create_verification_code(db=db, user_id=current_user.id)
    await send_verification_email(email=current_user.email, verification_code=verification.code)
    return {"message" : "Verification coede sent successfully"}
