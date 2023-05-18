from abc import abstractmethod

from pydantic import BaseModel, Field


class BaseMessage(BaseModel):
  """Message object."""

  content: str
  additional_kwargs: dict = Field(default_factory=dict)

  @property
  @abstractmethod
  def type(self) -> str:
    """Type of the message, used for serialization."""


class HumanMessage(BaseMessage):
  """Type of message that is spoken by the human."""

  example: bool = False

  @property
  def type(self) -> str:
    """Type of the message, used for serialization."""
    return "user"


class AIMessage(BaseMessage):
  """Type of message that is spoken by the AI."""

  example: bool = False

  @property
  def type(self) -> str:
    """Type of the message, used for serialization."""
    return "assistant"


class SystemMessage(BaseMessage):
  """Type of message that is a system message."""

  @property
  def type(self) -> str:
    """Type of the message, used for serialization."""
    return "system"
