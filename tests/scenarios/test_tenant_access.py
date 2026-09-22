from presentation.dependencies.notification_service import get_notifications

from tests.scenarios.support import PASSWORD, auth, create_alert, login, seed_tenant


def _recorder(client):
    return client.app.dependency_overrides[get_notifications]()


def test_failed_login_notifies_the_tenant_alert(client):
    tenant = seed_tenant()
    owner_token = login(client, "olivia")
    create_alert(client, owner_token, tenant["organization"].id, "Failed logins", "login_failed")
    _recorder(client).sent.clear()

    response = client.post("/auth/", data={"username": "mia", "password": "WrongPass1!"})

    assert response.status_code == 401
    events = _recorder(client).of_event("login_failed")
    assert len(events) == 1
    assert events[0].destination == "https://hooks.example/login_failed"
    assert events[0].payload["data"]["username"] == "mia"


def test_member_is_denied_an_admin_route_and_the_denial_is_alerted(client):
    tenant = seed_tenant()
    owner_token = login(client, "olivia")
    create_alert(
        client, owner_token, tenant["organization"].id, "Denied access", "permission_denied"
    )
    member_token = login(client, "mia")
    _recorder(client).sent.clear()

    response = client.get("/users/app", headers=auth(member_token))

    assert response.status_code == 403
    events = _recorder(client).of_event("permission_denied")
    assert len(events) == 1
    assert events[0].payload["data"]["username"] == "mia"


def test_owner_creates_a_user_then_changes_their_role(client):
    tenant = seed_tenant()
    owner_token = login(client, "olivia")
    create_alert(
        client, owner_token, tenant["organization"].id, "Role changes", "user_role_changed"
    )
    _recorder(client).sent.clear()

    created = client.post(
        "/user",
        headers=auth(owner_token),
        json={
            "organization_id": tenant["organization"].id,
            "username": "noah",
            "password": PASSWORD,
            "role": "regular",
            "user_type": "other",
            "contact_info": {
                "email": "noah@acme.test",
                "first_name": "Noah",
                "job_position": "analyst",
                "activity_area": "security",
                "affiliation_type": "internal",
            },
        },
    )
    assert created.status_code == 201, created.text
    created_user = created.json()
    notices = _recorder(client).of_kind("user_created")
    assert len(notices) == 1
    assert notices[0].destination == "noah@acme.test"

    _recorder(client).sent.clear()
    patched = client.patch(
        "/user",
        headers=auth(owner_token),
        json={"id": created_user["id"], "role": "admin"},
    )
    assert patched.status_code == 200, patched.text
    role_alerts = _recorder(client).of_event("user_role_changed")
    assert len(role_alerts) == 1
    assert role_alerts[0].payload["data"]["old_role"] == "regular"
    assert role_alerts[0].payload["data"]["new_role"] == "admin"
