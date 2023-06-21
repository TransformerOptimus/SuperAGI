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


class CodingSchema(BaseModel):
    spec_description: str = Field(
        ...,
        description="Specification for generating tests.",
    )
class CodingTool(BaseTool):
    """
    Used to generate code.

    Attributes:
        llm: LLM used for code generation.
        name : The name of tool.
        description : The description of tool.
        args_schema : The args schema.
        goals : The goals.
    """
    llm: Optional[BaseLlm] = None
    agent_id: int = None
    name = "CodingTool"
    description = (
        "You will get instructions for code to write. You will write a very long answer. "
        "Make sure that every detail of the architecture is, in the end, implemented as code. "
        "Think step by step and reason yourself to the right decisions to make sure we get it right. "
        "You will first lay out the names of the core classes, functions, methods that will be necessary, "
        "as well as a quick comment on their purpose. Then you will output the content of each file including ALL code."
    )
    args_schema: Type[CodingSchema] = CodingSchema
    goals: List[str] = []

    class Config:
        arbitrary_types_allowed = True

        
    def _write_code_to_files(self, code_content: str) -> str:
        try:
            code_sections = code_content.split("\n[FILENAME]\n")

            for section in code_sections:
                if not section.strip():
                    continue

                lines = section.strip().split("\n")
                file_name = lines[0].strip()

                file_name = file_name[:70]  # Truncate long file names

                if len(lines) > 1 and "```" in lines[1]:
                    code = "\n".join(lines[2:-1])
                else:
                    code = "\n".join(lines[1:])

                engine = connect_db()
                Session = sessionmaker(bind=engine)
                session = Session()

                final_path = file_name
                root_dir = get_config('RESOURCES_OUTPUT_ROOT_DIR')
                if root_dir is not None:
                    root_dir = root_dir if root_dir.startswith("/") else os.getcwd() + "/" + root_dir
                    root_dir = root_dir if root_dir.endswith("/") else root_dir + "/"
                    final_path = root_dir + file_name
                else:
                    final_path = os.getcwd() + "/" + file_name

                try:
                    with open(final_path, mode="w") as code_file:
                        code_file.write(code)

                    with open(final_path, 'r') as code_file:
                        resource = ResourceHelper.make_written_file_resource(file_name=file_name,
                                                                              agent_id=self.agent_id, file=code_file, channel="OUTPUT")

                    if resource is not None:
                        session.add(resource)
                        session.commit()
                        session.flush()
                        if resource.storage_type == "S3":
                            s3_helper = S3Helper()
                            s3_helper.upload_file(code_file, path=resource.path)
                    logger.info(f"Code {file_name} saved successfully")
                except Exception as err:
                    session.close()
                    return f"Error: {err}"

                session.close()

            return "Code saved successfully"

        except Exception as e:
            return f"Error saving code to files: {e}"

    def _execute(self, spec_description: str) -> str:
        """
        Execute the code tool.

        Args:
            task_description : The task description.

        Returns:
            Generated code or error message.
        """
        try:
            prompt = """You are a super smart developer who has been asked to make a specification for a program.
        
            Your high-level goal is:
            {goals}
            
            You will get instructions for code to write.
            You will write a very long answer. Make sure that every detail of the architecture is, in the end, implemented as code.
            Make sure that every detail of the architecture is, in the end, implemented as code.
            
            Think step by step and reason yourself to the right decisions to make sure we get it right.
            You will start by laying out the names of the core classes, functions, methods that will be necessary, as well as a quick comment on their purpose.
            
            Then you will output the content of each file including ALL code.
            Each file must strictly follow a markdown code block format, where the following tokens must be replaced such that
            [FILENAME] is the lowercase file name including the file extension,
            [LANG] is the markup code block language for the code's language, and [CODE] is the code:
            ```
            [FILENAME]
            [LANG]
            [CODE]
            ```
            
            You will start with the "entrypoint" file, then go to the ones that are imported by that file, and so on.
            Please note that the code should be fully functional. No placeholders.
            
            Follow a language and framework appropriate best practice file naming convention.
            Make sure that files contain all imports, types etc. Make sure that code in different files are compatible with each other.
            Ensure to implement all code, if you are unsure, write a plausible implementation.
            Include module dependency or package manager dependency definition file.
            Before you finish, double check that all parts of the architecture is present in the files.
            
            Please generate code files based on the following specification description:
            {spec}
            """
            prompt = prompt.replace("{goals}", AgentPromptBuilder.add_list_items_to_string(self.goals))
            prompt = prompt.replace("{task}", spec_description)
            messages = [{"role": "system", "content": prompt}]
            
            result = self.llm.chat_completion(messages, max_tokens=self.max_token_limit)
            
            # Save the code to files
            save_result = self._write_code_to_files(result["content"])
            if not save_result.startswith("Error"):
                return "Code generated and saved successfully"
            else:
                return save_result

        except Exception as e:
            logger.error(e)
            return f"Error generating code: {e}"
            