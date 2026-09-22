from entities.enum import RoleEnum, UserTypeEnum


def combine_permission(role: RoleEnum, user_type: UserTypeEnum) -> str:
    return f"{user_type.value}:{role.value}"


def combine_permissions(permission_combinations: list[tuple[RoleEnum, UserTypeEnum]]) -> list[str]:
    return [
        f"{combine_permission(role=permission[0], user_type=permission[1])}"
        for permission in permission_combinations
    ]


def get_all_permissions() -> list[str]:
    return [(role, user_type) for role in RoleEnum for user_type in UserTypeEnum]


def get_restricted_permissions() -> list[str]:
    return [
        (role, user_type)
        for role in RoleEnum
        for user_type in UserTypeEnum
        if user_type == UserTypeEnum.SYSTEM_ADMIN and role != RoleEnum.OWNER
    ]


def get_owner_permissions() -> list[str]:
    owner_permissions = [
        (role, user_type)
        for role in RoleEnum
        for user_type in UserTypeEnum
        if role == RoleEnum.OWNER
    ]
    owner_permissions.extend(
        [(RoleEnum.REGULAR, UserTypeEnum.SYSTEM_ADMIN), (RoleEnum.ADMIN, UserTypeEnum.SYSTEM_ADMIN)]
    )
    return owner_permissions


def get_admin_permissions() -> list[str]:
    admin_permissions = [
        (role, user_type)
        for role in RoleEnum
        for user_type in UserTypeEnum
        if role in [RoleEnum.ADMIN, RoleEnum.OWNER]
    ]
    admin_permissions.append((RoleEnum.REGULAR, UserTypeEnum.SYSTEM_ADMIN))
    return admin_permissions
