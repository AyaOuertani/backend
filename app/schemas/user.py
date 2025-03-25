from pydantic import BaseModel, EmailStr, Field, validator
import re
from typing import Optional

class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    mobile_number: str

    #Validation for mobile number
    @validator('mobile_number')
    def mobile_number_must_be_valid(cls, v):
        pattern = r'^\+?[0-9]{10,15}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid mobile number format')
        return v

class UserCreate(UserBase): 
    full_name: str
    email: EmailStr
    mobile_number: str

class UserCreatePassword(UserBase):
    email: EmailStr
    password: str = Field(..., min_length=8)
    confirm_password: str

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

class UserVerify(UserBase):
    verification_code: str = Field(..., min_length=5, max_length=5)

class User(BaseModel): #User model for response
    id:int
    is_active: bool
    is_verified: bool

    class Config:
        orm_mode = True

class UserInDB(UserBase):
    hashed_password: str

    class Config:
        orm_mode = True