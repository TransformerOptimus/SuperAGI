import os
import re

from superagi.config.config import get_config
from superagi.helper.s3_helper import S3Helper
from superagi.lib.logger import logger
from superagi.models.agent import Agent
from superagi.models.agent_execution import AgentExecution
from superagi.models.resource import Resource
from superagi.types.storage_types import StorageType


class ResourceHelper:
    @classmethod
    def make_written_file_resource(cls, file_name: str, agent: Agent, agent_execution: AgentExecution, session):
        """
        Function to create a Resource object for a written file.

        Args:
            file_name (str): The name of the file.
            agent (Agent): Agent related to resource.
            agent_execution(AgentExecution): Agent Execution related to a resource
            session (Session): The database session.

        Returns:
            Resource: The Resource object.
        """
        storage_type = StorageType.get_storage_type(get_config("STORAGE_TYPE", StorageType.FILE.value))
        file_parts = os.path.splitext(file_name)
        if len(file_parts) <= 1:
            file_name = file_name + ".txt"
        file_extension = os.path.splitext(file_name)[1][1:]

        if file_extension in ["png", "jpg", "jpeg"]:
            file_type = "image/" + file_extension
        elif file_extension == "txt":
            file_type = "application/txt"
        else:
            file_type = "application/misc"

        if agent is not None:
            final_path = ResourceHelper.get_agent_write_resource_path(file_name, agent, agent_execution)
        else:
            final_path = ResourceHelper.get_resource_path(file_name)
        file_size = os.path.getsize(final_path)

        file_path = ResourceHelper.get_agent_write_resource_path(file_name, agent, agent_execution)

        logger.info("make_written_file_resource:", final_path)
        if StorageType.get_storage_type(get_config("STORAGE_TYPE", StorageType.FILE.value)) == StorageType.S3:
            file_path = "resources" + file_path
        existing_resource = session.query(Resource).filter_by(
            name=file_name,
            path=file_path,
            storage_type=storage_type.value,
            type=file_type,
            channel="OUTPUT",
            agent_id=agent.id,
            agent_execution_id=agent_execution.id
        ).first()

        if existing_resource:
            # Update the existing resource attributes
            existing_resource.size = file_size
            session.commit()
            session.flush()
            return existing_resource
        else:
            resource = Resource(
                name=file_name,
                path=file_path,
                storage_type=storage_type.value,
                size=file_size,
                type=file_type,
                channel="OUTPUT",
                agent_id=agent.id,
                agent_execution_id=agent_execution.id
            )
            session.add(resource)
            session.commit()
            return resource

    @staticmethod
    def _sanitize_path_component(value) -> str:
        """Make a value safe to use as one directory name.

        Path separators ("/" and "\\") and control characters (including NUL)
        become "_". Spaces are removed. The result can not move a path up or down
        the directory tree.
        """
        text = "" if value is None else str(value)
        text = text.replace(" ", "")
        return re.sub(r'[\x00-\x1f\x7f/\\]', '_', text)

    @classmethod
    def get_formatted_agent_level_path(cls, agent: Agent, path) -> object:
        formatted_agent_name = ResourceHelper._sanitize_path_component(agent.name + '_' + str(agent.id))
        return path.replace("{agent_id}", formatted_agent_name)

    @classmethod
    def get_formatted_agent_execution_level_path(cls, agent_execution: AgentExecution, path):
        formatted_agent_execution_name = ResourceHelper._sanitize_path_component(
            agent_execution.name + '_' + str(agent_execution.id))
        return path.replace("{agent_execution_id}", formatted_agent_execution_name)

    @classmethod
    def get_resource_path(cls, file_name: str):
        """Get final path of the resource.

        Args:
            file_name (str): The name of the file.
        """
        return ResourceHelper._validate_path_containment(ResourceHelper.get_root_output_dir(), file_name)

    @classmethod
    def get_root_output_dir(cls):
        """Get root dir of the resource.
        """
        root_dir = get_config('RESOURCES_OUTPUT_ROOT_DIR')

        if root_dir is not None:
            root_dir = root_dir if root_dir.startswith("/") else os.getcwd() + "/" + root_dir
            root_dir = root_dir if root_dir.endswith("/") else root_dir + "/"
        else:
            root_dir = os.getcwd() + "/"
        return root_dir

    @classmethod
    def get_root_input_dir(cls):
        """Get root dir of the resource.
        """
        root_dir = get_config('RESOURCES_INPUT_ROOT_DIR')

        if root_dir is not None:
            root_dir = root_dir if root_dir.startswith("/") else os.getcwd() + "/" + root_dir
            root_dir = root_dir if root_dir.endswith("/") else root_dir + "/"
        else:
            root_dir = os.getcwd() + "/"
        return root_dir

    @staticmethod
    def _ensure_within(base_dir: str, path: str) -> str:
        """Raise ValueError if path is not base_dir or a descendant of base_dir.

        Both paths are resolved with os.path.realpath, so symlinks are followed.
        The comparison uses os.path.commonpath, so /base2 does not match /base.
        """
        real_base = os.path.realpath(base_dir)
        real_path = os.path.realpath(path)
        try:
            inside = os.path.commonpath([real_base, real_path]) == real_base
        except ValueError:  # for example, paths on different drives
            inside = False
        if not inside:
            raise ValueError(f"Path traversal detected: {path}")
        return path

    @staticmethod
    def _validate_path_containment(root_dir: str, file_name: str) -> str:
        if not isinstance(file_name, str) or "\x00" in file_name:
            raise ValueError("Path traversal detected: invalid file name")
        final_path = os.path.abspath(root_dir + file_name)
        try:
            ResourceHelper._ensure_within(os.path.abspath(root_dir), final_path)
        except ValueError:
            raise ValueError(f"Path traversal detected: {file_name}")
        return final_path

    @staticmethod
    def _static_root_prefix(root_template: str) -> str:
        """Return the part of a root directory template before the first placeholder."""
        index = root_template.find("{")
        if index == -1:
            return root_template
        return root_template[:root_template.rfind("/", 0, index) + 1]

    @classmethod
    def _expand_root_dir(cls, root_template: str, agent: Agent, agent_execution: AgentExecution) -> str:
        """Expand the placeholders of a root directory template.

        The expanded directory must stay inside the fixed part of the template.
        """
        root_dir = root_template
        if agent is not None and "{agent_id}" in root_dir:
            root_dir = ResourceHelper.get_formatted_agent_level_path(agent, root_dir)
        if agent_execution is not None and "{agent_execution_id}" in root_dir:
            root_dir = ResourceHelper.get_formatted_agent_execution_level_path(agent_execution, root_dir)
        if root_dir != root_template:
            ResourceHelper._ensure_within(os.path.abspath(ResourceHelper._static_root_prefix(root_template)),
                                          os.path.abspath(root_dir))
        return root_dir

    @classmethod
    def get_agent_write_resource_path(cls, file_name: str, agent: Agent, agent_execution: AgentExecution):
        """Get agent resource path to write files

        Args:
            file_name (str): The name of the file.
            agent (Agent): The unique identifier of the agent.
            agent_execution (AgentExecution): The unique identifier of the agent.
        """
        root_template = ResourceHelper.get_root_output_dir()
        root_dir = ResourceHelper._expand_root_dir(root_template, agent, agent_execution)
        if agent is not None and "{agent_id}" in root_template:
            os.makedirs(os.path.dirname(root_dir), exist_ok=True)
        final_path = ResourceHelper._validate_path_containment(root_dir, file_name)
        return final_path

    @staticmethod
    def __check_file_path_exists(path):
        return (StorageType.get_storage_type(get_config("STORAGE_TYPE",
                                                        StorageType.FILE.value)) is StorageType.S3 and
                not S3Helper().check_file_exists_in_s3(path)) or (
                StorageType.get_storage_type(
                    get_config("STORAGE_TYPE", StorageType.FILE.value)) is StorageType.FILE
                and not os.path.exists(path))

    @classmethod
    def get_agent_read_resource_path(cls, file_name, agent: Agent, agent_execution: AgentExecution):
        """Get agent resource path to read files i.e. both input and output directory
            at agent level.

        Args:
            file_name (str): The name of the file.
            agent (Agent): The agent corresponding to resource.
            agent_execution (AgentExecution): The agent execution corresponding to the resource.
        """
        input_root_dir = ResourceHelper._expand_root_dir(ResourceHelper.get_root_input_dir(), agent, None)
        final_path = ResourceHelper._validate_path_containment(input_root_dir, file_name)
        output_root_dir = ResourceHelper.get_root_output_dir()
        if final_path is None or cls.__check_file_path_exists(final_path):
            if output_root_dir is not None:
                output_root_dir = ResourceHelper._expand_root_dir(output_root_dir, agent, agent_execution)
                final_path = ResourceHelper._validate_path_containment(output_root_dir, file_name)
        return final_path
