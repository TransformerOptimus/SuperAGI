from typing import Dict, Any, List
from pydantic import BaseModel, Field
from tools.linkedin.base_linkedin_tool import BaseLinkedInTool, PhantomBusterClient
from config.config import config


class LinkedInVisitSchema(BaseModel):
    """Schema for LinkedIn profile visit"""
    profile_url: str = Field(
        ...,
        description="LinkedIn profile URL to visit"
    )


class LinkedInProfileVisitTool(BaseLinkedInTool):
    """
    LinkedIn Profile Visit Tool

    Visits LinkedIn profiles to increase visibility and warm up prospects
    before connection requests
    """

    name = "linkedin_visit_profile"
    description = (
        "Visit a LinkedIn profile to increase visibility. "
        "This creates a 'who viewed your profile' notification for the prospect, "
        "which can warm them up before a connection request."
    )
    args_schema = LinkedInVisitSchema

    def execute(self, profile_url: str) -> Dict[str, Any]:
        """
        Visit LinkedIn profile

        Args:
            profile_url: LinkedIn profile URL

        Returns:
            Dictionary with result
        """
        if not self.check_rate_limit("profile_visit"):
            return {
                "success": False,
                "error": "Rate limit exceeded. Try again later.",
                "profile_url": profile_url
            }

        try:
            if self.provider == "phantombuster":
                result = self._visit_via_phantombuster(profile_url)
            elif self.provider == "browser":
                result = self._visit_via_browser(profile_url)
            else:
                result = {
                    "success": False,
                    "error": f"Provider '{self.provider}' not implemented"
                }

            if result.get("success"):
                self.wait_and_record("profile_visit")

            return result

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "profile_url": profile_url
            }

    def _visit_via_phantombuster(self, profile_url: str) -> Dict[str, Any]:
        """Visit profile via PhantomBuster"""

        if not self.api_key:
            return {
                "success": False,
                "error": "PhantomBuster API key not configured"
            }

        client = PhantomBusterClient(self.api_key)

        arguments = {
            "spreadsheetUrl": f"linkedin:{profile_url}",
            "numberOfProfilesPerLaunch": 1
        }

        try:
            phantom_id = getattr(
                config,
                "PHANTOMBUSTER_LINKEDIN_PROFILE_VISITOR_ID",
                None
            )

            if not phantom_id:
                return {
                    "success": False,
                    "error": "PhantomBuster Profile Visitor Phantom ID not configured"
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
                "message": "Profile visited successfully",
                "profile_url": profile_url,
                "provider": "phantombuster"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"PhantomBuster error: {str(e)}",
                "profile_url": profile_url
            }

    def _visit_via_browser(self, profile_url: str) -> Dict[str, Any]:
        """Visit profile via browser automation"""
        return {
            "success": False,
            "error": "Browser automation not yet implemented",
            "profile_url": profile_url
        }
