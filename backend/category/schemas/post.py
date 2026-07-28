from pydantic import BaseModel, Field


class CreateCategoryRequest(BaseModel):
    name: str = Field(..., json_schema_extra={"example": "Soft Drinks"})
