from api.models.model_map import CONST_TABLE_NAME_APP_SETTINGS
from fastapi import Depends, FastAPI

from api.dependencies import get_query_token, get_token_header, getRepository
from api.internal import admin
from api.routers import items, users,settings,conversation,connections
from fastapi.middleware.cors import CORSMiddleware
from api.settings import settings as config_settings


def ini_app():
    app = FastAPI() # dependencies=[Depends(get_query_token)])

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],

    )

    app.include_router(users.router)
    app.include_router(items.router)
    app.include_router(settings.router)
    app.include_router(conversation.router)
    app.include_router(connections.router)

    app.include_router(
        admin.router,
        prefix="/admin",
        tags=["admin"],
        dependencies=[Depends(get_token_header)],
        responses={418: {"description": "I'm a teapot"}},
    )

    # check if the db connection is working
    print("Checking DB Connection")
    print(config_settings.db_url)
    repo = getRepository(CONST_TABLE_NAME_APP_SETTINGS,config_settings)
    repo.get_one_by_model({"customer_id":"default"})


    @app.get("/")
    async def root():
        return {"message": "Hello Bigger Applications!"}
    return app


app = ini_app()