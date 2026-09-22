from fastapi import Depends, Form, status

from entities.exceptions import (
    OrganizationInactiveException,
    IncorrectPassphraseException,
    MissingParameterException,
    NoUserFoundException,
    UserInactiveException,
)
from entities.user_entity import UserEntity
from infra.repositories import UserRepository
from presentation.request.user.user_filter_request import UserFilter
from notification_service import NotificationPort

from presentation.dependencies.notification_service import get_notifications
from use_cases.auth import AuthenticationUseCase, AuthorizationUseCase
from use_cases.user.user_helpers import is_sys_admin_user


def verify_user(
    username: str = Form(),
) -> UserEntity:
    if user := UserRepository().get_user(UserFilter(username=username.lower())):
        if user.settings.inactive:
            raise UserInactiveException(status_code=status.HTTP_401_UNAUTHORIZED)
        if not is_sys_admin_user(user) and AuthorizationUseCase.check_organization_inactivity(
            organization_id=user.organization_id
        ):
            raise OrganizationInactiveException(status_code=status.HTTP_401_UNAUTHORIZED)
        return user
    raise NoUserFoundException(status_code=status.HTTP_401_UNAUTHORIZED)


def verify_parameters(password: str = Form(), user=Depends(verify_user)) -> tuple[UserEntity, str]:
    if not user or not password:
        raise MissingParameterException(status_code=status.HTTP_400_BAD_REQUEST)

    return user, password


def verify_challenge(
    user_password=Depends(verify_parameters),
    notifications: NotificationPort = Depends(get_notifications),
) -> UserEntity:
    user, password = user_password
    if not AuthorizationUseCase.check_password(challenge=password, password=user.password):
        AuthenticationUseCase.notify_login_failed(user, notifications)
        raise IncorrectPassphraseException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user
