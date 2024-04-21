from fastapi import APIRouter, Depends
from api.settings import settings
from api.models.model_map import CONST_TABLE_NAME_APP_SETTINGS
from api.dependencies import getRepository
router = APIRouter()

# API to add, update, delete and get settings
@router.get("/settings/", tags=["settings"])
async def read_settings():

    repository = getRepository(CONST_TABLE_NAME_APP_SETTINGS,settings)
    app_settings  = repository.get_all()
    return app_settings

@router.post("/settings/", tags=["settings"])
async def create_settings():
    return {"settings": "settings"}

@router.put("/settings/", tags=["settings"])
async def update_settings():
    return {"settings": "settings"}

@router.delete("/settings/", tags=["settings"])
async def delete_settings():
    return {"settings": "settings"}