from typing import Callable

from fastapi import Depends

from entities.authorization_entity import AuthorizationRequestedEntity, AuthorizationRequestorEntity
from entities.enum import RoleEnum, UserTypeEnum
from entities.user_entity import UserEntity
from notification_service import NotificationPort

from presentation.dependencies.notification_service import get_notifications
from presentation.middleware.auth.role_and_type_checker_dependency import RoleAndTypeChecker
from use_cases.auth.authorization_use_case import AuthorizationUseCase


class PrivilegesChecker:
    def __new__(
        cls,
        allowed_permission_combinations: list,
        build_requested: Callable[..., AuthorizationRequestedEntity],
    ):
        logged_user_dep = Depends(
            RoleAndTypeChecker(allowed_permission_combinations=allowed_permission_combinations)
        )

        def _call(
            logged_user: UserEntity = logged_user_dep,
            notifications: NotificationPort = Depends(get_notifications),
        ):
            requestor = AuthorizationRequestorEntity(
                role=RoleEnum.from_str(logged_user.role),
                organization_id=logged_user.organization_id,
                user_type=UserTypeEnum.from_str(logged_user.user_type),
            )

            def check(requested_context):
                requested = build_requested(requested_context)
                AuthorizationUseCase.check_privileges(
                    requestor=requestor, requested=requested, notifications=notifications
                )

            return check

        return _call


class BulkPrivilegesChecker(PrivilegesChecker):
    def __new__(
        cls,
        allowed_permission_combinations: list,
        build_requested: Callable[..., AuthorizationRequestedEntity],
    ):
        logged_user_dep = Depends(
            RoleAndTypeChecker(allowed_permission_combinations=allowed_permission_combinations)
        )

        def _call(
            logged_user: UserEntity = logged_user_dep,
            notifications: NotificationPort = Depends(get_notifications),
        ):
            requestor = AuthorizationRequestorEntity(
                role=RoleEnum.from_str(logged_user.role),
                organization_id=logged_user.organization_id,
                user_type=UserTypeEnum.from_str(logged_user.user_type),
            )

            def check(requested_contexts: list):
                for ctx in requested_contexts:
                    requested = build_requested(ctx)
                    AuthorizationUseCase.check_privileges(
                        requestor=requestor, requested=requested, notifications=notifications
                    )

            return check

        return _call
