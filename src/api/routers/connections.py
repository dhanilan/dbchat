from datetime import datetime
from fastapi import APIRouter, Depends
from api.settings import settings
from api.models.model_map import CONST_TABLE_NAME_CONNECTIONS
from api.models.Connections import Connection
from api.dependencies import getRepository
from db_chat.sql_builder.schema import Schema,build_schema,validate_schema


router = APIRouter()

@router.get("/connections/", tags=["connections"])
async def read_connections(customer_id: str = "default"):
    repository = getRepository(CONST_TABLE_NAME_CONNECTIONS,settings)
    connections  = repository.get_by_model({"customer_id":customer_id})
    return connections

@router.post("/connections/", tags=["connections"])
async def create_connection(connection: Connection):
    repository = getRepository(CONST_TABLE_NAME_CONNECTIONS,settings)
    repository.create(connection)
    return connection

@router.get("/connections/{id}", tags=["connections"])
async def read_connection(id: str):
    repository = getRepository(CONST_TABLE_NAME_CONNECTIONS,settings)
    connection  = repository.get_one_by_model({"id":id})
    return connection

@router.delete("/connections/{id}", tags=["connections"])
async def delete_connection(id: str):
    repository = getRepository(CONST_TABLE_NAME_CONNECTIONS,settings)
    repository.delete_by_id(id)
    return {"success": True}

@router.put("/connections/{id}", tags=["connections"])
async def update_connection(id: str,connection: Connection):
    repository = getRepository(CONST_TABLE_NAME_CONNECTIONS,settings)
    connection.id = id
    repository.update(connection)
    return {"success": True}

@router.get("/connections/{connection_id}/schema", tags=["connections"])
async def read_connection_schema(connection_id: str):
    repository = getRepository(CONST_TABLE_NAME_CONNECTIONS,settings)
    connection  = repository.get_one_by_model({"id":connection_id})
    return connection.connection_schema.dict()

@router.post("/connections/{connection_id}/schema", tags=["connections"])
async def create_connection_schema(connection: Connection):
    schema = build_schema(connection.connection_string)
    return schema