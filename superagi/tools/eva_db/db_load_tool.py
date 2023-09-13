import json
import evadb
from typing import Type, Optional

from pydantic import BaseModel, Field

from superagi.helper.google_search import GoogleSearchWrap
from superagi.helper.token_counter import TokenCounter
from superagi.llms.base_llm import BaseLlm
from superagi.tools.base_tool import BaseTool



class DbLoadSchema(BaseModel):
    query: str = Field(
        ...,
        description="The prompt for loading data into EvaDB",
    )


class DbLoadTool(BaseTool):
    """
    Loads data into EvaDB.

    Attributes:
        name : The name of the tool.
        description : The description of the tool.
        args_schema : The args schema.
    """
    llm: Optional[BaseLlm] = None
    name = "DbLoad"
    description = (
        "A tool for loading the data from the source into EvaDB"
    )
    args_schema: Type[DbLoadSchema] = DbLoadSchema

    class Config:
        arbitrary_types_allowed = True

    def _execute(self, query: str) -> tuple:
        """
        Execute the EvaDB load tool.

        Args:
            query : the load command to execute in evaDB.

        Returns:
            The response of load query.
        """
        print("####^^^^####")
        print(query)

        cursor = evadb.connect().cursor()
        cursor.drop_table("CSVData", if_exists = True).df()
        query = cursor.query("""
            CREATE TABLE IF NOT EXISTS CSVData (
                id INTEGER UNIQUE, 
                name TEXT(30),
                area INTEGER,
                price INTEGER);
            """).execute()

        cursor.load("/app/data/sample_data.csv", "CSVData", format="csv").df()
        print("csv load done")
        ret = cursor.table("CSVData").select("*").df()
        print(ret)
        return "Successfully loaded the resource into table 'CSVData' in EvaDB. This is now available to be queries for insights"
        
        