from loguru import logger
from entities.enum import UserTypeEnum
from entities.enum.alert_event_type_enum import AlertEventTypeEnum
from entities.exceptions.user_exceptions import FailedNotifyNewUserException
from entities.user_entity import (
    UserEntity,
    UserSettingsEntity,
    UserTelemetryEntity,
    UserContactInfoEntity,
)
from infra.repositories.user_repository import UserRepository
from presentation.request.user.create_user_requests import CreateUserRequest
from presentation.request.user.user_filter_request import UserFilter
from presentation.response.user.create_user_response import CreateUserResponse
from notification_service import Notification, NotificationPort

from services.alert.alert_dispatch_service import AlertDispatchService
from use_cases.user.user_helpers import encrypt_password


def _dispatch_user_created(user_entity: UserEntity, notifications: NotificationPort) -> None:
    AlertDispatchService(notifications).dispatch(
        event_type=AlertEventTypeEnum.USER_CREATED,
        organization_id=user_entity.organization_id,
        data={
            "user_id": user_entity.id,
            "username": user_entity.username,
            "role": user_entity.role,
        },
    )


def __create_user_with_defaults(user: CreateUserRequest) -> UserEntity:
    settings = (
        UserSettingsEntity(**user.settings.model_dump()) if user.settings else UserSettingsEntity()
    )
    telemetry = (
        UserTelemetryEntity(**user.telemetry.model_dump())
        if user.telemetry
        else UserTelemetryEntity()
    )
    contact_info = (
        UserContactInfoEntity(**user.contact_info.model_dump())
        if user.contact_info
        else UserContactInfoEntity()
    )

    return UserEntity(
        password=encrypt_password(user.password),
        settings=UserSettingsEntity(**settings.model_dump()),
        telemetry=UserTelemetryEntity(**telemetry.model_dump()),
        contact_info=UserContactInfoEntity(**contact_info.model_dump()),
        username=user.username.lower(),
        **user.model_dump(
            exclude={"password", "telemetry", "settings", "username", "contact_info"}
        ),
    )


@classmethod
def create_user(
    cls, user: CreateUserRequest, notifications: NotificationPort
) -> CreateUserResponse:
    user_entity = UserRepository().create_user(create_user=__create_user_with_defaults(user=user))

    response = CreateUserResponse(**user_entity.model_dump(exclude={"password"}))

    if user.user_type == UserTypeEnum.SYSTEM_ADMIN.value:
        _dispatch_user_created(user_entity, notifications)
        return response

    try:
        notifications.send(
            Notification(
                channel="email",
                destination=user.contact_info.email,
                payload={
                    "kind": "user_created",
                    "username": user.username,
                    "email": user.contact_info.email,
                    "first_name": user.contact_info.first_name,
                },
            )
        )
        logger.info(
            f"User {user.username} created successfully and notified in {user.contact_info.email}"
        )
    except Exception:
        cls.delete_user(filter=UserFilter(id=user_entity.id), dispatch_alert=False)
        raise FailedNotifyNewUserException()

    _dispatch_user_created(user_entity, notifications)
    return response


@classmethod
def create_users(cls, users: list[CreateUserRequest], notifications: NotificationPort) -> None:
    user_entities = [__create_user_with_defaults(user=user) for user in users]
    users_created = UserRepository().create_users(users=user_entities)
    try:
        notifications.send(
            Notification(
                channel="email",
                destination="",
                payload={
                    "kind": "users_created",
                    "users": [
                        {
                            "username": user.username,
                            "email": user.contact_info.email,
                            "first_name": user.contact_info.first_name,
                        }
                        for user in users
                    ],
                },
            )
        )
        username_email_string = ", ".join(
            [f"{user.username}: {user.contact_info.email}" for user in users]
        )
        logger.info(
            f"Users created successfully and notified in the corresponding relation: {username_email_string}"
        )
    except Exception:
        [
            cls.delete_user(filter=UserFilter(id=user_entity.id), dispatch_alert=False)
            for user_entity in users_created
        ]
        raise FailedNotifyNewUserException()
    for user_entity in users_created:
        _dispatch_user_created(user_entity, notifications)
