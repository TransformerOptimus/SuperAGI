from typing import Type, Optional
import base64
import os

from pydantic import BaseModel, Field

from superagi.helper.prompt_reader import PromptReader
from superagi.helper.resource_helper import ResourceHelper
from superagi.resource_manager.file_manager import FileManager
from superagi.tools.base_tool import BaseTool
from superagi.tools.tool_response_query_manager import ToolResponseQueryManager
from superagi.llms.base_llm import BaseLlm
from superagi.models.agent import Agent
from superagi.models.agent_execution import AgentExecution


class WriteFileInput(BaseModel):
    """Input for CopyFileTool."""
    file_name: str = Field(..., description="Name of the file to write. Only include the file name. Don't include path.")
    content: str = Field(..., description="File content to write")

class WriteFileTool(BaseTool):
    """
    Write File tool

    Attributes:
        name : The name.
        description : The description.
        agent_id: The agent id.
        args_schema : The args schema.
        resource_manager: File resource manager.
    """
    llm: Optional[BaseLlm] = None
    name: str = "Write File"
    args_schema: Type[BaseModel] = WriteFileInput
    description: str = "Writes content in a file. The content can carry text and images."
    resource_manager: Optional[FileManager] = None
    agent_id:int =None
    agent_execution_id:int =None
    class Config:
        arbitrary_types_allowed = True

    def _execute(self, file_name: str, content: str):
        """
        Execute the write file tool.

        Args:
            file_name : The name of the file to write.
            content : The text to write to the file.

        Returns:
            success message if message is file written successfully or failure message if writing file fails.
        """
        
        attached_files = self._get_attached_files()
        file_type = file_name.split('.')[-1].lower()
        
        if file_type not in ['pdf', 'docx', 'doc']:
            return self.resource_manager.write_file(file_name, content)
        
        html_code_content = self._convert_content_into_html(content=content, attached_files = attached_files,formated_for=file_type)
        
        return self.resource_manager.write_file(file_name, html_code_content)

    def _convert_content_into_html(self, content: str, attached_files: list, formated_for: str) -> str:
        """
        Converts the content into an HTML file
        Args:
            content (str): Content to be beautified and formatted
            formated_for (str): HTML content to be specifically formatted for a specific document type
        Returns:
            HTML Code (str): HTML code of the formated content 
        """
        prompt = PromptReader.read_tools_prompt(__file__, "content_to_html_prompt.txt")
        prompt = prompt.replace("{content}", content)

        if image_file_paths := self._get_file_path_of_images(attached_files=attached_files):
            embedding_image_prompt = PromptReader.read_tools_prompt(__file__, "add_images_to_html.txt")
            for idx, image_path in enumerate(image_file_paths):
                embedding_image_prompt += f"\n{idx+1}. {image_path}"
            prompt = prompt.replace("{embedding_image}", embedding_image_prompt)
        else:
            prompt = prompt.replace("{embedding_image}", "")
            
        messages = [{"role": "system", "content": prompt}]
        result = self.llm.chat_completion(messages, max_tokens=self.max_token_limit)
        
        if formated_for == 'pdf':
            return self._html_formatting_for_pdf(content=result["content"], image_list=image_file_paths)
        return result['content']
    
    def _get_file_path_of_images(self, attached_files: list):
        """
        Filters Images from the attached files list and finds out the corresponding paths. 

        Args:
            attached_files: List of names of files generated

        Returns:
            Full paths of the image files
        """
        image_extensions, image_paths = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'],[]
        for file_name in attached_files:
            path = ResourceHelper().get_agent_read_resource_path(
                    file_name,
                    agent=Agent.get_agent_from_id(self.toolkit_config.session, self.agent_id),
                    agent_execution=AgentExecution.get_agent_execution_from_id(
                        self.toolkit_config.session, self.agent_execution_id
                    ),
                )
            if not os.path.exists(path):
                continue
            _, file_extension = os.path.splitext(path)
            # Check if the file extension is in the list of image extensions
            if file_extension.lower() in image_extensions:
                image_paths.append(path)
        return image_paths
    
    
    def _image_to_base64(self, image_path):
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
        return encoded_image
    
    def _html_formatting_for_pdf(self, content: str, image_list: list) -> str:
        """
        Converts image paths into base64 inputs in an HTML file
        Args:
            content (str): HTML code
            image_list (list): List of images to be converted and replaced
        Returns:
            HTML Code (str): Formatted HTML code 
        """
        
        for image_path in image_list:
            content = content.replace(f"{image_path}", f"data:image/png;base64,{self._image_to_base64(image_path=image_path)}")
        return content

    def _get_attached_files(self):
        output_directory = ResourceHelper.get_root_output_dir()
        if "{agent_id}" not in output_directory:
            return []
        output_directory = ResourceHelper.get_formatted_agent_level_path(agent=Agent
                                                                        .get_agent_from_id(session=self
                                                                                           .toolkit_config.session,
                                                                                           agent_id=self.agent_id),
                                                                        path=output_directory)
        agent_execution=AgentExecution.get_agent_execution_from_id(session=self.toolkit_config.session, agent_execution_id=self.agent_execution_id)
        if agent_execution is not None and "{agent_execution_id}" in output_directory:
            output_directory = ResourceHelper.get_formatted_agent_execution_level_path(agent_execution=agent_execution, path=output_directory)

        return self._list_files(output_directory)
    
    def _list_files(self, directory):
        found_files = []
        for root, dirs, files in os.walk(directory):
            found_files.extend(
                file
                for file in files
                if not file.startswith(".") and "__pycache__" not in root
            )
        return found_files