import random
import string
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.verification import VerificationCode

def generate_verification_code(length=5) :
    return ''.join(random.choices(string.digits, k=length))

def create_verification_code(db: Session, user_id: int) :

    exisiting_codes = db.query(VerificationCode).filter(
        VerificationCode.user_id == user_id,
        VerificationCode.is_used == False,
        VerificationCode.expires_at > datetime.now()
    ).all()

    for code in exisiting_codes :
        code.is_used = True
    
    #create a new verification code
    verification_code = VerificationCode(
        user_id=user_id,
        code=generate_verification_code()
    )

    db.add(verification_code)
    db.commit()
    db.refresh(verification_code)

    return verification_code

def verify_code(db: Session, user_id: int, code: str) :
    verification_code = db.query(VerificationCode).filter(
        VerificationCode.user_id == user_id,
        VerificationCode.code == code,
        VerificationCode.is_used == False,
        VerificationCode.expires_at > datetime.now()
    ).first()

    if not verification_code :
       return False
    
    #mark the code as used
    verification_code.is_used = True
    db.commit()
    
    return True