import json
import evadb
from typing import Type, Optional

from pydantic import BaseModel, Field

from superagi.helper.google_search import GoogleSearchWrap
from superagi.helper.token_counter import TokenCounter
from superagi.llms.base_llm import BaseLlm
from superagi.tools.base_tool import BaseTool



class DbQuerySchema(BaseModel):
    query: str = Field(
        ...,
        description="The prompt for querying evaDB",
    )


class DbQueryTool(BaseTool):
    """
    Executes queries on evaDB using SQL like eva Query language.

    Attributes:
        name : The name of the tool.
        description : The description of the tool.
        args_schema : The args schema.
    """
    llm: Optional[BaseLlm] = None
    name = "DbQuery"
    description = (
        "A tool for executing queries based on the tables in EvaDB"
    )
    args_schema: Type[DbQuerySchema] = DbQuerySchema

    class Config:
        arbitrary_types_allowed = True

    def _execute(self, query: str) -> tuple:
        """
        Execute the EvaDB query tool.

        Args:
            query : the task to execute on evaDB

        Returns:
            Response of query executed on EvaDB.
        """
        print("****^^^^****")
        print(query)

        cursor = evadb.connect().cursor()
        ret = cursor.query("SELECT * FROM CSVData ORDER BY price DESC LIMIT 1").df()
        print(ret)
        return ret
        
        