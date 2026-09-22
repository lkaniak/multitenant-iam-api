from datetime import datetime

from entities.exceptions.alert_exceptions import AlertNonexistentException
from entities.user_entity import UserEntity
from infra.repositories.alert_repository import AlertRepository
from presentation.request.alert.edit_alert_request import EditAlertRequest
from presentation.response.alert.get_alert_response import GetAlertResponse


@classmethod
def edit_alert(cls, payload: EditAlertRequest, requestor: UserEntity) -> GetAlertResponse:
    cls.get_alert(alert_id=payload.id, requestor=requestor)
    updates = payload.model_dump(exclude={"id"}, exclude_none=True)
    updates["updated_at"] = datetime.now()
    alert = AlertRepository().edit_alert(alert_id=payload.id, edit_alert=updates)
    if not alert:
        raise AlertNonexistentException()
    return GetAlertResponse(**alert.model_dump())
