from entities.exceptions.alert_exceptions import AlertNonexistentException
from entities.user_entity import UserEntity
from infra.repositories.alert_repository import AlertRepository


@classmethod
def delete_alert(cls, alert_id: str, requestor: UserEntity) -> None:
    cls.get_alert(alert_id=alert_id, requestor=requestor)
    deleted = AlertRepository().delete_alert(alert_id)
    if not deleted:
        raise AlertNonexistentException()
