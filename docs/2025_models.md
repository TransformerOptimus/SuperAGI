# 2025 AI Models - SuperAGI

This document outlines the latest AI models available in SuperAGI as of January 2025. All models listed are from January 2025 or newer releases.

## Supported Providers

### OpenAI Models (2025)
- **gpt-4o-2025-01-15**: Latest multimodal model with 200K context, vision, and enhanced efficiency
- **o3-mini**: Advanced reasoning model with 200K context and improved cost-effectiveness
- **o3**: Most advanced reasoning model with 300K context for complex scientific problems

### Anthropic Models (2025)
- **claude-3-5-sonnet-20250120**: Enhanced model with 500K context and improved reasoning
- **claude-3-5-haiku-20250115**: Ultra-fast model with 400K context and improved efficiency
- **claude-4-opus**: Most advanced Claude model with 1M context and multimodal capabilities

### Google Models (2025)
- **gemini-2.0-flash**: Next-generation model with 2M context and ultra-fast inference
- **gemini-2.0-pro**: Most advanced Google model with 5M context and superior reasoning

### xAI (Grok) Models (2025)
- **grok-2**: Next-generation conversational AI with enhanced reasoning and vision capabilities

### Groq Models (2025)
- **llama-3.3-70b-versatile**: Latest Meta model with 300K context and ultra-fast inference
- **llama-3.3-8b-instant**: Cost-effective model with lightning-fast inference speed

### DeepSeek Models (2025)
- **deepseek-v3**: Advanced coding and reasoning model with exceptional performance

### Mistral AI Models (2025)
- **mistral-large-2-2025**: Enhanced European AI model with superior multilingual capabilities

## Key Features

### Enhanced Context Lengths
- Gemini 2.0 Pro: 5M tokens
- Claude 4 Opus: 1M tokens
- Gemini 2.0 Flash: 2M tokens
- Claude 3.5 Sonnet: 500K tokens

### Cost Optimization
- DeepSeek V3: $0.0001 per 1M input tokens
- Groq models: Starting at $0.03 per 1M input tokens
- Improved efficiency across all providers

### Advanced Capabilities
- Multimodal support (vision, audio, code)
- Enhanced reasoning capabilities
- Function calling support
- Streaming responses
- JSON mode support

## Migration from Legacy Models

All models from 2024 and earlier have been removed. This ensures access to only the latest, most capable AI models with improved performance, reduced costs, and enhanced features.

## Usage Example

```python
from superagi.types.api_models import get_model_by_name, ProviderType

# Get the latest GPT-4o model
gpt_model = get_model_by_name("gpt-4o-2025-01-15")
print(f"Context length: {gpt_model.context_length}")
print(f"Supports vision: {gpt_model.supports_vision}")

# Get all models from a specific provider
from superagi.types.api_models import get_models_by_provider
anthropic_models = get_models_by_provider(ProviderType.ANTHROPIC)
```