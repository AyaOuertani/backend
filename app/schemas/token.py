from pydantic import BaseModel
from typing import Optional

class Token(BaseModel): #Response model for token
    access_token: str
    token_type: str

class TokenData(BaseModel): #Stores token data
    email: Optional[str] = None
    user_id: Optional[int] = None