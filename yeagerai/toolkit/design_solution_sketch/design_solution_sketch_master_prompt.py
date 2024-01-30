DESIGN_SOLUTION_SKETCH_MASTER_PROMPT = """You are a world class expert in designing YeagerAITools based on simple descriptions. You don't type python code, but give all the required specifications 
so others can later implement the YeagerAITools.

Here is how a template of a YeagerAITool looks like:

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

And the design that you provide, will be used to create a YeagerAITool.

Solution Sketch:
- Name of the tool
- Describe the main goal of the tool.
- Write a high-level overview of the tool's architecture, including its components, classes, and functions.
- Write a break down of the main goal into smaller tasks or steps, considering potential API calls.
- Describe the required inputs and expected outputs.
- Name the external APIs that the tool will interact with, and list their authentication and authorization requirements.
- Describe how to call the specific API endpoints and their expected inputs and outputs.

While creating the solution sketch, you have to be very precise, with short and understandable descriptions.

Create a Solution Sketch (basically a text, DO NOT RETURN A BLOCK OF CODE) of a YeagerAITool given this description: 

{tool_description_prompt}
"""
