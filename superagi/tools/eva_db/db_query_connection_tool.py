import json
import evadb
from typing import Type, Optional

from pydantic import BaseModel, Field

from superagi.helper.google_search import GoogleSearchWrap
from superagi.helper.token_counter import TokenCounter
from superagi.llms.base_llm import BaseLlm
from superagi.tools.base_tool import BaseTool



class DbQueryConnectionSchema(BaseModel):
    db_connection: str = Field(
        ...,
        description="The name of the connection on which the provided connection should be executed. This connection is created using create connection tool",
    )
    query: str = Field(
        ...,
        description="The query to be executed on the undelying database engine though EvaDB",
    )



class DbQueryConnectionTool(BaseTool):
    """
    Executes the provided query on the db engine attached in the provided db connection through EvaDB.

    Attributes:
        name : The name of the tool.
        description : The description of the tool.
        args_schema : The args schema.
    """
    llm: Optional[BaseLlm] = None
    name = "DbQueryConnectionTool"
    description = (
        "A tool for executing queries on the undelying database thorugh EvaDB"
    )
    args_schema: Type[DbQueryConnectionSchema] = DbQueryConnectionSchema

    class Config:
        arbitrary_types_allowed = True

    def _execute(self, db_connection: str, query: str) -> tuple:
        """
        Execute the EvaDB execute query tool

        Args:
            db_connection: the connection on which the query should be executed
            query : the query which should be executed on the underlying database through the provided connection

        Returns:
            Response of executed query.
        """
        print("####^^^^###")
        print(db_connection, query)
        db_query = """
            USE {db_connection} {{
                {query}
            }};
        """.format(db_connection = db_connection, query = query.strip(';'))

        print("FINAL_QUERY: ", db_query)
        cursor = evadb.connect().cursor()
        ret = cursor.query(db_query).execute()
        print(ret)
        return ("Successfully executed the provided query", "result: " + ret)

        cursor.close()
        
        