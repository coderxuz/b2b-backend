from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class FirmDetailResponse(BaseModel):
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
