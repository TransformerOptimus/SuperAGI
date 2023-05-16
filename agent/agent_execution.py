# agent has a master prompt
# agent executes the master prompt along with long term memory
# agent can run the task queue as well with long term memory
class AgentExecution:
  def __int__(self, agent_prompt, document):
    self.state = None


  async def send_request_to_openai(self, prompt):
    try:
      openai.api_key = os.getenv("OPENAI_API_KEY")
      response = await openai.ChatCompletion.acreate(
        n=self.number_of_results,
        model=self.model,
        messages=prompt,
        temperature=self.temperature,
        max_tokens=self.max_tokens,
        top_p=self.top_p,
        frequency_penalty=self.frequency_penalty,
        presence_penalty=self.presence_penalty
      )
      return response

    except Exception as exception:
      return {"error": exception}




