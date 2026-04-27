from datetime import datetime
from enum import StrEnum
from pydantic import BaseModel, ConfigDict, Field
from .pyobject_id import PyObjectId


class DocumentStatus(StrEnum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentCreate(BaseModel):
    user_id: PyObjectId = Field()
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1)

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)


class DocuementResponse(BaseModel):
    _id: PyObjectId = Field(..., alias="_id")
    title: str = Field(..., min_length=1, max_length=100)
    user_id: PyObjectId = Field(...)
    content: str = Field(..., min_length=1)
    status: DocumentStatus = Field(default=DocumentStatus.QUEUED)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True, arbitrary_types_allowed=True, use_enum_values=True
    )
