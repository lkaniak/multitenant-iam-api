from bson import ObjectId
from pymongo.collection import Collection

from config import settings
from entities import OrganizationPreferencesEntity
from infra.database import get_database


class OrganizationPreferencesRepository:
    def __init__(self) -> None:
        db = get_database()
        self.connection = db
        self.organization_preferences_collection: Collection = db[
            settings.MONGO_DATABASE_ORGANIZATION_PREFERENCES_COLLECTION
        ]

    def create_organization_preferences(
        self, organization_id: str, preferences: OrganizationPreferencesEntity
    ) -> None:
        self.organization_preferences_collection.insert_one(
            {"organization_id": ObjectId(organization_id), **preferences.model_dump()},
        )

    def delete_by_organization_id(self, organization_id: str) -> None:
        self.organization_preferences_collection.delete_many(
            {"organization_id": ObjectId(organization_id)}
        )
