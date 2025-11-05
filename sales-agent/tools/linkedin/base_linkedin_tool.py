import requests
import time
from typing import Dict, Any, Optional
from pydantic import BaseModel
from tools.base_tool import BaseTool
from tools.linkedin.rate_limiter import LinkedInRateLimiter
from config.config import config


class BaseLinkedInTool(BaseTool):
    """
    Base class for LinkedIn tools

    Supports multiple providers:
    - PhantomBuster (recommended)
    - Browser automation (advanced)
    - LinkedIn API (limited)
    """

    def __init__(self, provider: str = "phantombuster"):
        """
        Initialize LinkedIn tool

        Args:
            provider: "phantombuster", "browser", or "linkedin_api"
        """
        super().__init__()
        self.provider = provider
        self.rate_limiter = LinkedInRateLimiter()

        # Provider-specific configuration
        if provider == "phantombuster":
            self.api_key = getattr(config, "PHANTOMBUSTER_API_KEY", None)
            self.base_url = "https://api.phantombuster.com/api/v2"
        elif provider == "browser":
            # Browser automation configuration
            self.linkedin_email = getattr(config, "LINKEDIN_EMAIL", None)
            self.linkedin_password = getattr(config, "LINKEDIN_PASSWORD", None)

    def check_rate_limit(self, action_type: str) -> bool:
        """
        Check if action is within rate limits

        Args:
            action_type: Type of action to perform

        Returns:
            True if action can be performed
        """
        can_perform, reason = self.rate_limiter.can_perform_action(action_type)

        if not can_perform:
            print(f"Rate limit: {reason}")
            return False

        return True

    def wait_and_record(self, action_type: str):
        """
        Wait for rate limit delay and record action

        Args:
            action_type: Type of action performed
        """
        wait_time = self.rate_limiter.wait_if_needed(action_type)
        print(f"Waited {wait_time} seconds for safety")
        self.rate_limiter.record_action(action_type)


class PhantomBusterClient:
    """
    Client for PhantomBuster API

    Handles all PhantomBuster-specific operations
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.phantombuster.com/api/v2"
        self.headers = {
            "X-Phantombuster-Key": api_key,
            "Content-Type": "application/json"
        }

    def launch_phantom(
        self,
        phantom_id: str,
        arguments: Dict[str, Any],
        wait_for_result: bool = True
    ) -> Dict[str, Any]:
        """
        Launch a Phantom and optionally wait for results

        Args:
            phantom_id: ID of the Phantom to launch
            arguments: Arguments to pass to the Phantom
            wait_for_result: Whether to wait for completion

        Returns:
            Phantom execution result
        """
        # Launch Phantom
        url = f"{self.base_url}/phantoms/launch"
        payload = {
            "id": phantom_id,
            "argument": arguments
        }

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()

        launch_data = response.json()
        container_id = launch_data.get("containerId")

        if not wait_for_result:
            return {"status": "launched", "container_id": container_id}

        # Wait for completion
        return self.wait_for_completion(container_id)

    def wait_for_completion(
        self,
        container_id: str,
        timeout: int = 300,
        poll_interval: int = 5
    ) -> Dict[str, Any]:
        """
        Wait for Phantom to complete execution

        Args:
            container_id: Container ID from launch
            timeout: Maximum wait time in seconds
            poll_interval: Seconds between status checks

        Returns:
            Final execution result
        """
        url = f"{self.base_url}/containers/fetch"
        start_time = time.time()

        while True:
            if time.time() - start_time > timeout:
                return {"status": "timeout", "container_id": container_id}

            response = requests.get(
                url,
                headers=self.headers,
                params={"id": container_id}
            )
            response.raise_for_status()

            data = response.json()
            status = data.get("status")

            if status == "finished":
                return self.get_output(container_id)
            elif status == "error":
                return {
                    "status": "error",
                    "message": data.get("message", "Unknown error")
                }

            time.sleep(poll_interval)

    def get_output(self, container_id: str) -> Dict[str, Any]:
        """
        Get Phantom output data

        Args:
            container_id: Container ID

        Returns:
            Phantom output data
        """
        url = f"{self.base_url}/containers/fetch-output"

        response = requests.get(
            url,
            headers=self.headers,
            params={"id": container_id}
        )
        response.raise_for_status()

        return response.json()

    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """
        Get agent (Phantom) status

        Args:
            agent_id: Agent ID

        Returns:
            Agent status information
        """
        url = f"{self.base_url}/agents/fetch"

        response = requests.get(
            url,
            headers=self.headers,
            params={"id": agent_id}
        )
        response.raise_for_status()

        return response.json()
