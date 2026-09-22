from typing import Optional

from fastapi import APIRouter, Body, Depends, Query, status

from common.security.permission_handler import get_admin_permissions
from entities import UserEntity
from entities.enum.alert_event_type_enum import AlertEventTypeEnum
from presentation.middleware.auth import RoleAndTypeChecker
from presentation.middleware.verify_object_id import verify_object_id
from presentation.request.alert.alert_filter_request import AlertFilter
from presentation.request.alert.create_alert_request import CreateAlertRequest
from presentation.request.alert.edit_alert_request import (
    EditAlertRequest,
    EditAlertRequestFields,
)
from presentation.response.alert.get_alert_response import GetAlertResponse
from use_cases.alert import AlertUseCase

api_router = APIRouter()
tags = ["Alerts"]


@api_router.post(
    "/alerts",
    status_code=status.HTTP_201_CREATED,
    description="Create an organization alert configuration",
    tags=tags,
    response_model=GetAlertResponse,
    response_model_exclude_unset=True,
)
def create_alert(
    logged_user: UserEntity = Depends(
        RoleAndTypeChecker(allowed_permission_combinations=get_admin_permissions())
    ),
    alert_payload: CreateAlertRequest = Body(...),
) -> GetAlertResponse:
    return AlertUseCase().create_alert(payload=alert_payload, requestor=logged_user)


@api_router.get(
    "/alerts",
    status_code=status.HTTP_200_OK,
    description="Get organization alert configurations",
    tags=tags,
    response_model=list[GetAlertResponse],
    response_model_exclude_unset=True,
)
def get_alerts(
    organization_id: Optional[str] = Query(None, description="Organization id"),
    event_type: Optional[AlertEventTypeEnum] = Query(None, description="IAM event type"),
    enabled: Optional[bool] = Query(None, description="Whether the alert is active"),
    logged_user: UserEntity = Depends(
        RoleAndTypeChecker(allowed_permission_combinations=get_admin_permissions())
    ),
) -> list[GetAlertResponse]:
    return AlertUseCase().get_alerts(
        requestor=logged_user,
        alert_filter=AlertFilter(
            organization_id=organization_id,
            event_type=event_type.value if event_type else None,
            enabled=enabled,
        ),
    )


@api_router.get(
    "/alerts/{id}",
    status_code=status.HTTP_200_OK,
    description="Get an organization alert configuration",
    tags=tags,
    response_model=GetAlertResponse,
    response_model_exclude_unset=True,
)
def get_alert(
    id: str = Depends(verify_object_id),
    logged_user: UserEntity = Depends(
        RoleAndTypeChecker(allowed_permission_combinations=get_admin_permissions())
    ),
) -> GetAlertResponse:
    return AlertUseCase().get_alert(alert_id=id, requestor=logged_user)


@api_router.put(
    "/alerts/{id}",
    status_code=status.HTTP_200_OK,
    description="Update an organization alert configuration",
    tags=tags,
    response_model=GetAlertResponse,
    response_model_exclude_unset=True,
)
def update_alert(
    id: str = Depends(verify_object_id),
    logged_user: UserEntity = Depends(
        RoleAndTypeChecker(allowed_permission_combinations=get_admin_permissions())
    ),
    alert_payload: EditAlertRequestFields = Body(...),
) -> GetAlertResponse:
    return AlertUseCase().edit_alert(
        payload=EditAlertRequest(id=id, **alert_payload.model_dump()),
        requestor=logged_user,
    )


@api_router.delete(
    "/alerts/{id}",
    status_code=status.HTTP_200_OK,
    description="Delete an organization alert configuration",
    tags=tags,
    response_model=None,
)
def delete_alert(
    id: str = Depends(verify_object_id),
    logged_user: UserEntity = Depends(
        RoleAndTypeChecker(allowed_permission_combinations=get_admin_permissions())
    ),
) -> None:
    return AlertUseCase().delete_alert(alert_id=id, requestor=logged_user)


alert_router = {"router": api_router, "tags": tags}
