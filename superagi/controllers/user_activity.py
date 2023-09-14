import mixpanel
from superagi.config.config import get_config

router = APIRouter()

mp = Mixpanel(get_config("MIXPANEL_KEY"))

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