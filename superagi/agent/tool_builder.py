import importlib
import os
from superagi.config.config import get_config
from superagi.llms.llm_model_factory import get_model
from superagi.models.tool import Tool
from superagi.models.tool_config import ToolConfig
from superagi.resource_manager.file_manager import FileManager
from superagi.tools.base_tool import BaseToolkitConfiguration
from superagi.tools.tool_response_query_manager import ToolResponseQueryManager
from superagi.helper.encyption_helper import decrypt_data, is_encrypted

class DBToolkitConfiguration(BaseToolkitConfiguration):
    session = None
    toolkit_id: int

    def __init__(self, session=None, toolkit_id=None):
        self.session = session
        self.toolkit_id = toolkit_id

    def get_tool_config(self, key: str):
        tool_config = self.session.query(ToolConfig).filter_by(key=key, toolkit_id=self.toolkit_id).first()
        if tool_config and tool_config.value:
            if is_encrypted(tool_config.value):
                return decrypt_data(tool_config.value)
            else:
                return tool_config.value
        return super().get_tool_config(key=key)

class ToolBuilder:
    def __init__(self, session, agent_id: int, agent_execution_id: int = None):
        self.session = session
        self.agent_id = agent_id
        self.agent_execution_id = agent_execution_id

    def __validate_filename(self, filename):
        """
        Validate the filename by removing the last three characters if the filename ends with ".py".

        Args:
            filename (str): The filename.

        Returns:
            str: The validated filename.
        """
        if filename.endswith(".py"):
            return filename[:-3]  # Remove the last three characters (i.e., ".py")
        return filename

    def build_tool(self, tool: Tool):
        """
        Create an object of a agent usable tool dynamically.

        Args:
            tool (Tool) : Tool object from which agent tool would be made.

        Returns:
            object: The object of the agent usable tool.
        """
        file_name = self.__validate_filename(filename=tool.file_name)

        tools_dir=""
        tool_paths = ["superagi/tools", "superagi/tools/external_tools", "superagi/tools/marketplace_tools"]
        for tool_path in tool_paths:
            if os.path.exists(os.path.join(os.getcwd(), tool_path) + '/' + tool.folder_name):
                tools_dir = tool_path
                break
        parsed_tools_dir = tools_dir.rstrip("/")
        module_name = ".".join(parsed_tools_dir.split("/") + [tool.folder_name, file_name])

        # module_name = f"superagi.tools.{folder_name}.{file_name}"

        # Load the module dynamically
        module = importlib.import_module(module_name)

        # Get the class from the loaded module
        obj_class = getattr(module, tool.class_name)

        # Create an instance of the class
        new_object = obj_class()
        new_object.toolkit_config = DBToolkitConfiguration(session=self.session, toolkit_id=tool.toolkit_id)
        return new_object

    def set_default_params_tool(self, tool, agent_config, agent_execution_config, model_api_key: str,
                                resource_summary: str = ""):
        """
        Set the default parameters for the tools.

        Args:
            tool : Tool object.
            agent_config (dict): Parsed agent configuration.
            agent_execution_config (dict): Parsed execution configuration
            agent_id (int): The ID of the agent.
            model_api_key (str): The API key of the model

        Returns:
            list: The list of tools with default parameters.
        """
        if hasattr(tool, 'goals'):
            tool.goals = agent_execution_config["goal"]
        if hasattr(tool, 'instructions'):
            tool.instructions = agent_execution_config["instruction"]
        if hasattr(tool, 'llm') and (agent_config["model"] == "gpt4" or agent_config[
            "model"] == "gpt-3.5-turbo") and tool.name != "QueryResource":
            tool.llm = get_model(model="gpt-3.5-turbo", api_key=model_api_key, temperature=0.4)
        elif hasattr(tool, 'llm'):
            tool.llm = get_model(model=agent_config["model"], api_key=model_api_key, temperature=0.4)
        if hasattr(tool, 'agent_id'):
            tool.agent_id = self.agent_id
        if hasattr(tool, 'agent_execution_id'):
            tool.agent_execution_id = self.agent_execution_id
        if hasattr(tool, 'resource_manager'):
            tool.resource_manager = FileManager(session=self.session, agent_id=self.agent_id,
                                                agent_execution_id=self.agent_execution_id)
        if hasattr(tool, 'tool_response_manager'):
            tool.tool_response_manager = ToolResponseQueryManager(session=self.session,
                                                                  agent_execution_id=self.agent_execution_id)

        if tool.name == "QueryResourceTool":
            tool.description = tool.description.replace("{summary}", resource_summary)

        return tool
