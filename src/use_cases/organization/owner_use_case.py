from common.data.dictionary_handler import set_undefined_values_to_default
from entities.enum.role_enum import RoleEnum
from entities.user_entity import UserEntity
from presentation.request.organization.patch_organization_requests import (
    PatchOrganizationOwnerRequest,
)
from presentation.request.user.patch_requests import (
    PatchUserContactInfoRequest,
    PatchUserSettingsRequest,
)
from presentation.request.user.user_filter_request import UserFilter
from presentation.response.user.get_user_response import GetUserResponse
from use_cases.user import UserUseCase


def get_organization_owner(organization_id: str) -> UserEntity:
    return UserUseCase().get_user(
        filter=UserFilter(role=RoleEnum.OWNER.value, organization_id=organization_id)
    )


@classmethod
def patch_organization_owner(cls, owner_payload: PatchOrganizationOwnerRequest) -> GetUserResponse:
    organization_owner = get_organization_owner(organization_id=owner_payload.organization_id)
    for patch_key, patch_values in iter(owner_payload):
        if not patch_values:
            continue
        if type(patch_values) in [
            PatchUserSettingsRequest,
            PatchUserContactInfoRequest,
        ]:
            values_with_defaults = patch_values.model_dump()
            set_undefined_values_to_default(
                target_dict=values_with_defaults,
                default_dict=(
                    organization_owner[patch_key]
                    if patch_key in organization_owner.model_dump()
                    else {}
                ),
            )
            patch_values = patch_values.recreate(values_with_defaults)
            UserUseCase().patch_user_settings(
                user_id=organization_owner.id, configuration=patch_values
            )
    return get_organization_owner(organization_id=owner_payload.organization_id)
