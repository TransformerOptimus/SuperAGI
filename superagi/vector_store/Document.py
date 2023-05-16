from pydantic import BaseModel, Field


class Document(BaseModel):
    """Interface for interacting with a document."""

    text_content: str
    metadata: dict = Field(default_factory=dict)
