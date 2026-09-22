from entities.enum.role_enum import RoleEnum
from entities.enum.user_type_enum import UserTypeEnum
from entities.organization_entity import OrganizationEntity
from entities.user_entity import UserContactInfoEntity, UserEntity
from infra.database import get_database
from infra.repositories.organization_repository import OrganizationRepository
from infra.repositories.user_repository import UserRepository
from use_cases.user.user_helpers import encrypt_password

PASSWORD = "ValidPass1!"


def _contact(first_name, email):
    return UserContactInfoEntity(
        first_name=first_name,
        last_name="Acme",
        email=email,
        job_position="director",
        activity_area="security",
        affiliation_type="internal",
    )


def seed_tenant():
    db = get_database()
    db.organization_collection.drop()
    db.user_collection.drop()
    db.alerts_collection.drop()
    db.channel_collection.drop()
    organization = OrganizationRepository().create_organization(
        OrganizationEntity(
            name="Acme",
            created_at="2026-01-01",
            organization_plan="basic",
            inactive=False,
            registration_origin="default",
        )
    )
    owner = UserRepository().create_user(
        UserEntity(
            organization_id=organization.id,
            username="olivia",
            password=encrypt_password(PASSWORD),
            role=RoleEnum.OWNER.value,
            user_type=UserTypeEnum.OTHER.value,
            contact_info=_contact("Olivia", "olivia@acme.test"),
        )
    )
    member = UserRepository().create_user(
        UserEntity(
            organization_id=organization.id,
            username="mia",
            password=encrypt_password(PASSWORD),
            role=RoleEnum.REGULAR.value,
            user_type=UserTypeEnum.OTHER.value,
            contact_info=_contact("Mia", "mia@acme.test"),
        )
    )
    return {"organization": organization, "owner": owner, "member": member}


def login(client, username):
    from presentation.dependencies.notification_service import get_notifications

    challenge = client.post("/auth/", data={"username": username, "password": PASSWORD})
    assert challenge.status_code == 200, challenge.text
    recorder = client.app.dependency_overrides[get_notifications]()
    code = recorder.sent[-1].payload["temporary_otp_code"]
    validated = client.post(
        "/auth/validate_mfa_otp_code",
        data={
            "username": username,
            "password": PASSWORD,
            "temporary_otp_code": code,
        },
    )
    assert validated.status_code == 200, validated.text
    return validated.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def create_alert(client, token, organization_id, name, event_type):
    response = client.post(
        "/alerts",
        headers=auth(token),
        json={
            "organization_id": organization_id,
            "name": name,
            "event_type": event_type,
            "enabled": True,
            "channels": [
                {
                    "type": "webhook",
                    "destination": f"https://hooks.example/{event_type}",
                    "enabled": True,
                }
            ],
        },
    )
    assert response.status_code == 201, response.text
    return response.json()
