#pydantic model for settings
from pydantic import BaseModel


class AppSettings(BaseModel):
    oai_api_key: str
    analytics_db_url: str