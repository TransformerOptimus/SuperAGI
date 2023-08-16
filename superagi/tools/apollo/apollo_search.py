import json
from typing import Type

import requests
from pydantic import BaseModel, Field

from superagi.lib.logger import logger
from superagi.tools.base_tool import BaseTool


class ApolloSearchSchema(BaseModel):
    person_titles: list[str] = Field(
        ...,
        description="The titles of the people to search for.",
    )
    page: int = Field(
        1,
        description="The page of results to retrieve. Default value is 1.",
    )
    per_page: int = Field(
        25,
        description="The number of results to retrieve per page. Default value is 25.",
    )
    num_of_employees: list[int] = Field(
        [],
        description="The number of employees to filter by in format [start_range, end_range]. Default value is empty array.",
    )
    organization_domains: str = Field(
        "",
        description="The organization domains to search within. It is optional field.",
    )
    person_location: str = Field(
        "",
        description="Region country/state/city filter to search for. It is optional field.",
    )


class ApolloSearchTool(BaseTool):
    """
    Apollo Search tool

    Attributes:
        name : The name.
        description : The description.
        args_schema : The args schema.
    """
    name = "ApolloSearch"
    description = (
        "A tool for performing a Apollo search and extracting people data."
        "Input should include API key, organization domains, page number, and person titles."
    )
    args_schema: Type[BaseModel] = ApolloSearchSchema

    class Config:
        arbitrary_types_allowed = True

    def _execute(self, person_titles: list[str], page: int = 1, per_page: int = 25, num_of_employees: list[int] = [],
                 person_location: str = "", organization_domains: str = "") -> str:
        """
        Execute the Apollo search tool.

        Args:
            person_titles : The titles of the people to search for.
            page : The page of results to retrieve.
            num_of_employees : The number of employees to filter by in format [start_range, end_range]. It is optional.
            person_location : Region country/state/city filter to search for. It is optional.
            organization_domains : The organization domains to search within.

        Returns:
            People data from the Apollo search.
        """
        people_data = self.apollo_search_results(page, per_page, person_titles,
                                                 num_of_employees, person_location, organization_domains)
        logger.info(people_data)
        people_list = []
        if 'people' in people_data and len(people_data['people']) > 0:
            for person in people_data['people']:
                people_list.append({'first_name': person['first_name'],
                                    'last_name': person['last_name'],
                                    'name': person['name'],
                                    'linkedin_url': person['linkedin_url'],
                                    'email': person['email'],
                                    'headline': person['headline'],
                                    'title': person['title'],
                                    })

        return people_list

    def apollo_search_results(self, page, per_page, person_titles, num_of_employees = [],
                              person_location = "", organization_domains = ""):
        """
        Execute the Apollo search tool.

        Args:
            page : The page of results to retrieve.
            person_titles : The titles of the people to search for.
            num_of_employees : The number of employees to filter by in format [start_range, end_range]. It is optional.
            person_location: Region country/state/city filter to search for. It is optional.

        Returns:
            People data from the Apollo search.
        """
        url = "https://api.apollo.io/v1/mixed_people/search"
        headers = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache"
        }
        data = {
            "api_key": self.get_tool_config("APOLLO_SEARCH_KEY"),
            "page": page,
            "per_page": per_page,
            "person_titles": person_titles,
            "contact_email_status": ["verified"]
        }

        if organization_domains:
            data["q_organization_domains"] = organization_domains

        if num_of_employees:
            if num_of_employees[1] == num_of_employees[0]:
                data["num_of_employees"] = [str(num_of_employees[0]) + ","]
            else:
                data["num_of_employees"] = [str(num_of_employees[0]) + ","+ str(num_of_employees[1])]
        if person_location:
            data["person_locations"] = [person_location]

        response = requests.post(url, headers=headers, data=json.dumps(data))
        print(response)
        if response.status_code == 200:
            return response.json()
        else:
            return None
