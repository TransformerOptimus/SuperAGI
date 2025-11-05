from typing import Dict, Any
from pydantic import BaseModel, Field
from tools.linkedin.base_linkedin_tool import BaseLinkedInTool, PhantomBusterClient
from config.config import config


class LinkedInMessageSchema(BaseModel):
    """Schema for LinkedIn message"""
    profile_url: str = Field(
        ...,
        description="LinkedIn profile URL of the recipient"
    )
    message: str = Field(
        ...,
        description="Message content to send"
    )
    is_inmail: bool = Field(
        default=False,
        description="Whether this is an InMail (requires LinkedIn Premium)"
    )


class LinkedInMessageTool(BaseLinkedInTool):
    """
    LinkedIn Message Tool

    Sends direct messages to LinkedIn connections or InMails to prospects
    """

    name = "linkedin_send_message"
    description = (
        "Send a message to a LinkedIn connection or InMail to a prospect. "
        "For connections: Direct message (free). For non-connections: InMail (requires Premium). "
        "Keep messages professional, personalized, and value-focused."
    )
    args_schema = LinkedInMessageSchema

    def execute(
        self,
        profile_url: str,
        message: str,
        is_inmail: bool = False
    ) -> Dict[str, Any]:
        """
        Send LinkedIn message

        Args:
            profile_url: LinkedIn profile URL
            message: Message content
            is_inmail: Whether to use InMail

        Returns:
            Dictionary with result
        """
        # Check rate limits
        if not self.check_rate_limit("message"):
            return {
                "success": False,
                "error": "Rate limit exceeded. Try again later.",
                "profile_url": profile_url
            }

        try:
            # Execute based on provider
            if self.provider == "phantombuster":
                result = self._send_via_phantombuster(
                    profile_url, message, is_inmail
                )
            elif self.provider == "browser":
                result = self._send_via_browser(
                    profile_url, message, is_inmail
                )
            else:
                result = {
                    "success": False,
                    "error": f"Provider '{self.provider}' not implemented"
                }

            # Record action if successful
            if result.get("success"):
                self.wait_and_record("message")

            return result

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "profile_url": profile_url
            }

    def _send_via_phantombuster(
        self,
        profile_url: str,
        message: str,
        is_inmail: bool
    ) -> Dict[str, Any]:
        """Send message via PhantomBuster"""

        if not self.api_key:
            return {
                "success": False,
                "error": "PhantomBuster API key not configured"
            }

        client = PhantomBusterClient(self.api_key)

        # PhantomBuster LinkedIn Message Sender arguments
        arguments = {
            "spreadsheetUrl": f"linkedin:{profile_url}",
            "message": message,
            "onlyConnections": not is_inmail,
            "numberOfMessagesPerLaunch": 1
        }

        try:
            phantom_id = getattr(
                config,
                "PHANTOMBUSTER_LINKEDIN_MESSAGE_SENDER_ID",
                None
            )

            if not phantom_id:
                return {
                    "success": False,
                    "error": "PhantomBuster Message Sender Phantom ID not configured"
                }

            result = client.launch_phantom(
                phantom_id=phantom_id,
                arguments=arguments,
                wait_for_result=True
            )

            if result.get("status") == "error":
                return {
                    "success": False,
                    "error": result.get("message", "Unknown error"),
                    "profile_url": profile_url
                }

            return {
                "success": True,
                "message": "LinkedIn message sent successfully",
                "profile_url": profile_url,
                "is_inmail": is_inmail,
                "provider": "phantombuster"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"PhantomBuster error: {str(e)}",
                "profile_url": profile_url
            }

    def _send_via_browser(
        self,
        profile_url: str,
        message: str,
        is_inmail: bool
    ) -> Dict[str, Any]:
        """Send message via browser automation"""
        return {
            "success": False,
            "error": "Browser automation not yet implemented",
            "profile_url": profile_url
        }
