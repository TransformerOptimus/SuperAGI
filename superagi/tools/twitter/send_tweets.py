from typing import Any, Type
from pydantic import BaseModel, Field
from superagi.tools.base_tool import BaseTool

class SendTweetsInput(BaseModel):
    event_name: str = Field(..., description="Name of the event/meeting to be scheduled, if not given craete a name depending on description.")
    description: str = Field(..., description="Description of the event/meeting to be scheduled.")
    start_date: str = Field(..., description="Start date of the event to be scheduled in format 'yyyy-mm-dd', if no value is given keep the default value as 'None'.")
    start_time: str = Field(..., description="Start time of the event to be scheduled in format 'hh:mm:ss', if no value is given keep the default value as 'None'.")
    end_date: str = Field(..., description="End Date of the event to be scheduled in format 'yyyy-mm-dd', if no value is given keep the default value as 'None'.")
    end_time: str = Field(..., description="End Time of the event to be scheduled in format 'hh:mm:ss', if no value is given keep the default value as 'None'.")
    attendees: list = Field(..., description="List of attendees email ids to be invited for the event.")
    location: str = Field(..., description="Geographical location of the event. if no value is given keep the default value as 'None'")

class SendTweetsTool(BaseTool):
    name: str = "Send Tweets Tool"
    args_schema: Type[BaseModel] = SendTweetsInput
    description: str = "Send and Schedule Tweets for your Twitter Handle"

    def _execute(self, event_name: str, description: str, attendees: list, start_date: str = 'None', start_time: str = 'None', end_date: str = 'None', end_time: str = 'None', location: str = 'None'):
        toolkit_id = self.toolkit_config.toolkit_id
        service = False
        if service["success"]:
            service = service["service"]
        else:
            return f"Kindly connect to Google Calendar"