from typing import Annotated

from fastapi import Header, HTTPException

from api.settings import Settings
from api.database.repository import MongoRepository, IRepository


async def get_token_header(x_token: Annotated[str, Header()]):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def get_query_token(token: str):
    if token != "jessica":
        raise HTTPException(status_code=400, detail="No Jessica token provided")


def getRepository(collection_name: str,settings:Settings) -> IRepository:
    return MongoRepository(collection_name,settings)