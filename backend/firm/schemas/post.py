from typing import Optional, List
from pydantic import BaseModel, Field


class CreateFirmRequest(BaseModel):
    name: str = Field(..., json_schema_extra={"example": "Best Wholesale LLC"})
    inn: Optional[str] = Field(None, json_schema_extra={"example": "123456789"})
    mfo: Optional[str] = Field(None, json_schema_extra={"example": "00123"})
    address: Optional[str] = Field(None, json_schema_extra={"example": "Tashkent, Chilanzar 5"})
    location: Optional[str] = Field(None, json_schema_extra={"example": "41.311081, 69.240562"})
    firm_category: Optional[str] = Field(None, json_schema_extra={"example": "Drink Wholesale"})
    description: Optional[str] = Field(None, json_schema_extra={"example": "Leading distributor of soft drinks"})
    additional_phones: Optional[List[str]] = Field(None, json_schema_extra={"example": ["+998901234568"]})
