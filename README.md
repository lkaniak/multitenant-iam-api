# Multitenant IAM API

Identity and access management for multiple organizations: users, roles, groups, JWT sessions, MFA, and tenant alert rules.

Outbound delivery is not part of this app. It depends on the workspace package [`packages/notification-service`](packages/notification-service), which sends a generic notification over HTTP. Directory layout and the structural concepts are in [docs/architecture.md](docs/architecture.md). Tenant access, alerts, and the request path are in [docs/api_design.md](docs/api_design.md). The package README covers why that package exists and how to extract it.

## Setup

Requires Python 3.10 or 3.11.

```bash
uv sync
```

Copy `.env.example` to a local env file, fill the values, and export them before starting the app (settings are read from the environment).

| Variable | Purpose |
|---|---|
| `MONGO_URI` | MongoDB connection string |
| `MONGO_DATABASE_NAME` | Database name |
| `AUTH_SECRET_KEY` | JWT signing key |
| `AUTH_ALGORITHM` | JWT algorithm, for example `HS256` |
| `MFA_SECRET_KEY` | Key material for MFA codes |
| `EXPIRATION_MFA_OTP_CODE_IN_SECONDS` | MFA code lifetime |
| `API_URL` | This API’s URL, used as a JWT audience |
| `APP_CLIENT_URL` | Browser client origin, also a JWT audience and a CORS origin |
| `CORS_ALLOWED_ORIGINS` | Optional comma-separated extra origins |
| `API_VERSION` | Optional path prefix (`root_path`) |
| `DEBUG` | `true` to run uvicorn from `python src/main.py` |
| `TRACKING_LOG_PII` | `true` logs request bodies without redaction |

Notification delivery uses its own variables, not these. Set `NOTIFICATION_HTTP_BASE_URL` and, if needed, `NOTIFICATION_HTTP_API_KEY`. Details are in [`packages/notification-service/README.md`](packages/notification-service/README.md).

## Run

```bash
cd src
uv run uvicorn main:app --reload --port 8150
```

Or start MongoDB, the API, and a local notification receiver:

```bash
docker compose up --build
```

The API listens on port 8150. The receiver prints notification bodies and answers `204` so MFA and user-creation sends succeed. OpenAPI is served at `/docs` (under `API_VERSION` when that prefix is set).

Tests are not run on push. Start the [Tests workflow](.github/workflows/tests.yml) manually from the Actions tab when you want a demo run.

This project is licensed under the [MIT License](LICENSE.md).
