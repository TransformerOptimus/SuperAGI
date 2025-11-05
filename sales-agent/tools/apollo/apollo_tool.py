import json
import requests
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from tools.base_tool import BaseTool
from config.config import config


class ApolloSearchSchema(BaseModel):
    """Schema for Apollo search arguments"""
    person_titles: List[str] = Field(
        ...,
        description="The titles of the people to search for (e.g., 'VP of Sales', 'CEO')"
    )
    page: int = Field(
        default=1,
        description="The page of results to retrieve. Default value is 1."
    )
    per_page: int = Field(
        default=25,
        description="The number of results to retrieve per page (max 100). Default value is 25."
    )
    num_of_employees: List[int] = Field(
        default_factory=list,
        description="The number of employees to filter by in format [start_range, end_range]. Example: [50, 500]"
    )
    organization_domains: str = Field(
        default="",
        description="The organization domains to search within (e.g., 'acme.com'). Optional."
    )
    person_location: str = Field(
        default="",
        description="Region country/state/city filter (e.g., 'United States', 'California'). Optional."
    )


class ApolloTool(BaseTool):
    """
    Apollo.io Search Tool for finding B2B leads

    This tool searches Apollo.io's database of 700M+ contacts to find
    qualified leads based on job titles, company size, location, and other criteria.
    """

    name = "apollo_search"
    description = (
        "Search Apollo.io database for B2B leads and prospects. "
        "Find people by job title, company size, location, and domain. "
        "Returns verified email addresses, LinkedIn profiles, and contact information."
    )
    args_schema = ApolloSearchSchema

    def execute(
        self,
        person_titles: List[str],
        page: int = 1,
        per_page: int = 25,
        num_of_employees: List[int] = None,
        person_location: str = "",
        organization_domains: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Execute Apollo search and return lead data

        Args:
            person_titles: Job titles to search for
            page: Page number for pagination
            per_page: Results per page (max 100)
            num_of_employees: Company size range [min, max]
            person_location: Geographic location filter
            organization_domains: Company domain filter

        Returns:
            List of lead dictionaries with contact information
        """
        url = "https://api.apollo.io/v1/mixed_people/search"

        headers = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache"
        }

        # Build request payload
        payload = {
            "api_key": config.APOLLO_API_KEY,
            "page": page,
            "per_page": min(per_page, 100),  # Cap at 100
            "person_titles": person_titles,
            "contact_email_status": ["verified"]  # Only verified emails
        }

        # Add optional filters
        if organization_domains:
            payload["q_organization_domains"] = organization_domains

        if num_of_employees and len(num_of_employees) == 2:
            if num_of_employees[1] == num_of_employees[0]:
                payload["organization_num_employees_ranges"] = [f"{num_of_employees[0]},"]
            else:
                payload["organization_num_employees_ranges"] = [
                    f"{num_of_employees[0]},{num_of_employees[1]}"
                ]

        if person_location:
            payload["person_locations"] = [person_location]

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()

            data = response.json()
            people_list = []

            if data and 'people' in data and len(data['people']) > 0:
                for person in data['people']:
                    # Extract organization info
                    org = person.get('organization', {})

                    people_list.append({
                        'first_name': person.get('first_name', ''),
                        'last_name': person.get('last_name', ''),
                        'name': person.get('name', ''),
                        'email': person.get('email', ''),
                        'title': person.get('title', ''),
                        'headline': person.get('headline', ''),
                        'linkedin_url': person.get('linkedin_url', ''),
                        'phone': person.get('phone_numbers', [{}])[0].get('raw_number', '') if person.get('phone_numbers') else '',
                        'location': person.get('city', ''),
                        'company': org.get('name', ''),
                        'company_domain': org.get('primary_domain', ''),
                        'company_size': org.get('estimated_num_employees', ''),
                        'industry': org.get('industry', '')
                    })

            return people_list

        except requests.exceptions.RequestException as e:
            print(f"Apollo API error: {str(e)}")
            return []
        except Exception as e:
            print(f"Error processing Apollo results: {str(e)}")
            return []
