from superagi.tools.base_tool import BaseTool
from pydantic import BaseModel, Field
from typing import Type

# You might need to define an input schema, even if it's not used.
# Check other tools to see how they do it.
class UserFeedbackToolInput(BaseModel):
    query: str = Field(..., description="A placeholder query, can be an empty string")

class UserFeedbackTool(BaseTool):
    name: str = "User Feedback"
    args_schema: Type[BaseModel] = UsersFeedbackToolInput
    description: str = "Asks the user for direct feedback or guidance."

    def _execute(self, query: str = ""):
        """
        Prompts the user for input from the console.
        """
        print("\nThe agent requires your feedback to proceed.")
        # input() pauses the program and waits for the user to type something
        user_input = input("Please provide your feedback or guidance: ")
        return f"User provided the following feedback: {user_input}"