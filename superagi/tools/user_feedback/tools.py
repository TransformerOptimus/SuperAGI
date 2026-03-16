from typing import Type, Optional
from pydantic import BaseModel, Field
from superagi.tools.base_tool import BaseTool
from superagi.lib.logger import logger


class UserFeedbackSchema(BaseModel):
    question: str = Field(
        ...,
        description="The question or prompt to ask the user for feedback/input.",
    )
    context: str = Field(
        default="",
        description="Additional context about why this feedback is needed.",
    )


class UserFeedbackTool(BaseTool):
    """
    UserFeedback tool allows the agent to pause and request input from the user.

    Attributes:
        name: The name of the tool.
        description: Description of when and how to use this tool.
        args_schema: The schema for tool arguments.
        permission_required: Whether user permission is needed to execute.
    """
    name = "UserFeedbackTool"
    description = (
        "Request feedback or additional information from the user. "
        "Use this tool when you need clarification, confirmation, or additional "
        "details that cannot be determined from the available context. "
        "Best for: decision points, ambiguous requirements, or safety-critical actions."
    )
    args_schema: Type[UserFeedbackSchema] = UserFeedbackSchema
    permission_required: bool = False

    class Config:
        arbitrary_types_allowed = True

    def _execute(self, question: str, context: str = "") -> str:
        """
        Execute the UserFeedback tool.

        Args:
            question: The question to ask the user.
            context: Additional context for why feedback is needed.

        Returns:
            The user's response or a timeout message.
        """
        try:
            # Format the feedback request
            if context:
                feedback_msg = f"[User Feedback Requested]
Context: {context}
Question: {question}"
            else:
                feedback_msg = f"[User Feedback Requested]
Question: {question}"

            # Log the feedback request
            logger.info(f"UserFeedbackTool: Requesting user input - {question}")

            # Return the formatted message for the agent execution feed
            # The SuperAGI framework will handle presenting this to the user
            # and capturing their response
            return (
                f"{feedback_msg}

"
                "Status: Awaiting user response. "
                "The agent has paused for user input at this decision point."
            )

        except Exception as e:
            logger.error(f"UserFeedbackTool error: {e}")
            return f"Error requesting user feedback: {e}"
