from datetime import datetime

from bson import ObjectId
from pymongo.collection import Collection

from config import settings
from entities import OrganizationActionTypeActivityEnum
from infra.database import get_database


class OrganizationActivityRepository:
    def __init__(self) -> None:
        db = get_database()
        self.connection = db
        self.organization_activity_collection: Collection = db[
            settings.MONGO_DATABASE_ORGANIZATION_ACTIVITY_COLLECTION
        ]

    def register_activity(
        self, organization_id: str, user_id: str, action: OrganizationActionTypeActivityEnum
    ) -> None:
        self.organization_activity_collection.insert_one(
            {
                "organization_id": ObjectId(organization_id),
                "user_id": ObjectId(user_id),
                "action": action.value,
                "date": datetime.now(),
            }
        )

    def get_first_activity_in_organization(self, organization_id: str, owner_id: str) -> dict:
        if response := self.organization_activity_collection.find_one(
            {
                "organization_id": ObjectId(organization_id),
                "user_id": {"$nin": [ObjectId(owner_id)]},
            }
        ):
            return response

    def get_first_activity_in_organization_by_user(
        self, organization_id: str, user_id: str
    ) -> dict:
        if response := self.organization_activity_collection.find_one(
            {"organization_id": ObjectId(organization_id), "user_id": ObjectId(user_id)}
        ):
            return response

    def delete_by_organization_id(self, organization_id: str) -> None:
        self.organization_activity_collection.delete_many(
            {"organization_id": ObjectId(organization_id)}
        )
