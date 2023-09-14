import json
import evadb
from typing import Type, Optional

from pydantic import BaseModel, Field

from superagi.helper.google_search import GoogleSearchWrap
from superagi.helper.token_counter import TokenCounter
from superagi.llms.base_llm import BaseLlm
from superagi.tools.base_tool import BaseTool



class DbCreateConnectionSchema(BaseModel):
    db_engine: str = Field(
        ...,
        description = "The name of underlying database engine to connect to",
    )
    username: str = Field(
        ...,
        description = "The username for connecting to the database",
    )
    host: str = Field(
        ...,
        description = "The hostname for connecting to the database",
    )
    port: str = Field(
        ...,
        description = "The port for connecting to the database",
    )
    database_name: str = Field(
        ...,
        description = "The name of the database in the underlying database to connect to",
    )


class DbCreateConnectionTool(BaseTool):
    """
    Creates a connection entry in EvaDB for the underlying database engine to use it to execute future queries on the underlying database.

    Attributes:
        name : The name of the tool.
        description : The description of the tool.
        args_schema : The args schema.
    """
    llm: Optional[BaseLlm] = None
    name = "DbCreateConnectionTool"
    description = (
        """
        A tool for creating connection to the required database in the corresponding database engine using the credentials provided by the user.
        """
    )
    args_schema: Type[DbCreateConnectionSchema] = DbCreateConnectionSchema

    class Config:
        arbitrary_types_allowed = True

    def _execute(self, db_engine: str, username: str, host: str, port: str, database_name: str) -> tuple:
        """
        Execute the EvaDB create connection tool.

        Args:
            db_engine: The name of underlying database engine to connect to
            username: The username for connecting to the database
            password: The password for connecting to the database
            host: The hostname for connecting to the database
            port: The port for connecting to the database
            database_name: The name of the database in the underlying database to connect to

        Returns:
            The response of create connection query
        """
        print("####^^^^####")
        cursor = evadb.connect().cursor()
        db_connection_name = db_engine + '__' + database_name
        create_db_query = """
            CREATE DATABASE {connection_name} WITH ENGINE = '{db_engine}', PARAMETERS = {{
                "user": "{username}",
                "host": "{hostname}",
                "port": "{port}",
                "database": "{db_name}",
                "password": "{password}"
            }};
        """.format(connection_name = db_connection_name, db_engine = db_engine, username = username, 
        hostname = host, port = port, db_name = database_name, password = "dbpass")
        print("create_db_query", create_db_query)
        ret = cursor.query(create_db_query).execute()
        print(ret)
        cursor.close()
        return """
            Sucessfully created the desired connection to underlying databse engine with name {connection}.
            This connection can now be used to query requested database.""".format(connection = db_connection_name)
        
        # return "Error occurred while executing create connection query"        
        