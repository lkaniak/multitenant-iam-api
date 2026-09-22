from bson import ObjectId
from pymongo.collection import Collection

from config import settings
from entities.organization_user_group_entity import OrganizationUserGroupEntity
from infra.database import get_database
from presentation.request.organization_user_groups.organization_user_groups_filter_request import (
    OrganizationUserGroupsFilter,
)


class OrganizationUserGroupRepository:
    def __init__(self):
        db = get_database()
        self.connection = db
        self.organization_user_group_collection: Collection = db[
            settings.MONGO_DATABASE_ORGANIZATION_USER_GROUP_COLLECTION
        ]

    def get_groups(
        self, organization_user_groups_filter: OrganizationUserGroupsFilter | None = None
    ) -> list[OrganizationUserGroupEntity]:
        dict_filter = (
            organization_user_groups_filter.model_dump() if organization_user_groups_filter else {}
        )
        filter = {}
        if "organization_id" in dict_filter:
            filter = {"organizations": dict_filter["organization_id"]}
        elif "user_id" in dict_filter:
            filter = {"users": dict_filter["user_id"]}
        elif "id" in dict_filter:
            filter = {"_id": ObjectId(dict_filter["id"])}
        if responses := self.organization_user_group_collection.find(filter):
            return [
                OrganizationUserGroupEntity(id=str(response["_id"]), **response)
                for response in responses
            ]
        return []

    def get_group(self, group_id: str) -> OrganizationUserGroupEntity:
        if response := self.organization_user_group_collection.find_one(
            {"_id": ObjectId(group_id)}
        ):
            return OrganizationUserGroupEntity(id=str(response["_id"]), **response)

    def create_group(self, group: OrganizationUserGroupEntity) -> OrganizationUserGroupEntity:
        response = self.organization_user_group_collection.insert_one(
            group.model_dump(exclude={"id"})
        )
        if response.acknowledged:
            return self.get_group(group_id=str(response.inserted_id))

    def delete_group(self, group_id: str) -> bool:
        result = self.organization_user_group_collection.delete_one({"_id": ObjectId(group_id)})
        if result.deleted_count > 0:
            return True
        return False

    def edit_group(self, group_id: str, edit_group: dict) -> OrganizationUserGroupEntity:
        response = self.organization_user_group_collection.update_one(
            {"_id": ObjectId(group_id)}, {"$set": edit_group}
        )
        if response.acknowledged:
            return self.get_group(group_id=group_id)

    def remove_organization_from_groups(self, organization_id: str) -> None:
        self.organization_user_group_collection.update_many(
            {"organizations": organization_id}, {"$pull": {"organizations": organization_id}}
        )

    def remove_user_from_groups(self, user_id: str) -> None:
        self.organization_user_group_collection.update_many(
            {"users": user_id}, {"$pull": {"users": user_id}}
        )
