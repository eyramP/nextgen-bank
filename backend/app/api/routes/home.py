from fastapi import APIRouter
from backend.app.core.logging import get_logger

logger = get_logger()

router = APIRouter(prefix="/home",)

@router.get("/")
def home():
    logger.info("Home accessed")
    logger.debug("Home accessed")
    logger.error("Home accessed")
    logger.warning("Home accessed")
    logger.critical("Home accessed")
    return {"message": "Welcome to NextGen Banking API"}