from fastapi import APIRouter

router = APIRouter(prefix="/home",)

@router.get("/")
def home():
    return {"message": "Welcome to NextGen Banking API"}