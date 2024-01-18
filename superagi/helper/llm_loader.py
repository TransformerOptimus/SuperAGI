from llama_cpp import Llama
from llama_cpp import LlamaGrammar
from superagi.config.config import get_config
from superagi.lib.logger import logger


class LLMLoader:
    _instance = None
    _model = None
    _grammar = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(LLMLoader, cls).__new__(cls)
        return cls._instance

    def __init__(self, context_length):
        self.context_length = context_length

    @property
    def model(self):
        if self._model is None:
            try:
                self._model = Llama(
                    model_path="/app/local_model_path", n_ctx=self.context_length, n_gpu_layers=int(get_config('GPU_LAYERS', '-1')))
            except Exception as e:
                logger.error(e)
        return self._model

    @property
    def grammar(self):
        if self._grammar is None:
            try:
                self._grammar = LlamaGrammar.from_file(
                    "superagi/llms/grammar/json.gbnf")
            except Exception as e:
                logger.error(e)
        return self._grammar
