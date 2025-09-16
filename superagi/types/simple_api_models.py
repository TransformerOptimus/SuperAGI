"""
Simplified API models for testing.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Task execution status enumeration."""
    
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProviderType(str, Enum):
    """AI provider type enumeration with latest supported providers."""
    
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    GROK = "grok"  # xAI's Grok models
    GROQ = "groq"  # Hardware-accelerated inference provider
    REPLICATE = "replicate"
    HUGGINGFACE = "huggingface"
    LOCAL_LLM = "local_llm"


class ModelCapability(str, Enum):
    """Model capability enumeration."""
    
    TEXT_GENERATION = "text_generation"
    CODE_GENERATION = "code_generation"
    REASONING = "reasoning"
    VISION = "vision"
    MULTIMODAL = "multimodal"
    FUNCTION_CALLING = "function_calling"


class ModelSpec(BaseModel):
    """Specification for an AI model."""
    
    name: str
    provider: ProviderType
    capabilities: List[ModelCapability]
    context_length: int
    supports_vision: bool = False
    release_date: Optional[str] = None
    description: str


# Define some sample models for testing
OPENAI_MODELS = [
    ModelSpec(
        name="gpt-4o",
        provider=ProviderType.OPENAI,
        capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.CODE_GENERATION, ModelCapability.VISION],
        context_length=128000,
        supports_vision=True,
        release_date="2024-05-13",
        description="GPT-4o: Advanced multimodal model"
    ),
    ModelSpec(
        name="o1-preview",
        provider=ProviderType.OPENAI,
        capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.REASONING],
        context_length=128000,
        supports_vision=False,
        release_date="2024-09-12",
        description="o1-preview: Advanced reasoning model"
    ),
]

ANTHROPIC_MODELS = [
    ModelSpec(
        name="claude-3-5-sonnet-20241022",
        provider=ProviderType.ANTHROPIC,
        capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.CODE_GENERATION, ModelCapability.VISION],
        context_length=200000,
        supports_vision=True,
        release_date="2024-10-22",
        description="Claude 3.5 Sonnet: Latest model with enhanced capabilities"
    ),
]

GROQ_MODELS = [
    ModelSpec(
        name="llama-3.1-70b-versatile",
        provider=ProviderType.GROQ,
        capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.CODE_GENERATION],
        context_length=131072,
        supports_vision=False,
        release_date="2024-07-23",
        description="Llama 3.1 70B on Groq: Ultra-fast inference"
    ),
]

ALL_MODELS = OPENAI_MODELS + ANTHROPIC_MODELS + GROQ_MODELS


def get_models_by_provider(provider: ProviderType) -> List[ModelSpec]:
    """Get all models for a specific provider."""
    return [model for model in ALL_MODELS if model.provider == provider]


def get_latest_models() -> List[ModelSpec]:
    """Get the latest models (released in 2024)."""
    return [model for model in ALL_MODELS if model.release_date and model.release_date.startswith("2024")]