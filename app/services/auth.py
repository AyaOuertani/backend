from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import ssl
import jwt
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserCreate, UserCreate, UserLogin, Token, UserResponse
from app.utils.security import get_password_hash, verify_password, create_access_token
from app.config import settings
import datetime 
import requests
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = os.getenv("SMTP_EMAIL", "ouertaniaya03@gmail.com")
EMAIL_PASSWORD = os.getenv("SMTP_PASSWORD", "Aya_Ouertani_03")

def register_user(db: Session, user_data: UserCreate):
    existing_user = db.query(User).filter(User.fullname == user_data.fullname).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email: 
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = get_password_hash(user_data.password)
    
    user = User(
        fullname = user_data.fullname,
        email = user_data.email,
        hashed_password= hashed_password
    )
    
    try : 
        db.add(user)
        db.commit()
        db.refresh(user)
        logging.info(f"User registred successfully: {user.fullname}")
        return user
    except Exception as e :
        db.rollback()
        logger.error(f"Error registering user: {str(e)}")
        raise HTTPException(
            status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while registering user"   
        )
def authenticate_user(db : Session, login_data : UserLogin):
    user = db.query(User).filter(
        (User.fullname == login_data.fullname_or_email)|
        (User.email == login_data.fullname_or_email)
    ).first()
    
    if not user :
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail="Invalid username or password"
        )
    
    if not verify_password(login_data.password, user.hashed_password) :
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    access_token_expires = datetime.timedelta(minutes= settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub" : user.id}, expires_delta=access_token_expires
    )
    
    return Token(
        access_token= access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            fullname=user.fullname,
            is_active=user.is_active,
            created_at=user.created_at,
        )
    )
def authenticate_google(db: Session, token: str):
    try:
        google_response = requests.get(
            f"https://www.googleapis.com/oauth2/v3/tokeninfo?id_token={token}"
        )
        if google_response.status_code != 200 :
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Google token"
            )
        google_data = google_response.json()
        google_id = google_data.get("sub")
        email = google_data.get("email")
        name = google_data.get("name","")
        
        if not google_id or not email :
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Google account information"
            )
        if not user:
            user = db.query(User).filter(User.email == email).first()
            
            if not user:
                
                base_fullname = name if name else email.split("@")[0]
                fullname = base_fullname
                counter = 1
                
                while db.query(User).filter(User.fullname == fullname).first():
                    fullname = f"{base_fullname}{counter}"
                    counter += 1
            
                user = User(
                    fullname = fullname,
                    email = email,
                    google_id = google_id,
                    is_active = True,
                    hashed_password = None
                )
                db.add(user)
                db.commit()
                db.refresh(user)
        access_token_expires = datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.id}, expires_delta=access_token_expires
        )
        return Token (
             access_token=access_token,
             token_type="bearer",
             user=UserResponse(
                 id=user.id,
                 fullname=user.fullname,
                 email=user.email,
                 is_active=user.is_active,
                 created_at=user.created_at,
                 
             )
        )
    except Exception as e :
        logger.error(f"Error authonticating with Google: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during Foofle authontication"
        )
    
def request_password_reset(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()

    if user:
        try:
            # Generate reset token and send email (Ensure these functions exist)
            reset_token = generate_reset_token(user.email)
            send_reset_email(user.email, reset_token)
        except Exception as e:
            logging.error(f"Error sending password reset email: {e}")
            raise HTTPException(status_code=500, detail="An error occurred while processing your request.")

    # Generic response to prevent email enumeration
    return {"message": "If an account exists with this email, a password reset link has been sent."}

def generate_reset_token(email: str, expires_in: int = 600):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in)
    
    payload = {
        "email": email,
        "exp": expiration
    }
    token = jwt.encoded(payload)
    
    return token

def send_reset_email(email: str, token: str):
    try: 
        msg = MIMEMultipart()
        msg["From"] = EMAIL_SENDER
        msg["To"] = email
        msg["Subject"] = "Password Reset Verification Code"
        
        email_body = f"""
        <html>
        <body>
            <h2> Password Reset Request</h2>
            <p> Your verification code is: <b>{token}</b><p>
            <p>This code will expire in 10minites.</p>
            <p><b>if you did not requestthis, please ignore this email.</b></p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(email_body, "html"))
        
        context =ssl.create_default_context()
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, email, msg.as_string())
        
        print("Email sent successfully!")
        
    except Exception as e:
        print(f"error sending email:{e}")