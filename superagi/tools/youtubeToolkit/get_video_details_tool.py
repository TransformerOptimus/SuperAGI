from json import dump
from typing import Type
from pydantic import BaseModel, Field
from superagi.tools.base_tool import BaseTool
import googleapiclient.discovery
from config import YT_DATA_API_KEY,VIDEO_DETAILS_PARTS,API_VERSION

class GetVideoDetailsInput(BaseModel):
    video_id : str = Field(...,description = "The id of the youtube video.")
    parts : str = Field(VIDEO_DETAILS_PARTS,description = "Specifies a comma-separated list of one or more channel resource properties that the API response will include..")
    max_results : str = Field(5,description= "The maximum number of items to be retrieved. Value should be between 0 to 50")

class GetVideoDetailsTool(BaseTool):
    """
    Retrieves video details from youtube API

    Attributes:
        name : The name of the tool.
        description : The description of the tool.
        args_schema : The args schema.
    """
    name: str = "Get Video Details"
    args_schema: Type[BaseModel] = GetVideoDetailsInput
    description: str = "Retrieves video details from youtube API"

    def _execute(self,video_id : str,parts = VIDEO_DETAILS_PARTS,max_results = 5) -> dict:
        """
        Retrieves video details from youtube API

        Args:
            video_id : The id of the youtube video.
            parts : specifies a comma-separated list of one or more channel resource properties that the API response will 
                    include.Defaults to VIDEO_DETAILS_PARTS.
            max_results: The maximum number of items to be retrieved. Value should be 0 to 50, Defaults to 5.
        
        """
        if(type(parts) == list):
            parts = ",".join(parts)
        
        youtube_obj = googleapiclient.discovery.build("youtube",API_VERSION, developerKey=YT_DATA_API_KEY)
        
        req = youtube_obj.videos().list(
                    part = parts,
                    id = video_id,
                    maxResults = max_results
        )

        res = req.execute()

        return res
       



