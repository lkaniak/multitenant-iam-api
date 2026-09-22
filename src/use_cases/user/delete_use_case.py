from notification_service import NotificationPort

from entities.enum.alert_event_type_enum import AlertEventTypeEnum
from entities.exceptions.invalid_filter_exception import InvalidFilterRequiredException
from infra.repositories.user_repository import UserRepository
from presentation.request.user.user_filter_request import UserFilter
from infra.repositories.organization_user_group_repository import OrganizationUserGroupRepository
from services.alert.alert_dispatch_service import AlertDispatchService


@classmethod
def delete_user(
    cls,
    filter: UserFilter,
    dispatch_alert: bool = True,
    notifications: NotificationPort | None = None,
) -> None:
    if not any(filter.model_dump().values()):
        raise InvalidFilterRequiredException()
    user = None
    if dispatch_alert and (filter.id or filter.username):
        user = UserRepository().get_user(filter)
    UserRepository().delete_user(user_filter=filter)
    OrganizationUserGroupRepository().remove_user_from_groups(user_id=filter.id)
    if user and notifications:
        AlertDispatchService(notifications).dispatch(
            event_type=AlertEventTypeEnum.USER_DELETED,
            organization_id=user.organization_id,
            data={"user_id": user.id, "username": user.username},
        )
