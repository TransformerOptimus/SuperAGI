from abc import abstractmethod
from pydantic import BaseModel, Field


class BaseMessage(BaseModel):
    """Base message object."""

    content: str
    additional_kwargs: dict = Field(default_factory=dict)

    @property
    @abstractmethod
    def type(self) -> str:
        """Message type used."""


class HumanMessage(BaseMessage):
    """Message by human."""

    example: bool = False

    @property
    def type(self) -> str:
        return "user"


class AIMessage(BaseMessage):
    """Type of message that is spoken by the AI."""

    example: bool = False

    @property
    def type(self) -> str:
        return "assistant"


class SystemMessage(BaseMessage):
    """Used when message is system message."""

    @property
    def type(self) -> str:
        return "system"


class GitHubLinkRequest(BaseModel):
    """Used for Request body in install API"""
    github_link: str
