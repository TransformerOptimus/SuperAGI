
from abc import ABC
from superagi.tools.base_tool import BaseToolkit, BaseTool
from typing import List
from get_video_details_tool import GetVideoDetailsTool


class YoutubeToolkit(BaseToolkit,ABC):
    name: str = "Youtube Toolkit"
    description: str = "Youtube Toolkit contains tools for youtube channel and youtube videos"

    def get_tools(self) -> List[BaseTool]:
        return [GetVideoDetailsTool()]
    
    def get_env_keys(self) -> List[str]:
        return []
