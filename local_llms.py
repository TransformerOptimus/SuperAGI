from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    pipeline
)
from typing import Union
from local_llm_model import LocalLLM
import torch


model_path = "NousResearch/llama-2-7b-chat-hf"

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype="float16",
    bnb_4bit_use_double_quant=False,
)

tokenizer = AutoTokenizer.from_pretrained(model_path)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

model = AutoModelForCausalLM.from_pretrained(
    model_path,
    device_map="auto",
    quantization_config=bnb_config,
    low_cpu_mem_usage=True,
)

text_generation_pipeline = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer
)


def completion(
    model,
    tokenizer,
    message: Union[str, list[str]],
    max_new_tokens: int = 1000
):
    generation_config = model.generation_config
    generation_config.max_new_tokens = max_new_tokens
    generation_config.temperature = 0.9
    generation_config.top_p = 0.7
    generation_config.num_return_sequences = 1
    generation_config.pad_token_id = tokenizer.eos_token_id
    generation_config.eos_token_id = tokenizer.eos_token_id

    encoding = tokenizer(message, return_tensors="pt").to("cuda")
    with torch.inference_mode():
        outputs = model.generate(
            input_ids=encoding.input_ids,
            attention_mask=encoding.attention_mask,
            generation_config=generation_config
        )
        return tokenizer.batch_decode(outputs, skip_special_tokens=True)


def inference(payload: LocalLLM):
    generated_text = completion(
        model=model,
        tokenizer=tokenizer,
        message=payload.input_message,
    )
    return generated_text

def generate_response(input_message):
    generated_text = completion(
        model=model,
        tokenizer=tokenizer,
        message=input_message,
    )
    return generated_text