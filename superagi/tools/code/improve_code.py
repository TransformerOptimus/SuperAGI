import re
from typing import Type, Optional, List

from pydantic import BaseModel, Field

from superagi.agent.agent_prompt_builder import AgentPromptBuilder
from superagi.helper.prompt_reader import PromptReader
from superagi.helper.token_counter import TokenCounter
from superagi.lib.logger import logger
from superagi.llms.base_llm import BaseLlm
from superagi.resource_manager.file_manager import FileManager
from superagi.tools.base_tool import BaseTool
from superagi.tools.tool_response_query_manager import ToolResponseQueryManager


class ImproveCodeSchema(BaseModel):
    code_data: str = Field(
        ...,
        description="Data generated previously by CodingTool",
    )
class ImproveCodeTool(BaseTool):
    """
    Used to improve the already generated code.

    Attributes:
        llm: LLM used for code generation.
        name : The name of the tool.
        description : The description of the tool.
        resource_manager: Manages the file resources.
    """
    llm: Optional[BaseLlm] = None
    agent_id: int = None
    name = "ImproveCodeTool"
    description = (
        "This tool improves the generated code by using the Language Learning Model (LLM)."
    )
    resource_manager: Optional[FileManager] = None
    tool_response_manager: Optional[ToolResponseQueryManager] = None
    goals: List[str] = []

    class Config:
        arbitrary_types_allowed = True

    def _execute(self) -> str:
        """
        Execute the improve code tool.

        Returns:
            Improved code or error message.
        """
        # Get all file names that the CodingTool has written
        file_names = self.resource_manager.get_files()

        # Loop through each file
        for file_name in file_names:
            print("#############################$$$$$$$$$$$$$$$$$$$$$@")
            # Read the file content
            content = self.resource_manager.read_file(file_name)

            # Generate a prompt from improve_code.txt
            prompt = PromptReader.read_tools_prompt(__file__, "improve_code.txt")

            # Combine the hint from the file, goals, and content
            prompt = prompt.replace("{goals}", AgentPromptBuilder.add_list_items_to_string(self.goals))
            prompt = prompt.replace("{content}", content)

            # Add the file content to the chat completion prompt
            prompt = prompt + "\nOriginal Code:\n```\n" + content + "\n```"

            # Use LLM to generate improved code
            result = self.llm.chat_completion([{'role': 'system', 'content': prompt}])
            improved_content = result["messages"][0]["content"]

            # Rewrite the file with the improved content
            save_result = self.resource_manager.write_file(file_name, improved_content)

            if save_result.startswith("Error"):
                return save_result

        return f"All codes improved and saved successfully in: " + " ".join(file_names)

# class ImproveCodeTool(BaseTool):
#     """
#     Tool that improves the previously written code.

#     Attributes:
#         llm: LLM used for code improvement.
#         name : The name of tool.
#         description : The description of tool.
#         args_schema : The args schema.
#         goals : The goals.
#         resource_manager: Manages the file resources
#     """
#     llm: Optional[BaseLlm] = None
#     agent_id: int = None
#     name = "ImproveCodeTool"
#     description = (
#         "You will get previously generated code. You will improve this code considering "
#         "multiple parameters like efficiency, readability, simplicity, etc. "
#         "You will first analyze the existing code structure, then revise the code to make it better. "
#         "Then you will output the content of each updated file."
#     )
#     args_schema: Type[ImproveCodeSchema] = ImproveCodeSchema
#     goals: List[str] = []
#     resource_manager: Optional[FileManager] = None
#     tool_response_manager: Optional[ToolResponseQueryManager] = None

#     class Config:
#         arbitrary_types_allowed = True

#     def _execute(self, code_data: str) -> str:
#         """
#         Execute the improve_code tool.

#         Args:
#             code_data : The initially generated code.

#         Returns:
#             The improved code with a success or error message.
#         """
#         prompt = PromptReader.read_tools_prompt(__file__, "improve_code.txt") + "\nUseful to know:\n" + PromptReader.read_tools_prompt(__file__, "generate_logic.txt")
#         prompt = prompt.replace("{goals}", AgentPromptBuilder.add_list_items_to_string(self.goals))
#         prompt = prompt.replace("{code_data}", code_data)
#         code_response = self.tool_response_manager.get_last_response("CodingTool")
#         if code_response != "":
#             prompt = prompt.replace("{code}", "Improve this code:\n" + code_response)
#         logger.info(prompt)
#         messages = [{"role": "system", "content": prompt}]

#         total_tokens = TokenCounter.count_message_tokens(messages, self.llm.get_model())
#         token_limit = TokenCounter.token_limit(self.llm.get_model())
#         result = self.llm.chat_completion(messages, max_tokens=(token_limit - total_tokens - 100))

#         # Get all filenames and corresponding code blocks
#         regex = r"(\S+?)\n```\S*\n(.+?)```"
#         matches = re.finditer(regex, result["content"], re.DOTALL)
#         print("#############@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@$$$")
#         print(matches)

#         file_names = []
#         # Overwrite each file
#         for match in matches:
#             # Get the filename
#             file_name = re.sub(r'[<>"|?*]', "", match.group(1))

#             # Get the code
#             code = match.group(2)

#             # Ensure file_name is not empty
#             if not file_name.strip():
#                 continue

#             file_names.append(file_name)
#             save_result = self.resource_manager.overwrite_file(file_name, code)
#             if save_result.startswith("Error"):
#                 return save_result

#         # Get README contents and overwrite
#         split_result = result["content"].split("```")
#         if len(split_result) > 0:
#             readme = split_result[0]
#             save_readme_result = self.resource_manager.overwrite_file("README.md", readme)
#             if save_readme_result.startswith("Error"):
#                 return save_readme_result

#         return result["content"] + "\n Codes improved and overwritten successfully in " + ", ".join(file_names)


# class ImproveCodeSchema(BaseModel):
#     code: str = Field(
#         ..., description="The generated code to be improved"
#     )

# class ImproveCodeTool(BaseTool):
#     name = "ImproveCodeTool"
#     agent_id: int = None
#     description = (
#         "Code improvement tool. This tool checks if anything is missing or wrong in the generated code "
#         "and modifies the contents of the files stored in the resource manager accordingly." 
#         "It should be invoked everytime after code is generated by coding tool"
#     )
#     args_schema: Type[ImproveCodeSchema] = ImproveCodeSchema
#     goals: List[str] = []
#     resource_manager: Optional[FileManager] = None
#     tool_response_manager: Optional[ToolResponseQueryManager] = None
#     llm: Optional[BaseLlm] = None

#     class Config:
#         arbitrary_types_allowed = True

#     def _execute(self, code: str) -> str:
        
#         # Getting the response from the last run of "CodingTool"
#         # code_response = self.tool_response_manager.get_last_response("CodingTool")
        
#         # # If there is a previous response from "CodingTool" then use it for the new prompt
#         # if code_response != "":
#         #     prompt = PromptReader.read_tools_prompt(__file__, "improve_code.txt")
#         #     prompt = prompt.replace("{code}", code_response)
        

#         # messages = [{"role": "system", "content": prompt}]
#         prompt = PromptReader.read_tools_prompt(__file__, "improve_code.txt")
#         code_response = self.tool_response_manager.get_last_response("CodingTool")
#         print("###################$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$################################## CodingToolResponse")
#         print(code_response)
#         if code_response != "":
#             prompt = prompt.replace("{code}", "Improve this code and fill any missing function:\n" + code_response)
#         logger.info(prompt)
#         messages = [{"role": "system", "content": prompt}]

#         total_tokens = TokenCounter.count_message_tokens(messages, self.llm.get_model())
#         token_limit = TokenCounter.token_limit(self.llm.get_model())
#         improved_code_result = self.llm.chat_completion(messages, max_tokens=(token_limit - total_tokens - 100))

#         improved_code = improved_code_result["content"]

#         # Get all filenames and corresponding code blocks
#         regex = r"(\S+?)\n```\S*\n(.+?)```"
#         matches = re.finditer(regex, improved_code, re.DOTALL)

#         file_names = []
#         for match in matches:
#             print("@@@@@@@@@@@@@@@@@@@@@@@@###############################$$$$$$$$$$$$$$$$$$$$$$$$$$$$$____GOT IN THE FILE")
#             file_name = re.sub(r'[<>"|?*]', "", match.group(1))
#             print(f"############################   FILE NAME ################################### {file_name}")
#             improved_code_part = match.group(2)

#             if not file_name.strip():
#                 continue

#             file_names.append(file_name)
#             self.resource_manager.write_file(file_name, improved_code_part)

#         return "Successfully improved the below files: \n" + "\n".join(file_names) if file_names else "No files improved."