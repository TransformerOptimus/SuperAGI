"""Creates the source code of a new LangChain Tool on-the-fly and writes it into session cwd."""
import os
import re
from typing import List
from pydantic import BaseModel

from yeagerai.toolkit.yeagerai_tool import YeagerAITool

from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate, LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
from yeagerai.toolkit.create_tool_source.create_tool_master_prompt import (
    CREATE_TOOL_MASTER_PROMPT,
)


class CreateToolSourceAPIWrapper(BaseModel):
    session_path: str
    model_name: str
    request_timeout: int
    openai_api_key: str = os.getenv("OPENAI_API_KEY")

    def run(self, solution_sketch_n_tool_tests: str) -> str:
        # Split the solution sketch and tool tests
        try:
            solution_sketch = solution_sketch_n_tool_tests.split(
                "######SPLIT_TOKEN########"
            )[0]
            tool_tests = solution_sketch_n_tool_tests.split(
                "######SPLIT_TOKEN########"
            )[1]
        except IndexError:
            return "You have not provided the split token ######SPLIT_TOKEN########, retry it providing it between the solution sketch and the tool tests."
        # Initialize ChatOpenAI with API key and model name
        chat = ChatOpenAI(
            openai_api_key=self.openai_api_key,
            model_name=self.model_name,
            request_timeout=self.request_timeout,
        )

        # Create a PromptTemplate instance with the read template
        y_tool_master_prompt = PromptTemplate(
            input_variables=["solution_sketch", "tool_tests"],
            template=CREATE_TOOL_MASTER_PROMPT,
        )

        # Create a HumanMessagePromptTemplate instance with the master prompt
        human_message_prompt = HumanMessagePromptTemplate(prompt=y_tool_master_prompt)
        chat_prompt = ChatPromptTemplate.from_messages([human_message_prompt])

        # Create an LLMChain instance and run the command
        chain = LLMChain(llm=chat, prompt=chat_prompt)
        out = chain.predict(solution_sketch=solution_sketch, tool_tests=tool_tests)

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

            # Extract the name of the class from the code block
            class_name_pattern = re.compile(r"class (\w+)\(BaseModel\):")
            class_name_match = re.search(class_name_pattern, code)
            if class_name_match:
                class_name = class_name_match.group(1)
                class_name = class_name.replace("APIWrapper", "")

                output_file = f"{class_name}.py"
                with open(os.path.join(self.session_path, output_file), "w") as f:
                    f.write(code)
                    f.close()

                return f"The file {class_name}.py has been written in the {self.session_path} successfully!\nHere is the source code of the {class_name} LangChain tool based on given requirements:\n{code}"

        return "Error: No code block found or class name could not be extracted."


class CreateToolSourceRun(YeagerAITool):
    """Tool that adds the capability of creating the source code of other Tools on-the-fly and writing it into cwd."""

    name = "Create Tool Source"
    description = """Useful for when you need to create the source code of a YeagerAITool. 
        Input MUST BE a string made of two substrings separated by a this token '######SPLIT_TOKEN########'.
        That is substring1+'######SPLIT_TOKEN########'+substring2: 
        - where substring1 represents the first string represents the solution sketch of the functionality wanted in the Tool.
        - and substring 2 is code block that contains the tool_tests. That is the unit tests already created for testing the tool. 
        Both of them should be defined earlier in the conversation.
        """
    final_answer_format = "Final answer: just return a success message saying the path where the class was written"
    api_wrapper: CreateToolSourceAPIWrapper

    def _run(self, solution_sketch_n_tool_tests: str) -> str:
        """Use the tool."""
        return self.api_wrapper.run(
            solution_sketch_n_tool_tests=solution_sketch_n_tool_tests
        )

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("GoogleSearchRun does not support async")
