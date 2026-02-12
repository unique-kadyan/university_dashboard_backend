from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr
from enums.user_type import UserType
from enums.gender import Gender


class UserRegisterRequest(BaseModel):
    user_type: UserType
    email: EmailStr
    user_name: str
    password: str
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    date_of_birth: Optional[str] = None
    gender: Optional[Gender] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None


class UserRegisterResponse(BaseModel):
    id: int
    user_type: UserType
    email: str
    user_name: str
    first_name: str
    last_name: str
    is_active: bool
    is_verified: bool

    model_config = ConfigDict(from_attributes=True)
