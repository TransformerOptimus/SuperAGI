import os
import json

import openai

class OpenAi:
  def __init__(self, model="gpt-4", temperature=0.3, max_tokens=3600, top_p=1, frequency_penalty=0,
               presence_penalty=0, number_of_results=1):
    self.model = model
    self.temperature = temperature
    self.max_tokens = max_tokens
    self.top_p = top_p
    self.frequency_penalty = frequency_penalty
    self.presence_penalty = presence_penalty
    self.number_of_results = number_of_results


  async def chat_completion(self, prompt,role):
    try:
      openai.api_key = os.getenv("OPENAI_API_KEY")
      content = [{"role": role, "content": prompt}]
      response = await openai.ChatCompletion.acreate(
        n=self.number_of_results,
        model=self.model,
        messages=content,
        temperature=self.temperature,
        max_tokens=self.max_tokens,
        top_p=self.top_p,
        frequency_penalty=self.frequency_penalty,
        presence_penalty=self.presence_penalty
      )

      return json.dumps(response)

    except Exception as exception:
      return {"error": exception}
  
  def chat_completion_sync(self, prompt,role):
      """Generates text using the OpenGPT API in sync manner.

      Args:
          prompt: The prompt text.

      Returns:
          The generated text.
      """
      try:
          content = [{"role": role, "content": prompt}]
          response = openai.ChatCompletion.create(
              n=self.number_of_results,
              model=self.model,
              messages=content,
              temperature=self.temperature,
              max_tokens=self.max_tokens,
              top_p=self.top_p,
              frequency_penalty=self.frequency_penalty,
              presence_penalty=self.presence_penalty,
              api_key=os.getenv("OPENAI_API_KEY")
          )
          return json.dumps(response)
      except Exception as exception:
          return {"error":exception}
