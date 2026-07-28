from pydantic import BaseModel, Field


class UpdateCategoryRequest(BaseModel):
    name: str = Field(..., json_schema_extra={"example": "Juices & Drinks"})
