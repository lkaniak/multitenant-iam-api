from collections import defaultdict
from entities.enum.role_enum import RoleEnum
from entities.exceptions.invalid_filter_exception import InvalidFilterRequiredException
from entities.user_entity import UserEntity
from infra.repositories.organization_activity_repository import OrganizationActivityRepository
from infra.repositories.organization_repository import OrganizationRepository
from infra.repositories.user_repository import UserRepository
from presentation.request.organization.organization_filter_request import OrganizationFilter
from presentation.request.user.user_filter_request import UserFilter
from presentation.response.organization.get_organization_response import GetMyOrganizationResponse
from presentation.response.user.get_user_response import (
    GetMyUserResponse,
    GetUserResponse,
    GetUsersResponse,
)


def get_first_user_access(user: UserEntity) -> bool:
    if (
        user.role == RoleEnum.OWNER.value
        and OrganizationActivityRepository().get_first_activity_in_organization(
            user.organization_id, user.id
        )
    ):
        return False
    elif OrganizationActivityRepository().get_first_activity_in_organization_by_user(
        user.organization_id, user.id
    ):
        return False
    return True


@classmethod
def get_all_app_users(cls) -> list[GetUsersResponse]:
    response = []
    users = UserRepository().get_users(filter=UserFilter(exclude_sys_adm=True))
    organizations = OrganizationRepository().get_organizations(
        organizations_filter=OrganizationFilter(
            ids=[user.organization_id for user in users if user.organization_id]
        )
    )
    organizations_id_name = defaultdict(lambda: {"id": "", "name": ""})
    for organization in organizations:
        organizations_id_name[organization.id] = {"id": organization.id, "name": organization.name}

    for user in users:
        user_model = {
            "id": user.id,
            "name": f"{user.contact_info.first_name} {user.contact_info.last_name}",
            "email": user.contact_info.email,
            "role": user.role,
        }
        if user.organization_id:
            user_model["organization_id"] = organizations_id_name[user.organization_id]["id"]
            user_model["organization_name"] = organizations_id_name[user.organization_id]["name"]

        response.append(GetUsersResponse(**user_model))

    return response


@classmethod
def get_users(cls, filter: UserFilter = None) -> list[GetUserResponse]:
    if not any(filter.model_dump().values()):
        raise InvalidFilterRequiredException()
    users_entity = UserRepository().get_users(filter=filter)
    return [GetUserResponse(**user_entity.model_dump()) for user_entity in users_entity]


@classmethod
def get_organization_users_without_owner(cls, organization_id: str) -> list[GetUserResponse]:
    users_entity = UserRepository().get_users(filter=UserFilter(organization_id=organization_id))
    return [
        GetUserResponse(**user_entity.model_dump())
        for user_entity in users_entity
        if user_entity.role != RoleEnum.OWNER.value
    ]


@classmethod
def get_user(cls, filter: UserFilter) -> GetUserResponse:
    if not any(filter.model_dump().values()):
        raise InvalidFilterRequiredException()
    user_entity = UserRepository().get_user(filter=filter)
    return GetUserResponse(**user_entity.model_dump()) if user_entity else None


@classmethod
def get_user_internal(cls, filter: UserFilter) -> UserEntity:
    if not any(filter.model_dump().values()):
        raise InvalidFilterRequiredException()
    return UserRepository().get_user(filter=filter)


@classmethod
def get_my_user(cls, filter: UserFilter, organization_id: str) -> GetMyUserResponse:
    if user := UserRepository().get_user(filter=filter):
        user.organization_id = organization_id
        user.telemetry.first_access_user = get_first_user_access(user)
        user_dict = user.model_dump()
        if organization := OrganizationRepository().get_organization(
            filter=OrganizationFilter(id=user.organization_id)
        ):
            user_dict["organization"] = GetMyOrganizationResponse(
                **organization.model_dump()
            ).model_dump()
        return GetMyUserResponse(**user_dict)
