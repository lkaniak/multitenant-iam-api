from datetime import datetime

from entities.alert_entity import AlertChannelEntity, AlertEntity
from entities.enum.user_type_enum import UserTypeEnum
from entities.exceptions.insufficient_permissions_exception import InsufficientPermissionsException
from entities.exceptions.organization_exceptions import OrganizationNonexistentException
from entities.user_entity import UserEntity
from infra.repositories.alert_repository import AlertRepository
from presentation.request.alert.create_alert_request import CreateAlertRequest
from presentation.request.organization.organization_filter_request import OrganizationFilter
from presentation.response.alert.get_alert_response import GetAlertResponse
from use_cases.organization import OrganizationUseCase


def _resolve_organization_id(organization_id: str, requestor: UserEntity) -> str:
    if requestor.user_type != UserTypeEnum.SYSTEM_ADMIN.value:
        if organization_id != requestor.organization_id:
            raise InsufficientPermissionsException()
        return requestor.organization_id
    return organization_id


@classmethod
def create_alert(cls, payload: CreateAlertRequest, requestor: UserEntity) -> GetAlertResponse:
    organization_id = _resolve_organization_id(payload.organization_id, requestor)
    if not OrganizationUseCase().get_organization(filter=OrganizationFilter(id=organization_id)):
        raise OrganizationNonexistentException()
    now = datetime.now()
    alert = AlertRepository().create_alert(
        AlertEntity(
            name=payload.name,
            organization_id=organization_id,
            event_type=payload.event_type,
            enabled=payload.enabled,
            channels=[
                AlertChannelEntity(
                    type=channel.type,
                    destination=channel.destination,
                    enabled=channel.enabled,
                )
                for channel in payload.channels
            ],
            created_at=now,
            updated_at=now,
        )
    )
    return GetAlertResponse(**alert.model_dump())
