class OrganizationUserGroupsUseCase:

    from use_cases.organization_user_groups.create_use_case import create_organization_user_group
    from use_cases.organization_user_groups.delete_use_case import delete_organization_user_group
    from use_cases.organization_user_groups.get_use_case import (
        get_organization_user_groups,
        get_my_user_groups_organizations,
    )
    from use_cases.organization_user_groups.edit_use_case import edit_organization_user_group

    def __init__(self):
        pass
