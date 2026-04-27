from typing import Annotated, Any
from bson import ObjectId
from pydantic.functional_validators import BeforeValidator
from pydantic.functional_serializers import PlainSerializer
from pydantic import WithJsonSchema


# 1. Validation: Ensures the input is a valid 24-character hex string or ObjectId
def validate_object_id(v: Any) -> ObjectId:
    if isinstance(v, ObjectId):
        return v
    if isinstance(v, str) and ObjectId.is_valid(v):
        return ObjectId(v)
    raise ValueError("Invalid ObjectId")


# 2. Custom Type Alias
# - BeforeValidator: Converts incoming string to BSON ObjectId for your internal logic
# - PlainSerializer: Converts BSON ObjectId back to string for JSON responses
# - WithJsonSchema: Defines how this type appears in OpenAPI/Swagger documentation
PyObjectId = Annotated[
    ObjectId,
    BeforeValidator(validate_object_id),
    PlainSerializer(lambda x: str(x), return_type=str),
    WithJsonSchema(
        {"type": "string", "example": "507f1f77bcf86cd799439011", "description": "MongoDB ObjectId as a hex string"}
    ),
]
