from typing import Union

from common.data.dictionary_handler import merge_defaults_with_target
from entities.enum.alert_event_type_enum import AlertEventTypeEnum
from entities.exceptions.user_exceptions import ErrorSendingResetPasswordRequestException
from infra.repositories.user_repository import UserRepository
from notification_service import Notification, NotificationPort
from services.alert.alert_dispatch_service import AlertDispatchService
from presentation.request.user.patch_requests import (
    PatchUserContactInfoRequest,
    PatchUserRequest,
    PatchUserSettingsRequest,
    PatchUserTelemetryRequest,
    ResetPasswordRequest,
)
from presentation.request.user.user_filter_request import UserFilter
from presentation.response.user.get_user_response import GetUserResponse
from use_cases.user.user_helpers import encrypt_password, generate_password


@classmethod
def patch_user_settings(
    cls,
    user_id: str,
    configuration: Union[
        PatchUserSettingsRequest, PatchUserTelemetryRequest, PatchUserContactInfoRequest
    ],
) -> GetUserResponse:
    property_name = repr(configuration)
    user = UserRepository().get_user(filter=UserFilter(id=user_id)).model_dump()
    patch_payload = configuration.model_dump()
    patch_payload = merge_defaults_with_target(
        target_dict=patch_payload,
        previous_model=user[property_name] if property_name in user else {},
    )
    user_entity = UserRepository().patch_user_settings(
        user_id=user_id, property=property_name, patch_settings=patch_payload
    )
    return GetUserResponse(**user_entity.model_dump())


@classmethod
def patch_user(cls, user: PatchUserRequest, notifications: NotificationPort) -> GetUserResponse:
    new_values = user.model_dump(
        exclude={"password", "id", "new_password", "old_password"}, exclude_none=True
    )
    existing = UserRepository().get_user(filter=UserFilter(id=user.id))
    old_role = existing.role
    patch_payload = existing.model_dump(exclude={"password", "id"})
    for k, v in new_values.items():
        if isinstance(v, dict):
            patch_payload[k].update(v)
        else:
            patch_payload[k] = v

    if user.password:
        patch_payload["password"] = encrypt_password(user.password)
    user_entity = UserRepository().patch_user(user_id=user.id, patch_user=patch_payload)
    if user.role and user.role != old_role:
        AlertDispatchService(notifications).dispatch(
            event_type=AlertEventTypeEnum.USER_ROLE_CHANGED,
            organization_id=user_entity.organization_id,
            data={
                "user_id": user_entity.id,
                "username": user_entity.username,
                "old_role": old_role,
                "new_role": user_entity.role,
            },
        )
    return GetUserResponse(**user_entity.model_dump())


@classmethod
def send_reset_password_request(
    cls, payload: ResetPasswordRequest, notifications: NotificationPort
) -> None:
    if user := UserRepository().get_user(UserFilter(username=payload.username)):
        temp_password = generate_password()
        patch_payload = PatchUserRequest(id=user.id, password=temp_password)
        old_password = user.password
        try:
            cls.patch_user(patch_payload, notifications)
        except Exception as e:
            raise e
        try:
            notifications.send(
                Notification(
                    channel="email",
                    destination=user.contact_info.email,
                    payload={
                        "kind": "password_reset",
                        "username": payload.username,
                        "temporary_password": temp_password,
                    },
                )
            )
        except Exception:
            patch_payload = PatchUserRequest(id=user.id, password=old_password)
            cls.patch_user(patch_payload, notifications)
            raise ErrorSendingResetPasswordRequestException()
