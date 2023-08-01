from fastapi import APIRouter, Depends, HTTPException
import requests
import logging

logger = logging.getLogger()


router = APIRouter()

@router.get("/validateApi", status_code=200)
def verify_huggingface_key(token: str):
    """
    Verify the Huggingface token is valid.

    Returns:
        bool: True if token is valid, False otherwise.
    """
    try:
        response = requests.get("https://api-inference.huggingface.co/models/bert-base-uncased", headers={"Authorization": f"Bearer {token}"})
        return response.status_code == 200
    except Exception as exception:
        logger.error("Huggingface Exception:", exc_info=True)
        return False