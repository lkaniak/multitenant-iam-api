# API design

A tenant is an organization. Users, groups, alerts, and activity rows store that organization's id. The access token carries the same id. A request is in one tenant at a time: the token's organization, not a header the client can swap.

Isolation is enforced in the application, in one MongoDB database. Repositories filter by organization id. There is no database or schema per tenant. That keeps the demo one process and one connection string. The cost is that a missed filter is a cross-tenant read, so organization checks sit in the use cases and in token validation, not only in a query convention.

## Access model

Two axes combine into a permission string, `user_type:role`.

- **Role** is ownership inside a tenant: `owner`, `admin`, or `regular`. Owners and admins manage users. A regular user does not.
- **User type** is `system_admin` or `other`. A system admin operates across tenants. Everyone else is bound to organizations they belong to.

Organization user groups are how a non-admin user is allowed into more than one tenant. Changing organization issues a new token for the requested organization after that membership is checked. The group list is not a second permission system. It only answers "may this user enter this tenant?"

JWT is issued and verified by this API. The audience is this API and the browser client, so a token minted for one of those URLs is rejected by the other check. Session lifetime is fixed in the authentication use case. This is a closed demo API, not a federated identity provider, so there is no OIDC or external authorization server.

Passwords are hashed with PBKDF2-SHA512 from the standard library. A random salt and the iteration count are stored with the digest. Verification uses a constant-time compare. MFA codes are time-based one-time passwords derived from `MFA_SECRET_KEY` and the username, then sent as a notification. The code is not stored.

## Alerts and notifications

Alerts and notifications are different objects.

An **alert** is tenant configuration: when this IAM event happens, deliver to these channels. Events are user created, user deleted, role changed, login failed, and permission denied. Channels are email, webhook, or Slack. Administrators CRUD them through `/alerts`. Dispatch looks up enabled alerts for the event and the organization, then asks the notification port to send. A failed delivery is logged and does not fail the user action.

A **notification** is one outbound message: channel, destination, and payload. The API builds that message at the edge of a use case (welcome mail, password reset, MFA code, or an alert fan-out). It does not know URLs, status codes, or providers.

That split is why `notification-service` is a package. Delivery will grow (SMTP, a hosted provider) without new IAM concepts, and the package can be published on its own. The API depends on `NotificationPort`. Routers obtain the HTTP adapter from `presentation/dependencies` and pass it in. Use cases do not construct a client and do not read a notification base URL.

## Request path

`presentation` is the HTTP edge: routes, body models, and middleware. Middleware resolves the bearer token to a user, checks the role and user type for the route, and checks finer privileges when the target user or organization is only known after the body is read. Tracking middleware logs the request and redacts passwords, tokens, and contact fields unless `TRACKING_LOG_PII` is set.

Use cases are the decisions: create the user, decide the denial, mint the token. They call repositories and the notification port. Repositories are the only MongoDB queries. They share one `MongoClient`. PyMongo checks a connection out of that pool for each operation, so concurrent requests do not take turns on a request-local handle.

Entities are the shared shapes (Pydantic models and enums). Request and response models stay in `presentation` so HTTP field names can change without rewriting the stored document.
