from sqlalchemy.orm import Session

from superagi.helper.resource_helper import ResourceHelper
from superagi.helper.s3_helper import S3Helper
from superagi.lib.logger import logger


class ResourceManager:
    def __init__(self, session: Session):
        self.session = session

    def write_binary_file(self, file_name: str, data):
        final_path = ResourceHelper.get_resource_path(file_name)

        try:
            with open(final_path, mode="wb") as img:
                img.write(data)
                img.close()
            self.write_to_s3(file_name, final_path)
            logger.info(f"Binary {file_name} saved successfully")
        except Exception as err:
            return f"Error: {err}"

    def write_to_s3(self, file_name, final_path):
        with open(final_path, 'rb') as img:
            resource = ResourceHelper.make_written_file_resource(file_name=file_name,
                                                                 agent_id=self.agent_id, channel="OUTPUT")
            if resource is not None:
                self.session.add(resource)
                self.session.commit()
                self.session.flush()
                if resource.storage_type == "S3":
                    s3_helper = S3Helper()
                    s3_helper.upload_file(img, path=resource.path)

    def write_file(self, file_name: str, content):
        final_path = ResourceHelper.get_resource_path(file_name)

        try:
            with open(final_path, mode="w") as file:
                file.write(content)
                file.close()
            self.write_to_s3(file_name, final_path)
            logger.info(f"{file_name} saved successfully")
        except Exception as err:
            return f"Error: {err}"