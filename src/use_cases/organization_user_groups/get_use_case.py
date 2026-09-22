from infra.repositories.organization_user_group_repository import OrganizationUserGroupRepository
from presentation.request.organization.organization_filter_request import OrganizationFilter
from presentation.request.user.user_filter_request import UserFilter
from presentation.request.organization_user_groups.organization_user_groups_filter_request import (
    OrganizationUserGroupsFilter,
)
from presentation.response.organization_user_groups.get_organization_user_groups_response import (
    GetOrganizationUserGroupsResponse,
)
from presentation.response.organization.get_organization_response import GetListOrganizationResponse
from presentation.response.user.get_user_response import GetUsersResponse
from presentation.response.organization_user_groups.get_organization_user_groups_response import (
    GetMyUserGroupsOrganizationsResponse,
)
from infra.repositories.organization_repository import OrganizationRepository
from infra.repositories.user_repository import UserRepository
from collections import defaultdict


@classmethod
def get_organization_user_groups(
    cls, filter: OrganizationUserGroupsFilter | None = None
) -> list[GetOrganizationUserGroupsResponse]:
    groups = OrganizationUserGroupRepository().get_groups(organization_user_groups_filter=filter)
    if groups:
        group_organizations = set()
        group_users = set()
        for group in groups:
            group_organizations.update(group.organizations)
            group_users.update(group.users)
        organizations = OrganizationRepository().get_organizations(
            organizations_filter=OrganizationFilter(ids=list(group_organizations))
        )
        organizations_dict = {organization.id: organization for organization in organizations}
        users = UserRepository().get_users(filter=UserFilter(ids=list(group_users)))
        users_dict = {user.id: user for user in users}
        for group in groups:
            group.organizations = [
                GetListOrganizationResponse(
                    id=organization_id, name=organizations_dict[organization_id].name
                )
                for organization_id in group.organizations
                if organization_id in organizations_dict
            ]
            group.users = [
                GetUsersResponse(
                    id=user_id,
                    name=f"{users_dict[user_id].contact_info.first_name} {users_dict[user_id].contact_info.last_name}",
                    email=users_dict[user_id].contact_info.email,
                    role=users_dict[user_id].role,
                    organization_id=users_dict[user_id].organization_id,
                    organization_name=(
                        organizations_dict[users_dict[user_id].organization_id].name
                        if users_dict[user_id].organization_id
                        else ""
                    ),
                )
                for user_id in group.users
                if user_id in users_dict
            ]
    response = [GetOrganizationUserGroupsResponse(**group.model_dump()) for group in groups]
    return response


@classmethod
def get_my_user_groups_organizations(
    cls, filter: OrganizationUserGroupsFilter
) -> GetMyUserGroupsOrganizationsResponse:
    organization_user_groups = cls.get_organization_user_groups(filter=filter)
    organizations_dict = defaultdict(lambda: {"id": "", "name": ""})
    for organization_user_group in organization_user_groups:
        for organization in organization_user_group.organizations:
            if organization.id not in organizations_dict:
                organizations_dict[organization.id]["id"] = organization.id
                organizations_dict[organization.id]["name"] = organization.name
    return GetMyUserGroupsOrganizationsResponse(
        organizations=[
            GetListOrganizationResponse(**organization)
            for organization in organizations_dict.values()
        ]
    )
