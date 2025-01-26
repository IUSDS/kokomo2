from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    USER: str
    password: str

class UserResponse(BaseModel):
    member_id: int
    full_name: str
    membership_type: str
    points: int
    picture_url: Optional[str]
    address: set
    email_id: str
    phone_number: int
    emergency_contact: int