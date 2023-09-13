from pydantic import BaseModel

class LocalLLM(BaseModel):
    input_message: str
