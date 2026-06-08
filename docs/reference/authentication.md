# Authentication & authorization

> **Reference.** How a partner obtains and uses credentials. Auth is chronically under-documented and a
> top source of support tickets — so this is deliberately concrete. Implementation details reflect the
> current Polaris backend; anything not yet confirmed for production is marked **🚧 NEEDS INPUT**.

## Model at a glance

- **Protocol:** OAuth 2.0 **client credentials** (machine-to-machine). No interactive user login.
- **Identity provider:** **Cidaas** (OIDC).
- **Token type:** JWT Bearer, sent as `Authorization: Bearer <token>`.
- **Required scope:** `wwimmo:dms:api`. Tokens without it are rejected (`403`).

## Getting a token

The API exposes a **token proxy** so partners talk to one endpoint and don't need to know Cidaas internals:

```
POST {base-url}/api/v1/dms/token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials
client_id=<your client id>
client_secret=<your client secret>
```

The proxy forwards the request to Cidaas with `grant_type=client_credentials` and
`scope=wwimmo:dms:api`, discovering the Cidaas token endpoint via OIDC discovery (cached ~1h). It is
**rate limited to 30 requests/minute per IP** — cache and reuse your token until it expires.

Response is a standard OAuth token payload (`access_token`, `token_type=Bearer`, `expires_in`, …).

> A separate `POST /api/v1/dms/dev/token` exists for **local development only** (mock tokens). It is not
> available in production and partners never use it.

## Using the token

Send it on every request:

```
GET {base-url}/api/v1/dms/documents?changed_since=2026-01-01T00:00:00Z
Authorization: Bearer <access_token>
```

### Claims and scoping

- The token's **`client_id` becomes the `aud` claim**; audience validation is intentionally disabled
  because each customer has a unique client. Issuer and signature (JWKS) are validated normally.
- `customerid` claim scopes data to the customer. Endpoints that need it reject tokens without it (`403`,
  policy `RequireCustomerId`).
- `scopes` must contain `wwimmo:dms:api` (policy `DmsApiAccess`).

## 🚧 NEEDS INPUT

1. **Base URLs per environment** (gap #1). The OpenAPI `servers` entry is `https://erp.wwimmo.ch/api/v1/dms`;
   the live dev POC is `https://polaris.wwportal-dev.ch`. Confirm the canonical dev / test / prod hosts.
2. **Credential onboarding** (gap #2). How does a partner *get* its `client_id` / `client_secret`? Who
   issues them, through what process, and how are they rotated/revoked? — Sandro Brunner (Cidaas).
3. **Token lifetime** — confirm `expires_in` and whether refresh applies (client_credentials usually
   re-requests rather than refreshes).
4. **Cidaas issuer host(s)** partners should expect in the `iss` claim (e.g. `wwimmo-test.cidaas.eu` vs prod).
