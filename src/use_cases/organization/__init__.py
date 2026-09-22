class OrganizationUseCase:

    from use_cases.organization.create_use_case import create_organization_with_first_user
    from use_cases.organization.delete_use_case import delete_organization
    from use_cases.organization.get_use_case import (
        get_organizations,
        get_organization,
        get_first_organization,
    )
    from use_cases.organization.owner_use_case import patch_organization_owner
    from use_cases.organization.patch_organization_use_case import patch_organization

    def __init__(self):
        pass
