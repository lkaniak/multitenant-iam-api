from bson import ObjectId
from pymongo.collection import Collection

from config import settings
from entities.alert_entity import AlertChannelEntity, AlertEntity
from infra.database import get_database
from presentation.request.alert.alert_filter_request import AlertFilter


class AlertRepository:
    def __init__(self) -> None:
        db = get_database()
        self.connection = db
        self.alert_collection: Collection = db[settings.MONGO_DATABASE_ALERT_COLLECTION]
        self.channel_collection: Collection = db[settings.MONGO_DATABASE_CHANNEL_COLLECTION]

    def create_alert(self, alert: AlertEntity) -> AlertEntity:
        channel_ids = self._insert_channels(alert.channels)
        result = self.alert_collection.insert_one(
            {
                "organization": ObjectId(alert.organization_id),
                "name": alert.name,
                "event_type": alert.event_type,
                "enabled": alert.enabled,
                "channels": channel_ids,
                "created_at": alert.created_at,
                "updated_at": alert.updated_at,
            }
        )
        if result.acknowledged:
            return self.get_alert(str(result.inserted_id))

    def get_alert(self, alert_id: str) -> AlertEntity | None:
        document = self.alert_collection.find_one({"_id": ObjectId(alert_id)})
        if document:
            return self._to_entity(document)
        return None

    def get_alerts(self, alert_filter: AlertFilter | None = None) -> list[AlertEntity]:
        mongo_filter = self._build_filter(alert_filter)
        documents = list(self.alert_collection.find(mongo_filter))
        channels_by_id = self._load_channels(documents)
        return [self._to_entity(document, channels_by_id) for document in documents]

    def edit_alert(self, alert_id: str, edit_alert: dict) -> AlertEntity | None:
        current = self.get_alert(alert_id)
        if not current:
            return None
        document = self._to_document_update(edit_alert)
        if "channels" in edit_alert:
            self._delete_channels([channel.id for channel in current.channels])
            document["channels"] = self._insert_channels(
                [
                    (
                        channel
                        if isinstance(channel, AlertChannelEntity)
                        else AlertChannelEntity(**channel)
                    )
                    for channel in edit_alert["channels"]
                ]
            )
        result = self.alert_collection.update_one({"_id": ObjectId(alert_id)}, {"$set": document})
        if result.acknowledged:
            return self.get_alert(alert_id)
        return None

    def delete_alert(self, alert_id: str) -> bool:
        alert = self.get_alert(alert_id)
        if not alert:
            return False
        self._delete_channels([channel.id for channel in alert.channels])
        result = self.alert_collection.delete_one({"_id": ObjectId(alert_id)})
        return result.deleted_count > 0

    def delete_by_organization_id(self, organization_id: str) -> None:
        alerts = list(self.alert_collection.find({"organization": ObjectId(organization_id)}))
        channel_ids = [
            ObjectId(channel_id) for alert in alerts for channel_id in alert.get("channels", [])
        ]
        if channel_ids:
            self.channel_collection.delete_many({"_id": {"$in": channel_ids}})
        self.alert_collection.delete_many({"organization": ObjectId(organization_id)})

    def _build_filter(self, alert_filter: AlertFilter | None) -> dict:
        dict_filter = alert_filter.model_dump() if alert_filter else {}
        mongo_filter = {}
        if dict_filter.get("id"):
            mongo_filter["_id"] = ObjectId(dict_filter["id"])
        if dict_filter.get("ids"):
            mongo_filter["_id"] = {"$in": [ObjectId(alert_id) for alert_id in dict_filter["ids"]]}
        if dict_filter.get("organization_id"):
            mongo_filter["organization"] = ObjectId(dict_filter["organization_id"])
        if dict_filter.get("event_type"):
            mongo_filter["event_type"] = dict_filter["event_type"]
        if "enabled" in dict_filter:
            mongo_filter["enabled"] = dict_filter["enabled"]
        return mongo_filter

    def _insert_channels(self, channels: list[AlertChannelEntity]) -> list[ObjectId]:
        channel_ids = []
        for channel in channels:
            result = self.channel_collection.insert_one(channel.model_dump(exclude={"id"}))
            channel_ids.append(result.inserted_id)
        return channel_ids

    def _delete_channels(self, channel_ids: list[str]) -> None:
        object_ids = [ObjectId(channel_id) for channel_id in channel_ids if channel_id]
        if object_ids:
            self.channel_collection.delete_many({"_id": {"$in": object_ids}})

    def _load_channels(self, documents: list[dict]) -> dict[str, dict]:
        channel_ids = [
            ObjectId(channel_id)
            for document in documents
            for channel_id in document.get("channels", [])
        ]
        if not channel_ids:
            return {}
        return {
            str(channel["_id"]): channel
            for channel in self.channel_collection.find({"_id": {"$in": channel_ids}})
        }

    def _to_document_update(self, edit_alert: dict) -> dict:
        document = {}
        if "organization_id" in edit_alert:
            document["organization"] = ObjectId(edit_alert["organization_id"])
        if "name" in edit_alert:
            document["name"] = edit_alert["name"]
        if "event_type" in edit_alert:
            document["event_type"] = edit_alert["event_type"]
        if "enabled" in edit_alert:
            document["enabled"] = edit_alert["enabled"]
        if "created_at" in edit_alert:
            document["created_at"] = edit_alert["created_at"]
        if "updated_at" in edit_alert:
            document["updated_at"] = edit_alert["updated_at"]
        return document

    def _to_entity(
        self, document: dict, channels_by_id: dict[str, dict] | None = None
    ) -> AlertEntity:
        if channels_by_id is None:
            channels_by_id = self._load_channels([document])
        channels = []
        for channel_id in document.get("channels", []):
            channel = channels_by_id.get(str(channel_id))
            if channel:
                channels.append(
                    AlertChannelEntity(
                        id=str(channel["_id"]),
                        type=channel["type"],
                        destination=channel["destination"],
                        enabled=channel.get("enabled", True),
                    )
                )
        return AlertEntity(
            id=str(document["_id"]),
            organization_id=str(document["organization"]),
            name=document["name"],
            event_type=document["event_type"],
            enabled=document.get("enabled", True),
            channels=channels,
            created_at=document["created_at"],
            updated_at=document["updated_at"],
        )
