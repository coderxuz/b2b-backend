from typing import Optional
from pydantic import BaseModel, Field
from db.models.user import UserRole


class VerifyOTPRequest(BaseModel):
    phone: str = Field(..., json_schema_extra={"example": "+998901234567"})
    otp: str = Field(..., json_schema_extra={"example": "123456"}, min_length=6, max_length=6)


class RegisterRequest(BaseModel):
    phone: str = Field(..., json_schema_extra={"example": "+998901234567"})
    otp: str = Field(..., json_schema_extra={"example": "123456"}, min_length=6, max_length=6)
    first_name: str = Field(..., json_schema_extra={"example": "John"})
    last_name: Optional[str] = Field(None, json_schema_extra={"example": "Doe"})
    age: Optional[int] = Field(None, json_schema_extra={"example": 30})
    role: UserRole = Field(default=UserRole.SHOP_OWNER, json_schema_extra={"example": UserRole.DISTRIBUTOR})


class LoginRequest(BaseModel):
    phone: str = Field(..., json_schema_extra={"example": "+998901234567"})
    otp: str = Field(..., json_schema_extra={"example": "123456"}, min_length=6, max_length=6)


class RefreshTokenRequest(BaseModel):
    refresh_token: str
