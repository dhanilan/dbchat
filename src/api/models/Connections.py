#pydantic model for settings
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from api.models.BaseDbModel import BaseDbModel
from db_chat.sql_builder.schema import Schema


class Connection(BaseModel,BaseDbModel):
    name: str
    customer_id: str
    validated: Optional[ bool] = False
    connection_string: Optional[ str] = None
    connection_schema: Optional[ Schema] = None