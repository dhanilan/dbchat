from abc import ABC, abstractmethod
from typing import List
from pydantic import BaseModel
from pymongo import MongoClient
from api.models.model_map import collection_to_model_map
from api.settings import Settings
class DbModel(ABC,BaseModel):

    id: str

    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def to_dict(self):
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict):
        pass

class IRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[DbModel]:
        pass

    @abstractmethod
    def get_by_id(self, id: str) -> DbModel:
        pass

    @abstractmethod
    def create(self, entity: DbModel) -> DbModel:
        pass

    @abstractmethod
    def update(self, entity: DbModel) -> DbModel:
        pass

    @abstractmethod
    def delete(self, entity: DbModel) -> None:
        pass

class MongoRepository(IRepository):
    def __init__(self, collection_name: str,settings:Settings):
        self.client = MongoClient(settings.db_url)
        self.db = self.client["dbAgent"]
        self.collection_name = collection_name
        self.collection = self.db[collection_name]

    def get_all(self) -> List[DbModel]:
        results = self.collection.find()
        model_class = self._get_model_class()
        return [model_class(**result) for result in results]

    def _get_model_class(self):
        return collection_to_model_map[self.collection_name]


    def get_by_id(self, id: str) -> DbModel:
        pass

    def create(self, entity: DbModel) -> DbModel:
        pass

    def update(self, entity: DbModel) -> DbModel:
        pass

    def delete(self, entity: DbModel) -> None:
        pass

