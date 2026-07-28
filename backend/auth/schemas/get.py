import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from db.models.user import UserRole


class FirmResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    tariff_id: Optional[int] = None
    name: str
    inn: Optional[str] = None
    mfo: Optional[str] = None
    address: Optional[str] = None
    location: Optional[str] = None
    firm_category: Optional[str] = None
    description: Optional[str] = None
    additional_phones: Optional[List[str]] = None
    is_active: bool


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: Optional[str] = None
    age: Optional[int] = None
    phone: str
    role: UserRole
    is_active: bool
    created_at: datetime.datetime
    firm: Optional[FirmResponse] = None
