from bson import ObjectId
from pymongo.collection import Collection

from config import settings
from entities.organization_entity import OrganizationEntity
from infra.database import get_database
from presentation.request.organization.organization_filter_request import OrganizationFilter


class OrganizationRepository:
    def __init__(self):
        db = get_database()
        self.connection = db
        self.organization_collection: Collection = db[
            settings.MONGO_DATABASE_ORGANIZATION_COLLECTION
        ]

    def get_first_organization(self) -> OrganizationEntity:
        if response := self.organization_collection.find_one():
            return OrganizationEntity(id=str(response["_id"]), **response)

    def get_organizations(
        self, organizations_filter: OrganizationFilter | None = None
    ) -> list[OrganizationEntity]:
        dict_filter = organizations_filter.model_dump() if organizations_filter else {}
        filter = {}
        if "ids" in dict_filter:
            filter = {"_id": {"$in": [ObjectId(id) for id in dict_filter["ids"]]}}
        if responses := self.organization_collection.find(filter):
            return [
                OrganizationEntity(id=str(response["_id"]), **response) for response in responses
            ]
        return []

    def get_organization(self, filter: OrganizationFilter) -> OrganizationEntity:
        dict_filter = filter.model_dump()
        if "id" in dict_filter:
            dict_filter["_id"] = ObjectId(dict_filter["id"])
            del dict_filter["id"]
        if not dict_filter:
            return None
        if response := self.organization_collection.find_one(dict_filter):
            return OrganizationEntity(id=str(response["_id"]), **response)

    def create_organization(self, create_organization: OrganizationEntity) -> OrganizationEntity:
        response = self.organization_collection.insert_one(
            create_organization.model_dump(exclude={"id"})
        )
        if response.acknowledged:
            return self.get_organization(OrganizationFilter(id=str(response.inserted_id)))

    def patch_organization(
        self, organization_id: str, patch_organization: dict
    ) -> OrganizationEntity:
        response = self.organization_collection.update_one(
            {"_id": ObjectId(organization_id)}, {"$set": patch_organization}
        )
        if response.acknowledged:
            return self.get_organization(OrganizationFilter(id=organization_id))

    def delete_organization_by_id(self, organization_id: str) -> bool:
        result = self.organization_collection.delete_one({"_id": ObjectId(organization_id)})
        if result.deleted_count > 0:
            return True
        return False
