from datetime import datetime
from unicodedata import normalize

from loguru import logger

from entities import OrganizationEntity, OrganizationPreferencesEntity, RoleEnum, UserTypeEnum
from entities.exceptions.organization_exceptions import (
    OrganizationCreatedButErrorNotifyingException,
    OrganizationInformationAlreadyExistsException,
)
from infra.repositories import OrganizationPreferencesRepository, OrganizationRepository
from presentation.request.organization.create_organization_request import CreateOrganizationRequest
from presentation.request.user.create_user_requests import (
    CreateUserRequest,
    UserContactInfoRequest,
    UserTelemetryRequest,
)
from presentation.request.user.user_filter_request import UserFilter
from presentation.response.organization.create_organization_response import (
    CreateOrganizationResponse,
)
from notification_service import Notification, NotificationPort

from use_cases.user import UserUseCase
from use_cases.user.user_helpers import generate_password


@classmethod
def create_organization_with_first_user(
    cls,
    create_request: CreateOrganizationRequest,
    notifications: NotificationPort,
) -> CreateOrganizationResponse:
    user_use_case = UserUseCase()
    owner_username = create_request.organization_user_name.lower()
    normalized_personal_user_username = (
        normalize(
            "NFKD",
            f"{create_request.organization_owner_first_name}.{create_request.organization_owner_last_name}.{create_request.organization_name}",
        )
        .encode("ASCII", "ignore")
        .decode("ASCII")
        .replace(" ", "")
    )
    existing_resources = {}

    owner_user = user_use_case.get_user(filter=UserFilter(username=owner_username))
    if owner_user:
        existing_resources["owner"] = owner_user

    personal_user = user_use_case.get_user(
        filter=UserFilter(username=normalized_personal_user_username)
    )
    if personal_user:
        existing_resources["personal_user"] = personal_user

    if existing_resources:
        raise OrganizationInformationAlreadyExistsException(already_exists_dict=existing_resources)

    new_organization = OrganizationRepository().create_organization(
        create_organization=OrganizationEntity(
            created_at=str(datetime.now()),
            name=create_request.organization_name,
            registration_origin="default",
            organization_plan=create_request.organization_plan,
        )
    )

    OrganizationPreferencesRepository().create_organization_preferences(
        organization_id=new_organization.id,
        preferences=OrganizationPreferencesEntity(
            timezone=create_request.organization_preference_timezone,
            currency=create_request.organization_preference_currency,
            locale=create_request.organization_preference_locale,
        ),
    )

    password = generate_password()
    try:
        new_owner_user = user_use_case.create_user(
            user=CreateUserRequest(
                role=RoleEnum.OWNER.value,
                organization_id=new_organization.id,
                username=owner_username,
                password=password,
                user_type=UserTypeEnum.OTHER.value,
                contact_info=UserContactInfoRequest(
                    email=create_request.organization_owner_email,
                    first_name=create_request.organization_owner_first_name,
                    last_name=create_request.organization_owner_last_name,
                    job_position=create_request.organization_owner_job_position,
                    activity_area=create_request.organization_owner_activity_area,
                    phone=create_request.organization_owner_phone,
                    affiliation_type=create_request.organization_owner_affiliation_type,
                ),
                telemetry=UserTelemetryRequest(registration_origin="default"),
            )
        )
        new_regular_user = user_use_case.create_user(
            user=CreateUserRequest(
                role=RoleEnum.REGULAR.value,
                organization_id=new_organization.id,
                username=normalized_personal_user_username,
                password=password,
                user_type=UserTypeEnum.OTHER.value,
                contact_info=UserContactInfoRequest(
                    email=create_request.organization_owner_email,
                    first_name=create_request.organization_owner_first_name,
                    last_name=create_request.organization_owner_last_name,
                    job_position=create_request.organization_owner_job_position,
                    activity_area=create_request.organization_owner_activity_area,
                    phone=create_request.organization_owner_phone,
                    affiliation_type=create_request.organization_owner_affiliation_type,
                ),
                telemetry=UserTelemetryRequest(registration_origin="default"),
            )
        )
    except Exception as e:
        logger.error(
            f"An error occurred while creating settings for organization {new_organization.id}. Error: {e}"
        )
        cls.delete_organization(organization_id=new_organization.id)
        raise e

    try:
        notifications.send(
            Notification(
                channel="email",
                destination=new_owner_user.contact_info.email,
                payload={
                    "kind": "organization_created",
                    "organization_id": new_organization.id,
                    "organization_name": new_organization.name,
                    "user_first_name": new_owner_user.contact_info.first_name,
                    "user_last_name": new_owner_user.contact_info.last_name,
                    "owner_username": new_owner_user.username,
                    "personal_username": new_regular_user.username,
                },
            )
        )
        logger.info(
            f"Succesfully notified organization {new_organization.name} through {new_owner_user.contact_info.email}"
        )
    except Exception as e:
        logger.error(
            f"An error occurred while sending organization info to the new user for organization {new_organization.id}. Error: {e}"
        )
        cls.delete_organization(organization_id=new_organization.id)
        raise OrganizationCreatedButErrorNotifyingException()

    return CreateOrganizationResponse(
        organization_id=new_organization.id, organization_name=new_organization.name
    )
