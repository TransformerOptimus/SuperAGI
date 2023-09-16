from mixpanel import Mixpanel
from superagi.config.config import get_config
from fastapi import APIRouter

router = APIRouter()

mp = Mixpanel("66422baf1e14332d36273c6addcf22f7")
mp.track('page_view',{})

@router.post("/get_activity/{event_name}", status_code=200)
def get_user_activity(event_name, event_properties: dict):
    """
    Track an event in Mixpanel.

    Args:
        user_id (str): The unique identifier for the user.
        event_name (str): The name of the event to track.
        event_properties (dict, optional): Additional properties for the event.

    Returns:
        bool: True if the event tracking is successful, False otherwise.
    """
    try:
        mp.track(event_name, properties=event_properties)
        return True
    except Exception as e:
        print(f"Error in event: {e}")
        return False