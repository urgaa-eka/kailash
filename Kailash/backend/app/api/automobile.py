from fastapi import APIRouter

router = APIRouter(prefix="/automobile", tags=["automobile"])

@router.get("/")
async def automobile_root():
    return {"message": "Automobile module - coming soon"}
