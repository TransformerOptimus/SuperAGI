from functools import wraps
from typing import Optional, Type, Callable, Any, Union

from pydantic import BaseModel, Field, create_model, validate_arguments, Extra
from inspect import signature

class _SchemaConfig:
    """Configuration for the pydantic model."""
    extra = Extra.forbid
    arbitrary_types_allowed = True

def get_filtered_args(
    inferred_model: Type[BaseModel],
    func: Callable,
) -> dict:
    """Get the arguments from a function's signature."""
    schema = inferred_model.schema()["properties"]
    valid_keys = signature(func).parameters
    return {k: schema[k] for k in valid_keys if k != "run_manager"}

def _create_subset_model(
    name: str, model: BaseModel, field_names: list
) -> Type[BaseModel]:
    """Create a pydantic model with only a subset of model's fields."""
    fields = {
        field_name: (
            model.__fields__[field_name].type_,
            model.__fields__[field_name].default,
        )
        for field_name in field_names
        if field_name in model.__fields__
    }
    return create_model(name, **fields)  # type: ignore

def create_schema_from_function(
    model_name: str,
    func: Callable,
) -> Type[BaseModel]:
    """Create a pydantic schema from a function's signature."""
    validated = validate_arguments(func, config=_SchemaConfig)  # type: ignore
    inferred_model = validated.model  # type: ignore
    if "run_manager" in inferred_model.__fields__:
        del inferred_model.__fields__["run_manager"]
    # Pydantic adds placeholder virtual fields we need to strip
    filtered_args = get_filtered_args(inferred_model, func)
    return _create_subset_model(
        f"{model_name}Schema", inferred_model, list(filtered_args)
    )

class Tool(BaseModel):
    name: str = None
    description: str
    func: Callable
    args_schema: Type[BaseModel] = None
    coroutine: Optional[Callable] = None

    @property
    def args(self):
        # print("args_schema", self.args_schema)
        if self.args_schema is not None:
            return self.args_schema.__fields__ or self.args_schema.schema()["properties"]
        else:
            name = self.name or self.func.__name__
            args_schema = create_schema_from_function(f"{name}Schema", self.func)
            # print("args:", args_schema.schema()["properties"])
            return args_schema.schema()["properties"]

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
