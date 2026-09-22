# notification-service

Generic outbound notification sender. It is a workspace package so the multitenant IAM API can deliver messages without owning delivery.

## Why it exists

Creating a user, resetting a password, or fanning an alert out to email, a webhook, or Slack is not identity and access management. Those are messages. Keeping them in the IAM app couples tenant rules to HTTP clients, URLs, and provider payloads.

This package owns that boundary. The IAM app decides that something happened and maps it to a generic notification. This package sends it.

## What it demonstrates

- A small port (`NotificationPort.send`) with one adapter (`HttpNotificationAdapter`).
- Dependency injection at the IAM app edge: routers depend on the port, use cases receive it, and neither constructs an HTTP client.
- A monorepo split. The IAM app depends on this package. This package does not import the IAM app, so it does not know organizations, users, roles, MFA, or alerts.

A notification is only:

- `channel` — how the caller classifies the message (`email`, `webhook`, `slack`, or anything a future adapter understands)
- `destination` — an address, or an absolute `http`/`https` URL
- `payload` — JSON the caller already shaped

## How sending works

`HttpNotificationAdapter` reads its own settings from the environment:

- `NOTIFICATION_HTTP_BASE_URL` — provider base URL for destinations that are not absolute URLs (email and other provider-backed channels). The adapter POSTs the full notification to `{base URL}/notifications`.
- `NOTIFICATION_HTTP_API_KEY` — optional `X-API-Key` header.

If `destination` is an absolute HTTP(S) URL, the adapter POSTs `payload` to that URL instead. That covers tenant webhooks and Slack incoming webhooks. The IAM app does not configure a notification URL.

## Extraction and expansion

This package is not the focus of the multitenant API. It can leave the workspace and become its own repository: publish it, point the IAM app at the released distribution, and keep the same `send` call.

Expansion stays here. A second adapter (SMTP, a provider SDK) implements `NotificationPort` and the IAM app keeps mapping events to `Notification`. New channels are new `channel` values and payload shapes chosen by the caller, not new IAM endpoints.
