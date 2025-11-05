from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from tools.linkedin.base_linkedin_tool import BaseLinkedInTool, PhantomBusterClient
from config.config import config


class LinkedInSearchSchema(BaseModel):
    """Schema for LinkedIn search"""
    keywords: Optional[str] = Field(
        None,
        description="General search keywords"
    )
    title: Optional[str] = Field(
        None,
        description="Job title to search for (e.g., 'VP of Sales')"
    )
    company: Optional[str] = Field(
        None,
        description="Company name to search within"
    )
    location: Optional[str] = Field(
        None,
        description="Geographic location (e.g., 'San Francisco Bay Area')"
    )
    industry: Optional[str] = Field(
        None,
        description="Industry filter"
    )
    limit: int = Field(
        default=25,
        description="Maximum number of results to return"
    )


class LinkedInSearchTool(BaseLinkedInTool):
    """
    LinkedIn Search Tool

    Searches LinkedIn for prospects matching specific criteria
    """

    name = "linkedin_search"
    description = (
        "Search LinkedIn for prospects. Filter by job title, company, location, "
        "and industry. Returns profile URLs and basic information."
    )
    args_schema = LinkedInSearchSchema

    def execute(
        self,
        keywords: str = None,
        title: str = None,
        company: str = None,
        location: str = None,
        industry: str = None,
        limit: int = 25
    ) -> List[Dict[str, Any]]:
        """
        Search LinkedIn for profiles

        Args:
            keywords: General keywords
            title: Job title
            company: Company name
            location: Location
            industry: Industry
            limit: Max results

        Returns:
            List of profile dictionaries
        """
        if not self.check_rate_limit("search"):
            return [{
                "error": "Rate limit exceeded. Try again later."
            }]

        try:
            if self.provider == "phantombuster":
                results = self._search_via_phantombuster(
                    keywords, title, company, location, industry, limit
                )
            elif self.provider == "browser":
                results = self._search_via_browser(
                    keywords, title, company, location, industry, limit
                )
            else:
                results = [{
                    "error": f"Provider '{self.provider}' not implemented"
                }]

            if results and not results[0].get("error"):
                self.wait_and_record("search")

            return results

        except Exception as e:
            return [{
                "error": str(e)
            }]

    def _search_via_phantombuster(
        self,
        keywords: str,
        title: str,
        company: str,
        location: str,
        industry: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Search via PhantomBuster"""

        if not self.api_key:
            return [{
                "error": "PhantomBuster API key not configured"
            }]

        client = PhantomBusterClient(self.api_key)

        # Build LinkedIn search URL
        search_params = []
        if keywords:
            search_params.append(f"keywords={keywords}")
        if title:
            search_params.append(f"title={title}")
        if company:
            search_params.append(f"company={company}")
        if location:
            search_params.append(f"location={location}")

        search_url = f"https://www.linkedin.com/search/results/people/?{'&'.join(search_params)}"

        arguments = {
            "searchUrl": search_url,
            "numberOfResultsPerSearch": limit
        }

        try:
            phantom_id = getattr(
                config,
                "PHANTOMBUSTER_LINKEDIN_SEARCH_EXPORT_ID",
                None
            )

            if not phantom_id:
                return [{
                    "error": "PhantomBuster Search Export Phantom ID not configured"
                }]

            result = client.launch_phantom(
                phantom_id=phantom_id,
                arguments=arguments,
                wait_for_result=True
            )

            if result.get("status") == "error":
                return [{
                    "error": result.get("message", "Unknown error")
                }]

            # Parse results
            output = result.get("output", [])
            profiles = []

            for item in output[:limit]:
                profiles.append({
                    "profile_url": item.get("profileUrl"),
                    "name": item.get("fullName"),
                    "title": item.get("title"),
                    "company": item.get("companyName"),
                    "location": item.get("location"),
                    "linkedin_url": item.get("profileUrl")
                })

            return profiles

        except Exception as e:
            return [{
                "error": f"PhantomBuster error: {str(e)}"
            }]

    def _search_via_browser(
        self,
        keywords: str,
        title: str,
        company: str,
        location: str,
        industry: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Search via browser automation"""
        return [{
            "error": "Browser automation not yet implemented"
        }]
