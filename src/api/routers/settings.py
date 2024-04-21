from fastapi import APIRouter, Depends
from api.settings import settings
from api.models.model_map import CONST_TABLE_NAME_APP_SETTINGS
from api.models.AppSettings import AppSettings
from api.dependencies import getRepository
router = APIRouter()

# API to add, update, delete and get settings
@router.get("/settings/", tags=["settings"])
async def read_settings(customer_id: str = "default"):

    repository = getRepository(CONST_TABLE_NAME_APP_SETTINGS,settings)
    app_settings  = repository.get_one_by_model({"customer_id":customer_id})
    return app_settings

@router.post("/settings/", tags=["settings"])
async def create_settings(app_settings: AppSettings):

    repository = getRepository(CONST_TABLE_NAME_APP_SETTINGS,settings)
    existing_app_settings  = repository.get_one_by_model({"customer_id":app_settings.customer_id})

    if existing_app_settings:
        app_settings.id = existing_app_settings.id
        repository.update(app_settings)
    else:
        repository.create(app_settings)

    return {"success": app_settings.id}


@router.delete("/settings/", tags=["settings"])
async def delete_settings(customer_id: str = "default"):

    repository = getRepository(CONST_TABLE_NAME_APP_SETTINGS,settings)
    repository.delete_by_model({"customer_id":customer_id})
    return {"success": True}