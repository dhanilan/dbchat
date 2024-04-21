from fastapi import APIRouter, Depends
from api.settings import settings
router = APIRouter()

# API to add, update, delete and get settings
@router.get("/settings/", tags=["settings"])
async def read_settings():
    return {"settings": settings.model_dump()}

@router.post("/settings/", tags=["settings"])
async def create_settings():
    return {"settings": "settings"}

@router.put("/settings/", tags=["settings"])
async def update_settings():
    return {"settings": "settings"}

@router.delete("/settings/", tags=["settings"])
async def delete_settings():
    return {"settings": "settings"}