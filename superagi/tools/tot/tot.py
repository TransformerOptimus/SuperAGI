from typing import Type, Optional, List
from superagi.agent.agent_prompt_builder import AgentPromptBuilder
from superagi.tools.base_tool import BaseTool
from superagi.llms.base_llm import BaseLlm
from pydantic import BaseModel, Field

class TreeOfThoughtSchema(BaseModel):
    task_description: str = Field(
        ...,
        description="Description of the problem that needs solving.",
    )


class TreeOfThoughtTool(BaseTool):
    llm: Optional[BaseLlm] = None
    name = "TreeOfThought"
    description = (
        "Solves a problem by going through the steps of the Tree of Thought process."
    )
    args_schema: Type[TreeOfThoughtSchema] = TreeOfThoughtSchema
    goals: List[str] = []

    class Config:
        arbitrary_types_allowed = True

    def _execute(self, task_description: str):
        try:
            prompt = """Given the following overall objective
            Objective:
            {goals} 

            and the following problem, `{task_description}`.

            Solve the problem by going through the steps of the Tree of Thought process:
            1. Generate multiple coherent units of text representing different aspects of the problem.
            2. Evaluate each thought's relevance, coherence, and potential effectiveness.
            3. Select the most promising thought or thoughts based on evaluation.
            4. Look ahead and predict the potential outcomes of following the selected thought.
            5. If the current path proves to be unfruitful, backtrack and reconsider previously discarded thoughts.
            6. Always take into account the overall problem context and the potential long-term effects of decisions.
            7. For complex problems, initiate a process of non-trivial planning or search.
            8. If a solution seems incorrect or suboptimal, revisit the problem, generate new thoughts, and propose a new solution.
            """
            prompt = prompt.replace("{goals}", AgentPromptBuilder.add_list_items_to_string(self.goals))
            prompt = prompt.replace("{task_description}", task_description)

            messages = [{"role": "system", "content": prompt}]
            result = self.llm.chat_completion(messages, max_tokens=self.max_token_limit)
            return result["content"]
        except Exception as e:
            print(e)
            return f"Error generating text: {e}"
