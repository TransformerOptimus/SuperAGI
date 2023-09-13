from abc import ABC
from superagi.tools.base_tool import BaseToolkit, BaseTool, ToolConfiguration
from typing import Type, List
from superagi.tools.eva_db.db_load_tool import DbLoadTool
from superagi.tools.eva_db.db_query_tool import DbQueryTool
from superagi.types.key_type import ToolConfigKeyType


class DbToolkit(BaseToolkit, ABC):
    name: str = "Eva DB Toolkit"
    description: str = "Eva DB toolkit contains all tools related to using executing queries over underlying local database"

    def get_tools(self) -> List[BaseTool]:
        return [DbLoadTool(), DbQueryTool()]

    def get_env_keys(self) -> List[ToolConfiguration]:
        return [
            ToolConfiguration(key="EMAIL_ADDRESS", key_type=ToolConfigKeyType.STRING, is_required= False, is_secret = False),
        ]