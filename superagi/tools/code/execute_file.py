from typing import Type, Optional, List
import os
import subprocess
from pydantic import BaseModel, Field
from superagi.config.config import get_config
from superagi.agent.agent_prompt_builder import AgentPromptBuilder
from superagi.llms.base_llm import BaseLlm
from superagi.tools.base_tool import BaseTool

class ExecuteFileSchema(BaseModel):
    file_name: str = Field(
        ...,
        description="name of the file to be executed,Only include the file name in lowercase alphabet",
    )
class ExecuteFileTool(BaseTool):
    llm: Optional[BaseLlm] = None
    name = "ExecuteFileTool"
    description = (
        "Useful for executing code files"
    )
    args_schema: Type[ExecuteFileSchema] = ExecuteFileSchema
    goals: List[str] = []
    class Config:
        arbitrary_types_allowed = True
    def _execute(self,file_name:str):
        try:
            if not file_name.endswith(".py"):
                return "Error: Invalid file type. Only python files can be executed."
            input_root_dir = get_config('RESOURCES_INPUT_ROOT_DIR')
            output_root_dir = get_config('RESOURCES_OUTPUT_ROOT_DIR')
            final_path = None
            folder_path=None

            if input_root_dir is not None:
                input_root_dir = input_root_dir if input_root_dir.startswith("/") else os.getcwd() + "/" + input_root_dir
                input_root_dir = input_root_dir if input_root_dir.endswith("/") else input_root_dir + "/"
                final_path = input_root_dir + file_name
                folder_path = input_root_dir

            if final_path is None or not os.path.exists(final_path):
                if output_root_dir is not None:
                    output_root_dir = output_root_dir if output_root_dir.startswith(
                        "/") else os.getcwd() + "/" + output_root_dir
                    output_root_dir = output_root_dir if output_root_dir.endswith("/") else output_root_dir + "/"
                    final_path = output_root_dir + file_name
                    folder_path = output_root_dir

            if final_path is None or not os.path.exists(final_path):
                raise FileNotFoundError(f"File '{file_name}' not found.")
            
            result = subprocess.run(
                ["python", str(file_name)],
                capture_output=True,
                encoding="utf8",
                cwd=folder_path
            )
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Error: {result.stderr}"           
        except Exception as e:
            print(e)
            return f"Error executing file: {e}"