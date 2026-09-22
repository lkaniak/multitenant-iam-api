from bson import ObjectId
from pymongo.collection import Collection

from config import settings
from entities.enum.user_type_enum import UserTypeEnum
from entities.user_entity import UserEntity
from infra.database import get_database
from presentation.request.user.user_filter_request import UserFilter


class UserRepository:
    def __init__(self):
        db = get_database()
        self.connection = db
        self.user_collection: Collection = db[settings.MONGO_DATABASE_USER_COLLECTION]

    def get_user(self, filter: UserFilter) -> UserEntity:
        dict_filter = filter.model_dump()
        if "id" in dict_filter:
            dict_filter["_id"] = ObjectId(dict_filter["id"])
            del dict_filter["id"]
        if "organization_id" in dict_filter:
            dict_filter["organization_id"] = ObjectId(dict_filter["organization_id"])
        if not dict_filter:
            return None
        if response := self.user_collection.find_one(dict_filter):
            return UserEntity(id=response["_id"], **response)

    def get_users(self, filter: UserFilter | None = None) -> list[UserEntity]:
        dict_filter = filter.model_dump() if filter else {}
        if "id" in dict_filter:
            dict_filter["_id"] = ObjectId(dict_filter["id"])
            del dict_filter["id"]
        if "ids" in dict_filter:
            dict_filter["_id"] = {"$in": [ObjectId(id) for id in dict_filter["ids"]]}
            del dict_filter["ids"]
        if "organization_id" in dict_filter:
            dict_filter["organization_id"] = ObjectId(dict_filter["organization_id"])
        if "exclude_sys_adm" in dict_filter:
            dict_filter["user_type"] = {"$ne": UserTypeEnum.SYSTEM_ADMIN.value}
            del dict_filter["exclude_sys_adm"]
        if responses := self.user_collection.find(dict_filter):
            return [UserEntity(id=response["_id"], **response) for response in responses]

    def create_user(self, create_user: UserEntity) -> UserEntity:
        create_document = {
            **create_user.model_dump(exclude={"id"}),
        }
        if create_user.organization_id:
            create_document["organization_id"] = ObjectId(create_user.organization_id)
        response = self.user_collection.insert_one(create_document)
        if response.acknowledged:
            return self.get_user(UserFilter(id=str(response.inserted_id)))

    def create_users(self, users: list[UserEntity]) -> list[UserEntity]:
        documents = [{**create_user.model_dump(exclude={"id"})} for create_user in users]
        for document in documents:
            if document.get("organization_id"):
                document["organization_id"] = ObjectId(document["organization_id"])
        response = self.user_collection.insert_many(documents)
        if response.acknowledged:
            return self.get_users(
                UserFilter(ids=[str(entity_id) for entity_id in response.inserted_ids])
            )

    def patch_user_settings(self, user_id: str, property: str, patch_settings: dict) -> UserEntity:
        set_fields = {f"{property}.{k}": v for k, v in patch_settings.items() if v is not None}
        unset_fields = {f"{property}.{k}": "" for k, v in patch_settings.items() if v is None}

        update_operations = {}
        if set_fields:
            update_operations["$set"] = set_fields
        if unset_fields:
            update_operations["$unset"] = unset_fields

        response = self.user_collection.update_one({"_id": ObjectId(user_id)}, update_operations)
        if response.acknowledged:
            return self.get_user(UserFilter(id=user_id))

    def patch_user(self, user_id: str, patch_user: dict) -> UserEntity:
        if "organization_id" in patch_user and isinstance(patch_user["organization_id"], str):
            patch_user["organization_id"] = ObjectId(patch_user["organization_id"])
        response = self.user_collection.update_one({"_id": ObjectId(user_id)}, {"$set": patch_user})
        if response.acknowledged:
            return self.get_user(UserFilter(id=user_id))

    def delete_user(self, user_filter: UserFilter) -> None:
        if user_filter.id:
            self.user_collection.delete_one({"_id": ObjectId(user_filter.id)})
        if user_filter.organization_id:
            self.user_collection.delete_many(
                {"organization_id": ObjectId(user_filter.organization_id)}
            )
