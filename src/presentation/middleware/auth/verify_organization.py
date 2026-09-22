from bson import ObjectId

from entities.exceptions.organization_exceptions import InvalidOrganizationException
from entities.exceptions.invalid_id_exception import InvalidIdException
from use_cases.auth.authorization_use_case import AuthorizationUseCase


def verify_organization(organization_id: str) -> str:
    if not ObjectId.is_valid(organization_id):
        raise InvalidIdException(which_parameter="organization_id")

    if organization := AuthorizationUseCase.organization_id_exists(organization_id):
        return organization.id

    raise InvalidOrganizationException()
