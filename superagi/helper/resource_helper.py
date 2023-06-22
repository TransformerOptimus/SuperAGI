from superagi.config.config import get_config
from superagi.models.resource import Resource
import os
import datetime
from superagi.lib.logger import logger


class ResourceHelper:

    @staticmethod
    def make_written_file_resource(file_name: str, agent_id: int, channel: str):
        """
        Function to create a Resource object for a written file.

        Args:
            file_name (str): The name of the file.
            agent_id (int): The ID of the agent.
            channel (str): The channel of the file.

        Returns:
            Resource: The Resource object.
        """
        path = ResourceHelper.get_root_dir()
        storage_type = get_config("STORAGE_TYPE")
        file_extension = os.path.splitext(file_name)[1][1:]

        if file_extension in ["png", "jpg", "jpeg"]:
            file_type = "image/" + file_extension
        elif file_extension == "txt":
            file_type = "application/txt"
        else:
            file_type = "application/misc"

        if agent_id is not None:
            final_path = ResourceHelper.get_agent_resource_path(file_name, agent_id)
            path = path + str(agent_id) + "/"
        else:
            final_path = ResourceHelper.get_resource_path(file_name)
        file_size = os.path.getsize(final_path)

        if storage_type == "S3":
            file_name_parts = file_name.split('.')
            file_name = file_name_parts[0] + '_' + str(datetime.datetime.now()).replace(' ', '') \
                .replace('.', '').replace(':', '') + '.' + file_name_parts[1]
            path = 'input/' if (channel == "INPUT") else 'output/'

        logger.info(final_path)
        resource = Resource(name=file_name, path=path + file_name, storage_type=storage_type, size=file_size,
                            type=file_type,
                            channel="OUTPUT",
                            agent_id=agent_id)
        return resource

    @staticmethod
    def get_resource_path(file_name: str):
        """Get final path of the resource.

        Args:
            file_name (str): The name of the file.
        """
        return ResourceHelper.get_root_dir() + file_name

    @staticmethod
    def get_root_dir():
        """Get root dir of the resource.
        """
        root_dir = get_config('RESOURCES_OUTPUT_ROOT_DIR')

        if root_dir is not None:
            root_dir = root_dir if root_dir.startswith("/") else os.getcwd() + "/" + root_dir
            root_dir = root_dir if root_dir.endswith("/") else root_dir + "/"
        else:
            root_dir = os.getcwd() + "/"
        return root_dir

    @staticmethod
    def get_agent_resource_path(file_name: str, agent_id: int):
        """Get agent resource path

        Args:
            file_name (str): The name of the file.
        """
        root_dir = ResourceHelper.get_root_dir()
        if agent_id is not None:
            directory = os.path.dirname(root_dir + str(agent_id) + "/")
            os.makedirs(directory, exist_ok=True)
            root_dir = root_dir + str(agent_id) + "/"
        final_path = root_dir + file_name
        return final_path
