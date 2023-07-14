from abc import ABC
from typing import List

from superagi.tools.base_tool import BaseTool, BaseToolkit
from rabbitmq_tool import RabbitMQTool

class RabbitMQToolkit(BaseToolkit, ABC):
    name: str = "RabbitMQ Toolkit"
    description: str = "Toolkit containing tools for interacting with RabbitMQ"
    
    def get_tools(self) -> List[BaseTool]:
        return [RabbitMQTool()]

    def get_env_keys(self) -> List[str]:
        return [
            "RABBITMQ_SERVER",
            "RABBITMQ_USERNAME",
            "RABBITMQ_PASSWORD"
            # Add more config keys specific to your project
        ]
