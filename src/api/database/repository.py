from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel
from bson.objectid import ObjectId
from pymongo import MongoClient
from api.models.model_map import collection_to_model_map
from api.settings import Settings

class DbModel(ABC,BaseModel):

    id: Optional[str] = None

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
    def get_one_by_model(self, model: dict) -> DbModel:
        pass

    @abstractmethod
    def get_by_model(self, model: dict) -> List[DbModel]:
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
    def delete_by_id(self, id: str) -> None:
        pass

    @abstractmethod
    def delete_by_model(self, model: dict) -> None:
        pass



class MongoRepository(IRepository):
    def __init__(self, collection_name: str,settings:Settings):
        self.client = MongoClient(settings.db_url)
        self.db = self.client["dbAgent"]
        self.collection_name = collection_name
        self.collection = self.db[collection_name]

    def get_all(self) -> List[DbModel]:
        db_results = self.collection.find()

        results = []
        if db_results and len(db_results) > 0:
            for result in db_results:
                results.append(self._create_model_object(result))

        return results

    def get_by_model(self, filter: dict) -> DbModel:
        db_results = self.collection.find(filter)
        results = []
        if db_results:
            for result in db_results:
                results.append(self._create_model_object(result))
        return results

    def get_one_by_model(self, filter: dict) -> DbModel:
        db_result = self.collection.find_one(filter)
        return self._create_model_object(db_result)

    def _create_model_object(self, db_result):
        if not db_result:
            return None
        model_class = self._get_model_class()
        result = model_class(**db_result)
        result.id = str(db_result["_id"])
        return result


    def _get_model_class(self):
        return collection_to_model_map[self.collection_name]


    def get_by_id(self, id: str) -> DbModel:
        result = self.collection.find_one({"_id": ObjectId(id)})

        return self._create_model_object(result)

    def create(self, entity: DbModel) -> DbModel:
        del entity.id
        result = self.collection.insert_one(entity.model_dump())
        entity.id = str(result.inserted_id)
        return result.inserted_id


    def update(self,  entity: DbModel) -> DbModel:
        result = self.collection.update_one({"_id": ObjectId(entity.id)}, {"$set": entity.model_dump()})
        return result

    def delete_by_id(self, id: str) -> None:
        result = self.collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count

    def delete_by_model(self, model: dict) -> None:
        result = self.collection.delete_many(model)
        return result.deleted_count

