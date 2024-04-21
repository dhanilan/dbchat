#pydantic model for settings
from typing import Optional
from pydantic import BaseModel


class BaseDbModel():
    id: Optional[str] = None

class AppSettings(BaseModel,BaseDbModel):
    oai_api_key: str=None
    analytics_db_url: str=None
    customer_id: str = "default"