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


class WriteTestSchema(BaseModel):
    spec_description: str = Field(
        ...,
        description="Specification for generating tests.",
    )
    test_file_name: str = Field(
        ...,
        description="Name of the file to write. Only include the file name. Don't include path."
    )


class WriteTestTool(BaseTool):
    """
    Used to generate pytest unit tests based on the specification.

    Attributes:
        llm: LLM used for test generation.
        name : The name of tool.
        description : The description of tool.
        args_schema : The args schema.
        goals : The goals.
    """
    llm: Optional[BaseLlm] = None
    agent_id: int = None
    name = "WriteTestTool"
    description = (
        "You are a super smart developer using Test Driven Development to write tests according to a specification.\n"
        "Please generate tests based on the above specification. The tests should be as simple as possible, "
        "but still cover all the functionality.\n"
        "Write it in the file"
    )
    args_schema: Type[WriteTestSchema] = WriteTestSchema
    goals: List[str] = []

    class Config:
        arbitrary_types_allowed = True


        def _write_tests_to_file(self, tests_content: str, test_file_name: str) -> str:
            try:
                engine = connect_db()
                Session = sessionmaker(bind=engine)
                session = Session()

                final_path = test_file_name
                root_dir = get_config('RESOURCES_OUTPUT_ROOT_DIR')
                if root_dir is not None:
                    root_dir = root_dir if root_dir.startswith("/") else os.getcwd() + "/" + root_dir
                    root_dir = root_dir if root_dir.endswith("/") else root_dir + "/"
                    final_path = root_dir + test_file_name
                else:
                    final_path = os.getcwd() + "/" + test_file_name

                try:
                    with open(final_path, mode="w") as test_file:
                        test_file.write(tests_content)

                    with open(final_path, 'r') as test_file:
                        resource = ResourceHelper.make_written_file_resource(file_name=test_file_name,
                                                                            agent_id=self.agent_id, file=test_file, channel="OUTPUT")

                    if resource is not None:
                        session.add(resource)
                        session.commit()
                        session.flush()
                        if resource.storage_type == "S3":
                            s3_helper = S3Helper()
                            s3_helper.upload_file(test_file, path=resource.path)
                    logger.info(f"Tests {test_file_name} saved successfully")
                except Exception as err:
                    session.close()
                    return f"Error: {err}"
                session.close()

                return "Tests saved successfully"
                
            except Exception as e:
                return f"Error saving tests to file: {e}"

    def _execute(self, spec_description: str, test_file_name: str) -> str:
        """
        Execute the write_test tool.

        Args:
            spec_description : The specification description.
            test_file_name: The name of the file where the generated tests will be saved.

        Returns:
            Generated pytest unit tests or error message.
        """
        try:
            prompt = """You are a super smart developer who practices Test Driven Development for writing tests according to a specification.

            Your high-level goal is:
            {goals}

            Please generate pytest unit tests based on the following specification description:
            {spec}

            The tests should be as simple as possible, but still cover all the functionality described in the specification.
            """
            prompt = prompt.replace("{goals}", AgentPromptBuilder.add_list_items_to_string(self.goals))
            prompt = prompt.replace("{spec}", spec_description)
            messages = [{"role": "system", "content": prompt}]
            
            result = self.llm.chat_completion(messages, max_tokens=self.max_token_limit)
            
            # Save the tests to a file
            save_result = self._write_tests_to_file(result["content"], test_file_name)
            if not save_result.startswith("Error"):
                return "Tests generated and saved successfully"
            else:
                return save_result
                
        except Exception as e:
            logger.error(e)
            return f"Error generating tests: {e}"