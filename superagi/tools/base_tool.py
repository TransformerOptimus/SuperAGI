from functools import wraps
from typing import Optional, Type, Callable, Any, Union

from pydantic import BaseModel, Field
from inspect import signature

class Tool(BaseModel):
    name: str = None
    description: str
    func: Callable
    args_schema: Type[BaseModel] = None
    coroutine: Optional[Callable] = None

    @property
    def args(self):
        if self.args_schema:
            return self.args_schema.__fields__
        else:
            return signature(self.func).parameters

    def execute(self, *tool_input):
        return self.func(*tool_input)

    @classmethod
    def from_function(cls, func: Callable, args_schema: Type[BaseModel] = None):
        if args_schema:
            return cls(description=func.__doc__, args_schema=args_schema, func=func)
        else:
            return cls(description=func.__doc__, func=func)

def tool(*args: Union[str, Callable], return_direct: bool = False, args_schema: Optional[Type[BaseModel]] = None) -> Callable:
    def decorator(func: Callable) -> Callable:
        nonlocal args_schema

        tool_instance = Tool.from_function(func, args_schema)

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
