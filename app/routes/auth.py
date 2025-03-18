from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, GoogleLogin, Token, UserResponse
from app.services.auth import(
    register_user,
    authenticate_user,
    authenticate_google,
    request_password_reset
)
from app.utils.security import get_current_user
from app.database import get_db
from pydantic import EmailStr

router = APIRouter(tags=["Authentication"])

@router.post("/signup", response_model=Token)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    user = register_user(db, user_data)
    return authenticate_user(db, UserLogin(
        fullname_or_email=user.fullname,
        password=user_data.password
    ))
    
@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    return authenticate_user(db, login_data)

@router.post("/token", response_model=Token)
def login_form(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return authenticate_user(db, UserLogin(
        fullname_or_email =  form_data.username,
        password= form_data.password
    ))

@router.post("/google-login", response_model=Token)
def google_login(login_data: GoogleLogin, db: Session = Depends(get_db)):
    return authenticate_google(db, login_data.token)

@router.post("/forget_password")
def forget_password(email: EmailStr = Body(..., embed=True), db: Session = Depends(get_db)):
    return request_password_reset(db, email)

@router.post("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

