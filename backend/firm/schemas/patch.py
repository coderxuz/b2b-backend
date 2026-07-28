from pydantic import BaseModel, Field


class UpdateFirmStatusRequest(BaseModel):
    is_active: bool = Field(..., json_schema_extra={"example": False})
