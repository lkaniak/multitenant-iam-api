# Architecture

## Directories

### Notification package

`packages/notification-service` is a workspace member. Its import name is `notification_service`. It does not import the API.

```text
packages/notification-service/
├── README.md
├── pyproject.toml
├── notification_sink.py     # local HTTP receiver used by Docker Compose
└── notification_service/
    ├── __init__.py          # exports Notification, NotificationPort, HttpNotificationAdapter
    ├── models.py            # generic message and the send port
    └── http_adapter.py      # POST implementation and its own env settings
```

`models.py` is the contract: a channel, a destination, and a JSON payload. `http_adapter.py` is the only sender. An absolute `http` or `https` destination receives the payload (webhook or Slack). Any other destination is posted to `{NOTIFICATION_HTTP_BASE_URL}/notifications` as the full message, with an optional API key header.

### Multitenant API

The API lives under `src/` and is run with that directory on `PYTHONPATH`. Dependencies point inward: routers call use cases, use cases call repositories and the notification port. The notification package is the one outbound dependency.

```text
src/
├── main.py                  # FastAPI app, CORS, routers, exception handlers
├── config.py                # environment settings for this API only
├── common/
│   ├── data/                # dictionary merge helpers
│   └── security/            # permission strings and request redaction
├── entities/
│   ├── enum/                # roles, user types, plans, alert events
│   └── exceptions/          # application errors with stable codes
├── infra/
│   ├── database/            # shared Mongo client and its connection pool
│   └── repositories/        # collection access for orgs, users, groups, alerts
├── presentation/
│   ├── dependencies/        # composition root (notification port)
│   ├── handler/             # HTTP mapping for application exceptions
│   ├── middleware/          # token checks, privilege checks, request tracking
│   ├── request/             # inbound payloads and filters
│   ├── response/            # outbound models
│   └── routers/             # HTTP routes
├── services/
│   └── alert/               # loads tenant alert rules and calls the port
└── use_cases/
    ├── auth/                # login, MFA, JWT, privilege decisions
    ├── organization/
    ├── organization_user_groups/
    ├── user/
    └── alert/               # alert configuration CRUD
```

Tests sit beside `src/`, not inside it. `tests/coverage` exercises units. `tests/scenarios` drives the HTTP API against an in-memory database.

How tenants, access, alerts, and requests are shaped is in [api_design.md](api_design.md).

## Concepts

The API is one deployable process. Inside it, each capability is a module with its own use cases, routes, and repositories. Auth, users, organizations, groups, and alerts share `entities` and `infra`. They do not share each other's workflows. That is a modular monolith: one codebase and one database, with boundaries you can read in the directory tree. `notification-service` sits outside those boundaries on purpose.

### Use cases

A use case is one operation: create a user, deny a privilege, mint a token. Each operation lives in its own file under `use_cases/<module>/`. The module class (`UserUseCase`, `OrganizationUseCase`, and the others) imports those functions onto itself, so a router calls `UserUseCase().create_user(...)` while the steps stay in a file that does only that job.

Routers do not contain those steps. Repositories do not decide whether a caller is allowed to take them. The use case calls repositories, and it calls the notification port when the operation has something to send.

### Dependency injection

The notification sender is the dependency that changes. `NotificationPort` is the contract in the package. `HttpNotificationAdapter` is the implementation that posts HTTP. The API chooses the implementation in `presentation/dependencies/notification_service.py`, and FastAPI `Depends` supplies that object to the route. The route passes it into the use case. Use cases type the argument as the port, so they do not construct an HTTP client and do not read `NOTIFICATION_HTTP_BASE_URL`.

Route guards are built the same way. `RoleAndTypeChecker` and `PrivilegesChecker` are callables FastAPI invokes per request, with the authenticated user and the notification port filled in. A route declares the guard it needs. It does not look up a global sender.

Repositories are not injected. Every request uses the same database, so a repository constructs itself and asks `infra.database` for it.

### Concurrency

Sync routes run on a thread pool. One `MongoClient` is shared by all of those threads. The client is created once, behind a lock, and it keeps a connection pool. Each query checks a connection out of the pool and returns it when the operation finishes. A request does not own a database handle, and nothing is stored on the task or the thread to remember which database to use.

Outbound HTTP is short-lived. `HttpNotificationAdapter` opens a client for one post and closes it. A missing base URL, a connection error, a timeout, or a non-2xx response raises `NotificationDeliveryError`. What the API does with that error depends on whether the message is part of the operation.

### Transactional notifications

Some sends are required for the operation to count. The use case writes first, then sends. If the send fails, it undoes the write and the request ends with HTTP 424.

- Creating a user sends `user_created`. Failure deletes that user. A batch create deletes every user from that batch. A system admin skips this mail, so this rollback does not apply.
- Creating an organization sends `organization_created` after the organization and its first users exist. Failure deletes the organization.
- MFA login sends `mfa_otp` before any token exists. Failure issues no token.
- Password reset stores a temporary password, then sends `password_reset`. Failure writes the previous password value back.

Alert delivery is not part of the operation. It runs after the action has succeeded. `AlertDispatchService` logs a failed load or a failed channel and continues with the next channel. The original request still succeeds.
