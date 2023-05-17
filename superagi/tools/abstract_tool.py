#__________________________AbstractTOOL_LOGIC____________________________


# class AbstractTool:
#     def __init__(self):
#         pass

# class Tool:
#     def __init__(self):
#         pass

############################################################################

#----------------------In Development-----------------------#

############################################################################




"""Base implementation for tools """

from typing import Callable, Optional, Union, Type
from pydantic import BaseModel
import inspect
from functools import wraps

class BaseTool:
    pass

class Tool(BaseTool):
    def __init__(
        self,
        description: str,
        func: Callable,
        coroutine: Optional[Callable] = None,
    ):
        self.description = description
        self.func = func
        self.coroutine = coroutine

    @property
    def args(self):
        return inspect.signature(self.func).parameters

    def _to_args_and_kwargs(self, tool_input: BaseModel):
        return tool_input

    def _exec(self, *tool_input):
        return self.func(*tool_input)

    async def _asyncexec(self, *tool_input):
        if self.coroutine:
            return await self.coroutine(*tool_input)
        return self.func(*tool_input)

    @classmethod
    def from_function(cls, func: Callable):
        return cls(description=func.__doc__, func=func)

class StructuredTool(BaseTool):
    def __init__(
        self,
        description: str,
        args_schema: Type[BaseModel],
        func: Callable,
        coroutine: Optional[Callable] = None,
    ):
        self.description = description
        self.args_schema = args_schema
        self.func = func
        self.coroutine = coroutine

    @property
    def args(self):
        return self.args_schema.__fields__

    def _exec(self, *tool_input):
        return self.func(*tool_input)

    async def _asyncexec(self, *tool_input):
        if self.coroutine:
            return await self.coroutine(*tool_input)
        return self.func(*tool_input)

    @classmethod
    def from_function(cls, func: Callable, args_schema: Type[BaseModel]):
        return cls(description=func.__doc__, args_schema=args_schema, func=func)

def tool(*args: Union[str, Callable], return_direct: bool = False, args_schema: Optional[Type[BaseModel]] = None, infer_schema: bool = False) -> Callable:
    def decorator(func: Callable) -> Callable:
        nonlocal args_schema

        if infer_schema:
            args_schema = create_schema_from_function(func)

        if args_schema:
            tool_instance = StructuredTool.from_function(func, args_schema)
        else:
            tool_instance = Tool.from_function(func)

        @wraps(func)
        def wrapper(*tool_args, **tool_kwargs):
            if return_direct:
                return tool_instance._exec(*tool_args, **tool_kwargs)
            else:
                return tool_instance

        return wrapper

    if len(args) == 1 and callable(args[0]):
        return decorator(args[0])
    else:
        return decorator

def create_schema_from_function(func: Callable) -> Type[BaseModel]:
    # Implement the logic to create a Pydantic schema based on the function's signature
    pass