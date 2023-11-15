"""Creates the source code of a new LangChain Tool on-the-fly and writes it into session cwd."""
import os

from pydantic import BaseModel

from yeagerai.toolkit.yeagerai_tool import YeagerAITool

from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate, LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
from yeagerai.toolkit.design_solution_sketch.design_solution_sketch_master_prompt import (
    DESIGN_SOLUTION_SKETCH_MASTER_PROMPT,
)


class DesignSolutionSketchAPIWrapper(BaseModel):
    session_path: str
    model_name: str
    request_timeout: int
    openai_api_key: str = os.getenv("OPENAI_API_KEY")

    def run(self, tool_description_prompt: str) -> str:
        # Initialize ChatOpenAI with API key and model name
        chat = ChatOpenAI(
            openai_api_key=self.openai_api_key,
            model_name=self.model_name,
            request_timeout=self.request_timeout,
        )

        # Create a PromptTemplate instance with the read template
        y_tool_master_prompt = PromptTemplate(
            input_variables=["tool_description_prompt"],
            template=DESIGN_SOLUTION_SKETCH_MASTER_PROMPT,
        )

        # Create a HumanMessagePromptTemplate instance with the master prompt
        human_message_prompt = HumanMessagePromptTemplate(prompt=y_tool_master_prompt)
        chat_prompt = ChatPromptTemplate.from_messages([human_message_prompt])

        # Create an LLMChain instance and run the command
        chain = LLMChain(llm=chat, prompt=chat_prompt)
        out = chain.run(tool_description_prompt)

        return f"Here is the solution sketch of the YeagerAI tool that you described based on your requirements:\n{out}"


class DesignSolutionSketchRun(YeagerAITool):
    """Tool that adds the capability of creating the source code of other Tools on-the-fly and writing it into cwd."""

    name = "Design Tool Solution Sketch"
    description = """Useful for when you need to create the solution sketch of a YeagerAITool. 
        Input should be one string, that contains a brief description of the functionality wanted in the Tool.
        The goal of this tool is augment this brief description converting it into a solution sketch.
        """
    final_answer_format = "Final answer: just return a message just saying that the solution sketch was created."
    api_wrapper: DesignSolutionSketchAPIWrapper

    def _run(self, tool_description_prompt: str) -> str:
        """Use the tool."""
        return self.api_wrapper.run(tool_description_prompt=tool_description_prompt)

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("GoogleSearchRun does not support async")
