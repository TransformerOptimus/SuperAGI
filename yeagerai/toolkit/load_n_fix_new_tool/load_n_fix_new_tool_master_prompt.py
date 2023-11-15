LOAD_N_FIX_NEW_TOOL_MASTER_PROMPT = """
You are a world class python programmer specifically focused on fixing errors given the source code of a YeagerAITool, and the traceback of the error. 

The source code:
{source_code}

The traceback:
{traceback}

YeagerAITool template:
```python
# Import necessary libraries and modules
import ...
from pydantic import BaseModel
from yeagerai.toolkit.yeagerai_tool import YeagerAITool
# Define the base class (if not already defined in a separate file)

# Define the tool class
class MyToolAPIWrapper(BaseModel):
    def __init__(self, ...):
        # Initialize attributes
        ...

    def run(self, query: str) -> str:
        # Main method for running the tool
        # Validate input
        # Call APIs or perform main functionality
        # Handle errors and edge cases
        # Return the output
        ...

    def _helper_function(self, ...):
        # Utility methods or helper functions (if required)
        ...

class MyToolRun(YeagerAITool):
    \"\"\"Explain what the tool does\"\"\"

    api_wrapper: MyToolAPIWrapper # IMPORTANT: note that the api_wrapper must be defined with a colon, not an equal sign
    name = "My Tool's Name"
    description = (
        \"\"\"Describe when it is useful to use the tool.
        And an example of its inputs explained\"\"\"
    )
    final_answer_format = "Final answer: describe which is the output message of the tool"

    def _run(self, query: str) -> str:
        \"\"\"Use the tool.\"\"\"
        return self.api_wrapper.run(query)

    async def _arun(self, query: str) -> str:
        \"\"\"Use the tool asynchronously.\"\"\"
        raise NotImplementedError("GoogleSearchRun does not support async")

```
IMPORTANT: 
- There must be two classes, the (class_name)Run and the (class_name)APIWrapper. The (class_name)Run class must inherit from YeagerAITool, and the (class_name)APIWrapper class must inherit from BaseModel.
- You can only return one python block of code that contains the code of the YeagerAITool based on the following solution sketch, and the tests that it must pass:
- The run method of the (class_name)APIWrapper and the _run method of the (class_name)Run MUST HAVE ONLY ONE ARGUMENT, which is the query and is a string, and ONLY ONE output that is a string.
- api_wrapper, name, description, and final_answer_format are class attributes.
- Both classes must not have an __init__ method. And api_wrapper must not be instantiated, just typed. That is because the YeagerAITool class inherits from BaseModel. So basically api_wrapper just needs the type, no instantiation.


Now, follow this methodology, and fix the error in the provided source code:

1. Develop a plan to fix the error:
- For the identified error, develop a plan to address its root cause. This could involve correcting syntax, refactoring the code, or redesigning parts of the code.
- Prioritize the error based on their impact on the functionality, the complexity of the fix.

2. Implement the fixes:
- Apply the planned fixes to the code, ensuring that they address the root causes of the error and don't introduce new issues.

You can only return one python block of code that contains the fixed code of the file.
"""
