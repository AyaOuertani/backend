from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.user import User 
from app.schemas.user import UserCreatePassword, User as UserSchema
from app.utils.security import get_password_hash, create_access_token
from app.utils.verification import create_verification_code
from app.utils.email import send_verification_email
from datetime import timedelta
from app.config import settings

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreatePassword, db: Session = Depends(get_db)):
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user: 
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if mobile number already exists
    existing_mobile = db.query(User).filter(User.mobile_number == user_data.mobile_number).first()
    if existing_mobile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mobile number already registered"
        )
    
    try:
        # Hash the password
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            full_name=user_data.full_name,
            email=user_data.email,
            mobile_number=user_data.mobile_number,
            hashed_password= hashed_password,
            is_active=False,
            is_verified=False
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        verification = create_verification_code(db=db, user_id=new_user.id)

        await send_verification_email(
            email=new_user.email,
            verification_code=verification.code
        )

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": new_user.email, "user_id": new_user.id}, 
            expires_delta=access_token_expires
        )

        return {
            "id": new_user.id,
            "is_active": new_user.is_active,
            "is_verified": new_user.is_verified,
            "access_token": access_token,
            "token_type": "bearer"
        }

    except IntegrityError as e:
        db.rollback()
        print(f"Registration Integrity Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )
    except Exception as e :
        db.rollback()
        print(f"Unexpected REgistration Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Enexpected error during registration"
        )