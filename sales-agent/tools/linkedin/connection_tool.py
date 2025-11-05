from typing import Dict, Any
from pydantic import BaseModel, Field
from tools.linkedin.base_linkedin_tool import BaseLinkedInTool, PhantomBusterClient
from config.config import config


class LinkedInConnectionSchema(BaseModel):
    """Schema for LinkedIn connection request"""
    profile_url: str = Field(
        ...,
        description="LinkedIn profile URL to connect with"
    )
    message: str = Field(
        default="",
        description="Personalized connection note (max 300 characters, optional)"
    )
    include_note: bool = Field(
        default=True,
        description="Whether to include a personalized note"
    )


class LinkedInConnectionTool(BaseLinkedInTool):
    """
    LinkedIn Connection Request Tool

    Sends personalized connection requests on LinkedIn with safety mechanisms
    to prevent account suspension.
    """

    name = "linkedin_send_connection"
    description = (
        "Send a personalized connection request on LinkedIn. "
        "Best practice: Include a personalized note mentioning how you found them "
        "or what you have in common. Keep it professional and concise (under 300 chars)."
    )
    args_schema = LinkedInConnectionSchema

    def execute(
        self,
        profile_url: str,
        message: str = "",
        include_note: bool = True
    ) -> Dict[str, Any]:
        """
        Send LinkedIn connection request

        Args:
            profile_url: LinkedIn profile URL
            message: Personalized connection note
            include_note: Whether to include note

        Returns:
            Dictionary with result
        """
        # Check rate limits
        if not self.check_rate_limit("connection_request"):
            return {
                "success": False,
                "error": "Rate limit exceeded. Try again later.",
                "profile_url": profile_url
            }

        try:
            # Validate message length
            if include_note and len(message) > 300:
                message = message[:297] + "..."

            # Execute based on provider
            if self.provider == "phantombuster":
                result = self._send_via_phantombuster(
                    profile_url, message, include_note
                )
            elif self.provider == "browser":
                result = self._send_via_browser(
                    profile_url, message, include_note
                )
            else:
                result = {
                    "success": False,
                    "error": f"Provider '{self.provider}' not implemented"
                }

            # Record action if successful
            if result.get("success"):
                self.wait_and_record("connection_request")

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
        include_note: bool
    ) -> Dict[str, Any]:
        """
        Send connection via PhantomBuster

        Uses PhantomBuster's LinkedIn Network Booster Phantom
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "PhantomBuster API key not configured"
            }

        client = PhantomBusterClient(self.api_key)

        # PhantomBuster LinkedIn Network Booster arguments
        arguments = {
            "profileUrls": [profile_url],
            "message": message if include_note else "",
            "onlySecondCircle": False,
            "numberOfAddsPerLaunch": 1
        }

        try:
            # Get Phantom ID from config
            phantom_id = getattr(
                config,
                "PHANTOMBUSTER_LINKEDIN_NETWORK_BOOSTER_ID",
                None
            )

            if not phantom_id:
                return {
                    "success": False,
                    "error": "PhantomBuster Phantom ID not configured. "
                           "Set PHANTOMBUSTER_LINKEDIN_NETWORK_BOOSTER_ID in .env"
                }

            # Launch Phantom
            result = client.launch_phantom(
                phantom_id=phantom_id,
                arguments=arguments,
                wait_for_result=True
            )

            # Parse result
            if result.get("status") == "error":
                return {
                    "success": False,
                    "error": result.get("message", "Unknown error"),
                    "profile_url": profile_url
                }

            return {
                "success": True,
                "message": "Connection request sent successfully",
                "profile_url": profile_url,
                "note_included": include_note,
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
        include_note: bool
    ) -> Dict[str, Any]:
        """
        Send connection via browser automation

        Uses Selenium/Playwright for direct LinkedIn automation
        """
        # This would require Selenium/Playwright implementation
        # Placeholder for now
        return {
            "success": False,
            "error": "Browser automation not yet implemented. Use PhantomBuster provider.",
            "profile_url": profile_url
        }
