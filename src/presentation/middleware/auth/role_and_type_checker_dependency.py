from fastapi import Depends, HTTPException, status

from common.security.permission_handler import combine_permission, combine_permissions
from entities.enum import RoleEnum
from entities.enum.user_type_enum import UserTypeEnum
from entities.user_entity import UserEntity
from notification_service import NotificationPort

from presentation.dependencies.notification_service import get_notifications
from presentation.middleware.auth.verify_token import verify_user_token
from use_cases.auth.authorization_use_case import AuthorizationUseCase


class RoleAndTypeChecker:
    def __init__(self, allowed_permission_combinations: list[tuple[RoleEnum, UserTypeEnum]] = []):
        self.allowed_combinations = combine_permissions(allowed_permission_combinations)

    def __call__(
        self,
        user: UserEntity = Depends(verify_user_token),
        notifications: NotificationPort = Depends(get_notifications),
    ) -> UserEntity:
        if (
            combine_permission(RoleEnum.from_str(user.role), UserTypeEnum.from_str(user.user_type))
            in self.allowed_combinations
        ):
            return user
        AuthorizationUseCase.notify_permission_denied(
            organization_id=user.organization_id,
            notifications=notifications,
            data={"user_id": user.id, "username": user.username, "role": user.role},
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You don't have enough permissions"
        )
