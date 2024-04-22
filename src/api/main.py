from fastapi import Depends, FastAPI

from api.dependencies import get_query_token, get_token_header
from api.internal import admin
from api.routers import items, users,settings
from fastapi.middleware.cors import CORSMiddleware

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
app.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_token_header)],
    responses={418: {"description": "I'm a teapot"}},
)


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}