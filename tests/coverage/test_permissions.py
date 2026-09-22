from common.security.permission_handler import (
    combine_permission,
    get_admin_permissions,
    get_all_permissions,
    get_owner_permissions,
    get_restricted_permissions,
)
from entities.enum.role_enum import RoleEnum
from entities.enum.user_type_enum import UserTypeEnum


def test_permission_sets_match_role_and_type():
    assert combine_permission(RoleEnum.OWNER, UserTypeEnum.OTHER) == "other:owner"
    assert (RoleEnum.ADMIN, UserTypeEnum.SYSTEM_ADMIN) in get_restricted_permissions()
    assert (RoleEnum.OWNER, UserTypeEnum.SYSTEM_ADMIN) not in get_restricted_permissions()
    assert (RoleEnum.OWNER, UserTypeEnum.OTHER) in get_owner_permissions()
    assert (RoleEnum.REGULAR, UserTypeEnum.OTHER) not in get_owner_permissions()
    assert (RoleEnum.ADMIN, UserTypeEnum.OTHER) in get_admin_permissions()
    assert (RoleEnum.REGULAR, UserTypeEnum.OTHER) not in get_admin_permissions()
    assert len(get_all_permissions()) == len(RoleEnum) * len(UserTypeEnum)
