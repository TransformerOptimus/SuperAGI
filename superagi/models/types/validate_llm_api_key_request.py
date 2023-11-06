from pydantic import BaseModel


class ValidateAPIKeyRequest(BaseModel):
    model_source: str
    model_api_key: str
