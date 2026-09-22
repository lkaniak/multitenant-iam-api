from datetime import datetime

from loguru import logger

from entities.enum.organization_action_type_activity_enum import OrganizationActionTypeActivityEnum
from entities.user_entity import UserEntity
from infra.repositories.organization_activity_repository import OrganizationActivityRepository
from presentation.request.user.patch_requests import PatchUserTelemetryRequest
from presentation.response.organization.get_organization_response import GetOrganizationResponse


@classmethod
def register_user_activity(
    cls,
    user: UserEntity,
    organization: GetOrganizationResponse,
    activity: OrganizationActionTypeActivityEnum,
) -> None:
    OrganizationActivityRepository().register_activity(
        user.organization_id,
        user.id,
        activity,
    )

    log_message = f"Activity: {activity.value} - Accessed by user {user.username} and user_id {user.id} from organization {organization.name} and organization_id {organization.id}"
    cls.patch_user_settings(user.id, PatchUserTelemetryRequest(last_access_date=datetime.now()))

    logger.info(log_message)
