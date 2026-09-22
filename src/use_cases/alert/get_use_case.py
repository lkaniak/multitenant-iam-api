from entities.enum.user_type_enum import UserTypeEnum
from entities.exceptions.alert_exceptions import AlertNonexistentException
from entities.exceptions.insufficient_permissions_exception import InsufficientPermissionsException
from entities.user_entity import UserEntity
from infra.repositories.alert_repository import AlertRepository
from presentation.request.alert.alert_filter_request import AlertFilter
from presentation.response.alert.get_alert_response import GetAlertResponse


def _scope_filter(alert_filter: AlertFilter | None, requestor: UserEntity) -> AlertFilter:
    scoped_filter = alert_filter or AlertFilter()
    if requestor.user_type != UserTypeEnum.SYSTEM_ADMIN.value:
        scoped_filter.organization_id = requestor.organization_id
    return scoped_filter


def _assert_access(organization_id: str, requestor: UserEntity) -> None:
    if (
        requestor.user_type != UserTypeEnum.SYSTEM_ADMIN.value
        and organization_id != requestor.organization_id
    ):
        raise InsufficientPermissionsException()


@classmethod
def get_alert(cls, alert_id: str, requestor: UserEntity) -> GetAlertResponse:
    alert = AlertRepository().get_alert(alert_id)
    if not alert:
        raise AlertNonexistentException()
    _assert_access(alert.organization_id, requestor)
    return GetAlertResponse(**alert.model_dump())


@classmethod
def get_alerts(
    cls, requestor: UserEntity, alert_filter: AlertFilter | None = None
) -> list[GetAlertResponse]:
    scoped_filter = _scope_filter(alert_filter, requestor)
    alerts = AlertRepository().get_alerts(alert_filter=scoped_filter)
    return [GetAlertResponse(**alert.model_dump()) for alert in alerts]
