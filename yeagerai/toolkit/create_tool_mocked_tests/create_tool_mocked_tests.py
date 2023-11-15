"""Creates the source code of a new LangChain Tool on-the-fly and writes it into session cwd."""
import os
import re
from typing import List
from pydantic import BaseModel

from yeagerai.toolkit.yeagerai_tool import YeagerAITool

from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain import PromptTemplate, LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
from yeagerai.toolkit.create_tool_mocked_tests.create_tool_mocked_tests_master_prompt import (
    CREATE_TOOL_MOCKED_TESTS_MASTER_PROMPT,
)


class CreateToolMockedTestsAPIWrapper(BaseModel):
    session_path: str
    model_name: str
    request_timeout: int
    openai_api_key: str = os.getenv("OPENAI_API_KEY")

    def run(self, solution_sketch: str) -> str:
        # Initialize ChatOpenAI with API key and model name
        chat = ChatOpenAI(
            openai_api_key=self.openai_api_key,
            model_name=self.model_name,
            request_timeout=self.request_timeout,
        )

        # Create a PromptTemplate instance with the read template
        y_tool_master_prompt = PromptTemplate(
            input_variables=["solution_sketch"],
            template=CREATE_TOOL_MOCKED_TESTS_MASTER_PROMPT,
        )

        # Create a HumanMessagePromptTemplate instance with the master prompt
        human_message_prompt = HumanMessagePromptTemplate(prompt=y_tool_master_prompt)
        chat_prompt = ChatPromptTemplate.from_messages([human_message_prompt])

        # Create an LLMChain instance and run the command
        chain = LLMChain(llm=chat, prompt=chat_prompt)
        out = chain.run(solution_sketch)

        # Extract the name of the class from the code block
        quick_llm = OpenAI(temperature=0)
        class_name = quick_llm(
            f"Which is the name of the class that is being tested here? Return only the class_name value like a python string, without any other explanation \n {out}"
        ).replace("\n", "")

        # Parse the Python block inside the output, handling different code block formats
        code_block_pattern = re.compile(r"(```.*?```)", re.DOTALL)
        code_block = re.search(code_block_pattern, out)
        if code_block:
            code = code_block.group(1).strip()

            if code.startswith("```python"):
                code = code[9:]
            elif code.startswith("```"):
                code = code[3:]

            if code.endswith("```"):
                code = code[:-3]

            # Write the {class_name}.py file inside the user-defined session_path
            output_file = f"test_{class_name}.py"
            with open(os.path.join(self.session_path, output_file), "w") as f:
                f.write(code)
                f.close()

            return f"The file test_{class_name}.py has been written in the {self.session_path} successfully!\nHere is the source code of the {class_name} LangChain tool based on given requirements:\n{code}"

        return "Error: No code block found or class name could not be extracted."


class CreateToolMockedTestsRun(YeagerAITool):
    """Tool that adds the capability of creating the source code of other Tools on-the-fly and writing it into cwd."""

    name = "Create Tool Tests Source"
    description = """Useful for when you need to create the unit tests for a YeagerAI Tool. 
        Input should be a string that represents the solution sketch of the functionality wanted in the YeagerAI Tool,
        It should be defined earlier in the conversation.
        """
    final_answer_format = "Final answer: just return a success message saying that the file has been written successfully and the path."
    api_wrapper: CreateToolMockedTestsAPIWrapper

    def _run(self, solution_sketch: str) -> str:
        """Use the tool."""
        return self.api_wrapper.run(solution_sketch=solution_sketch)

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("GoogleSearchRun does not support async")
