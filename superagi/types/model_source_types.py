from enum import Enum


class ModelSourceType(Enum):
    GooglePalm = 'Google Palm'
    OpenAI = 'OpenAi'
    Replicate = 'Replicate'
    HuggingFace = 'Hugging Face'
    LocalLLM = 'Local LLM'
    Anthropic = 'Anthropic'  # Added support for Anthropic Claude models
    Grok = 'Grok'  # xAI's Grok conversational AI models
    Groq = 'Groq'  # Hardware-accelerated inference provider

    @classmethod
    def get_model_source_type(cls, name):
        name = name.upper().replace(" ", "")
        for member in cls.__members__:
            if name == member.upper():
                return cls[member]
        raise ValueError(f"{name} is not a valid vector store name.")

    @classmethod
    def get_model_source_from_model(cls, model_name: str):
        # Updated OpenAI models list to include latest GPT-4 and GPT-3.5 variants as of 2024
        open_ai_models = [
            # GPT-4 models
            'gpt-4', 'gpt-4-32k', 'gpt-4-0125-preview', 'gpt-4-1106-preview',
            'gpt-4-turbo', 'gpt-4-turbo-2024-04-09', 'gpt-4-turbo-preview', 
            'gpt-4o', 'gpt-4o-2024-08-06', 'gpt-4o-mini', 'gpt-4o-mini-2024-07-18',
            # New reasoning models
            'o1-preview', 'o1-mini',
            # GPT-3.5 models
            'gpt-3.5-turbo', 'gpt-3.5-turbo-16k', 'gpt-3.5-turbo-0125', 
            'gpt-3.5-turbo-1106', 'gpt-3.5-turbo-instruct'
        ]
        # Updated Google models to include latest Gemini models (removing legacy PaLM)
        google_models = [
            # Latest Gemini models (primary)
            'gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-1.0-pro', 
            'gemini-pro', 'gemini-pro-vision',
            # Model API format variants
            'models/gemini-1.5-pro', 'models/gemini-1.5-flash', 'models/gemini-1.0-pro',
            'models/gemini-pro', 'models/gemini-pro-vision',
            # Legacy PaLM models (for backward compatibility)
            'google-palm-bison-001', 'models/chat-bison-001', 'models/text-bison-001'
        ]
        # Updated Replicate models with latest LLaMA and CodeLLaMA variants
        replicate_models = [
            # Latest LLaMA models
            'meta/llama-2-70b-chat', 'meta/llama-2-13b-chat', 'meta/llama-2-7b-chat',
            'meta/codellama-70b-instruct', 'meta/codellama-34b-instruct', 'meta/codellama-13b-instruct',
            # Legacy model identifiers (for backward compatibility)
            'replicate-llama13b-v2-chat', 'llama-2-70b-chat', 'llama-2-13b-chat', 'llama-2-7b-chat',
            'codellama-34b-instruct', 'codellama-13b-instruct'
        ]
        # Updated Anthropic Claude models with latest releases
        anthropic_models = [
            # Claude 3.5 series (latest)
            'claude-3-5-sonnet-20241022', 'claude-3-5-sonnet-20240620', 'claude-3-5-haiku-20241022',
            # Claude 3 series
            'claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307',
            # Claude 2 series (legacy)
            'claude-2.1', 'claude-2.0', 'claude-instant-1.2'
        ]
        # xAI Grok models
        grok_models = [
            'grok-beta', 'grok-1'
        ]
        # Groq hardware-accelerated models
        groq_models = [
            # Llama models on Groq
            'llama-3.1-70b-versatile', 'llama-3.1-8b-instant', 'llama-3-70b-8192', 'llama-3-8b-8192',
            # Mixtral models on Groq
            'mixtral-8x7b-32768', 'gemma-7b-it'
        ]
        if model_name in open_ai_models:
            return ModelSourceType.OpenAI
        if model_name in google_models:
            return ModelSourceType.GooglePalm
        if model_name in replicate_models:
            return ModelSourceType.Replicate
        if model_name in anthropic_models:
            return ModelSourceType.Anthropic
        if model_name in grok_models:
            return ModelSourceType.Grok
        if model_name in groq_models:
            return ModelSourceType.Groq
        return ModelSourceType.OpenAI

    def __str__(self):
        return self.value