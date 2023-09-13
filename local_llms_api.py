from fastapi import APIRouter
from local_llms import inference
from local_llm_model import LocalLLM
from superagi.lib.logger import logger

router = APIRouter()

@router.post("/run", status_code=201)
def run_local_llm(payload: LocalLLM):
    reponse = inference(payload)
    logger.info(reponse)