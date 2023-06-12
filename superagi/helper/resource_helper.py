from superagi.config.config import get_config
from superagi.models.resource import Resource
import os
import datetime


class ResourceHelper:

    @staticmethod
    def make_written_file_resource(file_name: str, agent_id: int, file, channel):
        path = get_config("RESOURCES_OUTPUT_ROOT_DIR")
        storage_type = get_config("STORAGE_TYPE")
        file_extension = os.path.splitext(file_name)[1][1:]

        if file_extension in ["png", "jpg", "jpeg"]:
            file_type = "image/" + file_extension
        elif file_extension == "txt":
            file_type = "application/txt"
        else:
            file_type = "application/misc"

        root_dir = get_config('RESOURCES_OUTPUT_ROOT_DIR')

        if root_dir is not None:
            root_dir = root_dir if root_dir.startswith("/") else os.getcwd() + "/" + root_dir
            root_dir = root_dir if root_dir.endswith("/") else root_dir + "/"
            final_path = root_dir + file_name
        else:
            final_path = os.getcwd() + "/" + file_name

        file_size = os.path.getsize(final_path)

        if storage_type == "S3":
            file_name_parts = file_name.split('.')
            file_name = file_name_parts[0] + '_' + str(datetime.datetime.now()).replace(' ', '').replace('.', '').replace(
                ':', '') + '.' + file_name_parts[1]
            if channel == "INPUT":
                path = 'input'
            else:
                path = 'output'

        print(path + "/" + file_name)
        resource = Resource(name=file_name, path=path + "/" + file_name, storage_type=storage_type, size=file_size,
                            type=file_type,
                            channel="OUTPUT",
                            agent_id=agent_id)
        return resource
