from unittest.mock import patch

from entities.authorization_entity import AuthorizationRequestedEntity, AuthorizationRequestorEntity
from entities.enum.role_enum import RoleEnum
from entities.enum.user_type_enum import UserTypeEnum
from entities.exceptions.insufficient_permissions_exception import InsufficientPermissionsException
from use_cases.auth.authorization_use_case import AuthorizationUseCase


class Capture:
    def __init__(self):
        self.sent = []

    def send(self, notification):
        self.sent.append(notification)


def _requestor(role, user_type, organization_id="org-1"):
    return AuthorizationRequestorEntity(
        role=role, user_type=user_type, organization_id=organization_id
    )


def _requested(role, user_type, organization_id="org-1"):
    return AuthorizationRequestedEntity(
        role=role, user_type=user_type, organization_id=organization_id
    )


@patch("services.alert.alert_dispatch_service.AlertRepository.get_alerts", return_value=[])
def test_system_admin_is_allowed_without_dispatch(_alerts):
    capture = Capture()
    AuthorizationUseCase.check_privileges(
        requestor=_requestor(RoleEnum.ADMIN, UserTypeEnum.SYSTEM_ADMIN),
        requested=_requested(RoleEnum.OWNER, UserTypeEnum.OTHER),
        notifications=capture,
    )
    assert capture.sent == []


@patch("services.alert.alert_dispatch_service.AlertRepository.get_alerts", return_value=[])
def test_regular_user_cannot_cross_organizations(_alerts):
    capture = Capture()
    try:
        AuthorizationUseCase.check_privileges(
            requestor=_requestor(RoleEnum.REGULAR, UserTypeEnum.OTHER, "org-1"),
            requested=_requested(RoleEnum.REGULAR, UserTypeEnum.OTHER, "org-2"),
            notifications=capture,
        )
    except InsufficientPermissionsException:
        return
    raise AssertionError("cross-organization access was allowed")


def test_role_and_type_rules():
    assert AuthorizationUseCase.role_is_allowed(RoleEnum.OWNER, RoleEnum.ADMIN)
    assert not AuthorizationUseCase.role_is_allowed(RoleEnum.REGULAR, RoleEnum.ADMIN)
    assert not AuthorizationUseCase.user_type_is_allowed(
        UserTypeEnum.OTHER, UserTypeEnum.SYSTEM_ADMIN
    )
    assert AuthorizationUseCase.user_type_is_allowed(UserTypeEnum.SYSTEM_ADMIN, UserTypeEnum.OTHER)
