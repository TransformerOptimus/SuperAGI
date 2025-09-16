# SuperAGI API Models Documentation

This document provides comprehensive documentation for the SuperAGI Core API models, including the latest AI models from major providers.

## Overview

The SuperAGI API uses Pydantic models for robust data validation, serialization, and documentation. The system supports multiple AI providers and the latest model releases as of 2024.

## Core Enumerations

### TaskStatus
Represents the execution status of tasks:
- `PENDING`: Task is queued and waiting to be processed
- `IN_PROGRESS`: Task is currently being executed
- `COMPLETED`: Task has finished successfully
- `FAILED`: Task encountered an error during execution
- `CANCELLED`: Task was cancelled before completion

### TaskType
Defines the type of AI-powered development tasks:
- `CODE_GENERATION`: Generate new code based on specifications
- `CODE_ANALYSIS`: Analyze existing code for patterns, issues, or insights
- `CODE_REVIEW`: Review code for quality, security, and best practices
- `DOCUMENTATION`: Generate or update documentation
- `TESTING`: Create or improve test coverage
- `DEBUGGING`: Identify and fix bugs in code
- `REFACTORING`: Improve code structure without changing functionality
- `SECURITY_AUDIT`: Analyze code for security vulnerabilities
- `PERFORMANCE_OPTIMIZATION`: Optimize code for better performance
- `CUSTOM`: Custom task types defined by users

### ProviderType
Supported AI providers (updated 2024):
- `OPENAI`: OpenAI's GPT models including GPT-4o and o1 series
- `ANTHROPIC`: Anthropic's Claude models including Claude 3.5 series
- `GOOGLE`: Google's Gemini models including 1.5 Pro/Flash
- `GROK`: xAI's Grok conversational AI models
- `GROQ`: Hardware-accelerated inference platform with Llama and Mixtral
- `REPLICATE`: Cloud platform for running ML models
- `HUGGINGFACE`: Hugging Face model hub
- `LOCAL_LLM`: Local language model deployment

### PersonaType
AI persona types for specialized assistance:
- `DEVELOPER`: General software development assistance
- `ARCHITECT`: System design and architecture guidance
- `REVIEWER`: Code review and quality assurance
- `SECURITY_ANALYST`: Security-focused analysis and recommendations
- `PERFORMANCE_EXPERT`: Performance optimization specialist
- `TESTER`: Testing strategy and implementation
- `TECHNICAL_WRITER`: Documentation and communication
- `DEVOPS_ENGINEER`: Infrastructure and deployment expertise
- `DATA_SCIENTIST`: Data analysis and machine learning
- `CUSTOM`: User-defined personas

### ModelCapability
Model capability flags:
- `TEXT_GENERATION`: Generate human-like text
- `CODE_GENERATION`: Generate and understand code
- `REASONING`: Advanced logical reasoning and problem-solving
- `VISION`: Process and understand images
- `MULTIMODAL`: Handle multiple input types (text, images, audio)
- `FUNCTION_CALLING`: Call external functions and tools
- `JSON_MODE`: Structured JSON output

## Latest AI Models (2024)

### OpenAI Models

#### GPT-4o Series
- **gpt-4o**: Advanced multimodal model with vision and reasoning (128K context)
- **gpt-4o-2024-08-06**: Latest version with improved performance
- **gpt-4o-mini**: Cost-effective variant for most tasks (128K context)
- **gpt-4o-mini-2024-07-18**: Specific stable release version

#### o1 Reasoning Models
- **o1-preview**: Advanced reasoning for complex problem-solving (128K context)
- **o1-mini**: Faster reasoning optimized for STEM tasks (128K context)

#### GPT-4 Turbo
- **gpt-4-turbo**: High-performance model with vision capabilities (128K context)

#### GPT-3.5 Turbo
- **gpt-3.5-turbo**: Fast and efficient for general tasks (16K context)

### Anthropic Models

#### Claude 3.5 Series (Latest)
- **claude-3-5-sonnet-20241022**: Latest with enhanced reasoning and coding (200K context)
- **claude-3-5-haiku-20241022**: Fast and efficient for quick tasks (200K context)

#### Claude 3 Series
- **claude-3-opus-20240229**: Most capable for complex reasoning (200K context)
- **claude-3-sonnet-20240229**: Balanced for general-purpose tasks (200K context)
- **claude-3-haiku-20240307**: Fastest for light tasks and high-volume use (200K context)

### Google Models

#### Gemini 1.5 Series
- **gemini-1.5-pro**: Most capable with massive 2M context window
- **gemini-1.5-flash**: Fast and efficient with 1M context window

#### Gemini 1.0 Series
- **gemini-1.0-pro**: Reliable for general-purpose tasks (32K context)
- **gemini-pro-vision**: Specialized for vision and multimodal tasks

### xAI Models
- **grok-beta**: Conversational AI with real-time knowledge and humor (131K context)

### Groq Models (Hardware-Accelerated)
- **llama-3.1-70b-versatile**: Ultra-fast Llama 3.1 70B inference (131K context)
- **llama-3.1-8b-instant**: Lightning-fast Llama 3.1 8B inference (131K context)
- **mixtral-8x7b-32768**: High-performance mixture of experts model (32K context)

## Model Selection Guidelines

### For Code Generation
- **Recommended**: GPT-4o, Claude-3-5-Sonnet, o1-mini
- **Fast & Cost-effective**: GPT-4o-mini, Claude-3-5-Haiku
- **Ultra-fast**: Groq models (llama-3.1-70b-versatile)

### For Complex Reasoning
- **Best**: o1-preview, Claude-3-Opus
- **Balanced**: GPT-4o, Claude-3-5-Sonnet
- **Cost-effective**: o1-mini, Claude-3-Sonnet

### For Vision Tasks
- **Best**: GPT-4o, Claude-3-5-Sonnet, Gemini-1.5-Pro
- **Specialized**: Gemini-Pro-Vision
- **Cost-effective**: GPT-4-Turbo

### For Large Context
- **Massive context**: Gemini-1.5-Pro (2M tokens), Gemini-1.5-Flash (1M tokens)
- **Large context**: All Anthropic Claude models (200K tokens)
- **Standard**: Most other models (128K+ tokens)

## Cost Optimization

### Token Cost Comparison (per 1M tokens)
- **Most economical**: Groq models ($0.05-$0.79), GPT-4o-mini ($0.15-$0.60)
- **Balanced**: Claude-3-Haiku ($0.25-$1.25), Gemini-1.5-Flash ($0.075-$0.30)
- **Premium**: o1-preview ($15-$60), Claude-3-Opus ($15-$75)

### Best Practices
1. Use mini/fast variants for simple tasks
2. Reserve premium models for complex reasoning
3. Leverage Groq for high-throughput scenarios
4. Consider context length needs vs. cost
5. Monitor token usage and set appropriate limits