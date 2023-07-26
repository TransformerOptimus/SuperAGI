import json
from datetime import datetime

from superagi.helper.time_helper import get_time_difference


def parse_feed(feed):
    """
    Helper function to parse the feed.

    Args:
        feed (AgentExecutionFeed): The feed to be parsed.

    Returns:
        dict: Parsed feed information with role, feed content, and updated timestamp.
              If parsing fails, the original feed is returned.
    """

    # Get the current time
    feed.time_difference = get_time_difference(feed.updated_at, str(datetime.now()))

    # Check if the feed belongs to an assistant role
    if feed.role == "assistant":
        try:
            # Parse the feed as JSON
            parsed = json.loads(feed.feed, strict=False)

            final_output = ""
            if "reasoning" in parsed["thoughts"]:
                final_output = "Thoughts: " + parsed["thoughts"]["reasoning"] + "\n"
            if "plan" in parsed["thoughts"]:
                final_output += "Plan: " + str(parsed["thoughts"]["plan"]) + "\n"
            if "criticism" in parsed["thoughts"]:
                final_output += "Criticism: " + parsed["thoughts"]["criticism"] + "\n"
            if "tool" in parsed:
                final_output += "Tool: " + parsed["tool"]["name"] + "\n"
            if "command" in parsed:
                final_output += "Tool: " + parsed["command"]["name"] + "\n"

            return {"role": "assistant", "feed": final_output, "updated_at": feed.updated_at,
                    "time_difference": feed.time_difference}
        except Exception:
            return feed

    if feed.role == "system":
        final_output = feed.feed
        if "json-schema.org" in feed.feed:
            final_output = feed.feed.split("TOOLS:")[0]
        return {"role": "system", "feed": final_output, "updated_at": feed.updated_at,
                "time_difference": feed.time_difference}

    return feed
