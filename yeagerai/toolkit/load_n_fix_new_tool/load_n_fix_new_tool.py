"""Creates the source code of a new LangChain Tool on-the-fly and writes it into session cwd."""
import importlib.util
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
from yeagerai.toolkit.load_n_fix_new_tool.load_n_fix_new_tool_master_prompt import (
    LOAD_N_FIX_NEW_TOOL_MASTER_PROMPT,
)
from yeagerai.toolkit import YeagerAIToolkit


class LoadNFixNewToolAPIWrapper(BaseModel):
    session_path: str
    model_name: str
    request_timeout: int
    openai_api_key: str = os.getenv("OPENAI_API_KEY")
    toolkit: YeagerAIToolkit

    class Config:
        arbitrary_types_allowed = True

    def run(self, new_tool_path: str) -> str:
        # try to load the file
        try:
            with open(
                new_tool_path.strip(")").strip('"').strip(" ").strip("\n"), "r"
            ) as f:
                source_code = f.read()
                f.close()
        except FileNotFoundError as traceback:
            return f"Error: The provided path is not correct. Please try again.\n Traceback: {traceback}"

        class_name = new_tool_path.split("/")[-1].split(".")[0]

        try:
            spec = importlib.util.spec_from_file_location(class_name, new_tool_path)
            myfile = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(myfile)

            # load the imported classes into the toolkit
            class_api_wrapper = getattr(myfile, class_name + "APIWrapper")
            class_run = getattr(myfile, class_name + "Run")
            self.toolkit.register_tool(class_run(api_wrapper=class_api_wrapper()))

        except Exception as traceback:
            # Initialize ChatOpenAI with API key and model name
            chat = ChatOpenAI(
                openai_api_key=self.openai_api_key,
                model_name=self.model_name,
                request_timeout=self.request_timeout,
            )

            # Create a PromptTemplate instance with the read template
            y_tool_master_prompt = PromptTemplate(
                input_variables=["source_code", "traceback"],
                template=LOAD_N_FIX_NEW_TOOL_MASTER_PROMPT,
            )

            # Create a HumanMessagePromptTemplate instance with the master prompt
            human_message_prompt = HumanMessagePromptTemplate(
                prompt=y_tool_master_prompt
            )
            chat_prompt = ChatPromptTemplate.from_messages([human_message_prompt])

            # Create an LLMChain instance and run the command
            chain = LLMChain(llm=chat, prompt=chat_prompt)
            out = chain.predict(source_code=source_code, traceback=traceback)

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
                output_file = f"{class_name}.py"
                with open(os.path.join(self.session_path, output_file), "w") as f:
                    f.write(code)
                    f.close()

                return f"The file {class_name}.py has been improved but it was not loaded into the toolkit.\n Traceback: {traceback}"
            else:
                # Write the {class_name}.py file inside the user-defined session_path
                output_file = f"{class_name}.py"
                with open(os.path.join(self.session_path, output_file), "w") as f:
                    f.write(out)
                    f.close()
                return f"The file {class_name}.py has been improved but it was not loaded into the toolkit.\n Traceback: {traceback}"

        return f"The {class_name} tool has been loaded into your toolkit, Now you can use it as any other tool."


class LoadNFixNewToolRun(YeagerAITool):
    """Tool that adds the capability of creating the source code of other Tools on-the-fly and writing it into cwd."""

    name = "Load and Fix New Tool"
    description = """Useful for when you want to load a YeagerAITool into your toolkit. 
        Input MUST BE a string containing the path to the YeagerAITool file. Example: "/home/user/.yeagerai-sessions/session_id/class_name.py" 
        It should be defined earlier in the conversation.
        This tool is perfect for loading and executing Python scripts on local machines.
        YOU CAN NOT ANSWER: As an AI, I am unable to access files on your local machine or perform actions beyond my capabilities. Or similar sentences.
        """
    final_answer_format = """Final answer: just return the message explaining:
      if the tool still has errors but has been improved or 
      if the new tool has been loaded into the toolkit and now is available for you to use."""
    api_wrapper: LoadNFixNewToolAPIWrapper

    def _run(self, new_tool_path: str) -> str:
        """Use the tool."""
        return self.api_wrapper.run(new_tool_path=new_tool_path)

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("LoadNFixNewToolRun does not support async")
