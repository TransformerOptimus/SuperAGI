from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Union, Optional


# Define an Enum for the different tasks
class Tasks(Enum):
    TEXT_GENERATION = "text-generation"


class TaskParameters:
    def __init__(self) -> None:
        self.params = self._generate_params()
        self._validate_params()

    def get_params(self, task, **kwargs) -> Dict[str, Union[int, float, bool, str]]:
        # Return the task parameters and override with any kwargs
        # This allows us to override the default parameters
        # Ignore any parameters that are not defined for the task
        params = self.params[task]
        for param in kwargs:
            if param in params:
                params[param] = kwargs[param]
        return params

    def _generate_params(self):
        return {
            Tasks.TEXT_GENERATION: TextGenerationParameters().__dict__,
        }

    def _validate_params(self):
        assert len(self.params) == len(Tasks), "Not all tasks have parameters defined"

        for task in Tasks:
            assert task in self.params, f"Task {task} does not have parameters defined"
            # params = self.params[task]
            # assert isinstance(params, dict), f"Task {task} parameters are not a dictionary"
            # for param in params:
            #     assert isinstance(param, str), f"Task {task} parameter {param} is not a string"
            #     assert isinstance(params[param], (int, float, bool, str)), f"Task {task} parameter {param} is not a valid type"


@dataclass
class TextGenerationParameters():
    """
    top_k: (Default: None).
    Integer to define the top tokens considered within the sample operation to create new text.

    top_p: (Default: None).
    Float to define the tokens that are within the sample operation of text generation.
    Add tokens in the sample for more probable to least probable until the sum of  the probabilities is greater than top_p.

    temperature: (Default: 1.0). Float (0.0-100.0).
    The temperature of the sampling operation.
    1 means regular sampling, 0 means always take the highest score, 100.0 is getting closer to uniform probability.

    repetition_penalty: (Default: None). Float (0.0-100.0).
    The more a token is used within generation the more it is penalized to not be picked in successive generation passes.

    max_new_tokens: (Default: None). Int (0-250).
    The amount of new tokens to be generated, this does not include the input length it is a estimate of the size of generated text you want. Each new tokens slows down the request, so look for balance between response times and length of text generated.

    max_time: (Default: None). Float (0-120.0).
    The amount of time in seconds that the query should take maximum.
    Network can cause some overhead so it will be a soft limit.
    Use that in combination with max_new_tokens for best results.

    return_full_text: (Default: True). Bool.
    If set to False, the return results will not contain the original query making it easier for prompting.

    num_return_sequences: (Default: 1). Integer.
    The number of proposition you want to be returned.

    do_sample: (Optional: True). Bool.
    Whether or not to use sampling, use greedy decoding otherwise.
    """
    top_k: Optional[int] = None
    top_p: Optional[float] = None
    temperature: float = 1.0
    repetition_penalty: Optional[float] = None
    max_new_tokens: Optional[int] = None
    max_time: Optional[float] = None
    return_full_text: bool = True
    num_return_sequences: int = 1
    do_sample: bool = True