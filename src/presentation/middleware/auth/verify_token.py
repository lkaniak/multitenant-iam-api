from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from notification_service import NotificationPort

from entities import UserEntity
from presentation.dependencies.notification_service import get_notifications
from use_cases.auth import AuthenticationUseCase

bearer = HTTPBearer()


def verify_token(
    scheme_credentials: HTTPAuthorizationCredentials = Depends(bearer),
) -> str:
    return scheme_credentials.credentials


def verify_user_token(
    scheme_credentials: HTTPAuthorizationCredentials = Depends(bearer),
    notifications: NotificationPort = Depends(get_notifications),
) -> UserEntity:
    token = scheme_credentials.credentials
    user = AuthenticationUseCase.get_user_by_token(token, notifications)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return user
