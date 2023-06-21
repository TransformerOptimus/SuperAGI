from typing import Type, Optional, List

from pydantic import BaseModel, Field
from superagi.config.config import get_config
from superagi.agent.agent_prompt_builder import AgentPromptBuilder
import os
from superagi.llms.base_llm import BaseLlm
from superagi.tools.base_tool import BaseTool
from superagi.lib.logger import logger
from superagi.models.db import connect_db
from superagi.helper.resource_helper import ResourceHelper
from superagi.helper.s3_helper import S3Helper
from sqlalchemy.orm import sessionmaker


class WriteSpecSchema(BaseModel):
    task_description: str = Field(
        ...,
        description="Specification task description.",
    )

    spec_file_name: str = Field(
        ...,
        description="Name of the file to write. Only include the file name. Don't include path."
    )

class WriteSpecTool(BaseTool):
    """
    Used to generate program specification.

    Attributes:
        llm: LLM used for specification generation.
        name : The name of tool.
        description : The description of tool.
        args_schema : The args schema.
        goals : The goals.
    """
    llm: Optional[BaseLlm] = None
    agent_id: int = None
    name = "WriteSpecTool"
    description = (
        "A tool to write the spec of a program."
    )
    args_schema: Type[WriteSpecSchema] = WriteSpecSchema
    goals: List[str] = []

    class Config:
        arbitrary_types_allowed = True
    
    def _write_spec_to_file(self, spec_content: str, spec_file_name: str) -> str:
        try:
            engine = connect_db()
            Session = sessionmaker(bind=engine)
            session = Session()

            final_path = spec_file_name
            root_dir = get_config('RESOURCES_OUTPUT_ROOT_DIR')
            if root_dir is not None:
                root_dir = root_dir if root_dir.startswith("/") else os.getcwd() + "/" + root_dir
                root_dir = root_dir if root_dir.endswith("/") else root_dir + "/"
                final_path = root_dir + spec_file_name
            else:
                final_path = os.getcwd() + "/" + spec_file_name

            try:
                with open(final_path, mode="w") as spec_file:
                    spec_file.write(spec_content)
                    
                with open(final_path, 'r') as spec_file:
                    resource = ResourceHelper.make_written_file_resource(file_name=spec_file_name,
                                                                          agent_id=self.agent_id, file=spec_file, channel="OUTPUT")
                    
                if resource is not None:
                    session.add(resource)
                    session.commit()
                    session.flush()
                    if resource.storage_type == "S3":
                        s3_helper = S3Helper()
                        s3_helper.upload_file(spec_file, path=resource.path)
                logger.info(f"Specification {spec_file_name} saved successfully")
            except Exception as err:
                session.close()
                return f"Error: {err}"
            session.close()

            return "Specification saved successfully"

        except Exception as e:
            return f"Error saving specification to file: {e}"

    def _execute(self, task_description: str, spec_file_name: str) -> str:
        """
        Execute the write_spec tool.

        Args:
            task_description : The task description.
            spec_file_name: The name of the file where the generated specification will be saved.

        Returns:
            Generated specification or error message.
        """
        try:
            prompt = """You are a super smart developer who has been asked to make a specification for a program.
        
            Your high-level goal is:
            {goals}
        
            Please keep in mind the following when creating the specification:
            1. Be super explicit about what the program should do, which features it should have, and give details about anything that might be unclear.
            2. Lay out the names of the core classes, functions, methods that will be necessary, as well as a quick comment on their purpose.
            3. List all non-standard dependencies that will have to be used.
        
            Write a specification for the following task:
            {task}
            """
            prompt = prompt.replace("{goals}", AgentPromptBuilder.add_list_items_to_string(self.goals))
            prompt = prompt.replace("{task}", task_description)
            messages = [{"role": "system", "content": prompt}]
            
            result = self.llm.chat_completion(messages, max_tokens=self.max_token_limit)
            
            # Save the specification to a file
            write_result = self._write_spec_to_file(result["content"], spec_file_name)
            if not write_result.startswith("Error"):
                return result["content"] + "Specification generated and saved successfully"
            else:
                return write_result
                
        except Exception as e:
            logger.error(e)
            return f"Error generating specification: {e}"