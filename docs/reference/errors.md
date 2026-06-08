# Error handling

> **Reference.** The error response shape and how to react. The catalogue of concrete error types is a
> known gap (#5).

## Response shape — Problem (RFC 9457-style)

Errors are returned as `application/problem+json` using the `Problem` schema from the
[OpenAPI spec](../openapi/README.md):

```json
{
  "type": "/some/uri-reference",
  "title": "some title for the error situation",
  "status": 422,
  "detail": "a human-readable explanation specific to this occurrence",
  "instance": "/some/uri-reference#specific-occurrence-context"
}
```

| Field | Meaning |
| --- | --- |
| `type` | URI reference identifying the **problem type**, unique within this API. Note: unlike strict RFC 9457, it is *not* guaranteed to be dereferenceable or globally unique — treat it as an opaque, API-local category. |
| `title` | Short English summary for engineers. Not localized, not end-user-facing. |
| `status` | The HTTP status code, duplicated in the body. |
| `detail` | Occurrence-specific English explanation to help locate the problem. |
| `instance` | URI reference identifying this specific occurrence. |

`title` and `detail` are written for engineers, in English, and are **not** suitable to show to end users
verbatim.

## Reacting to errors

General guidance until the catalogue lands:

| Status | Likely cause | What to do |
| --- | --- | --- |
| `401` | Missing/expired token. | Re-request a token (see [authentication](authentication.md)); retry once. |
| `403` | Token lacks `wwimmo:dms:api` scope or `customerid`. | Stop and fix credentials/scope — do not retry blindly. |
| `404` | Unknown id / secondary key. | Treat as "not present"; don't retry. |
| `422` | Validation problem in the payload. | Inspect `detail`, fix the request; do not retry unchanged. |
| `429` | Rate limited. | Back off; honour `Retry-After` if present. |
| `5xx` | Server-side. | Retry with backoff; safe because operations are intended to be idempotent. |

## 🚧 NEEDS INPUT (gap #5)

- The **catalogue of `type` values** the API actually emits, each with: meaning, the status it pairs with,
  and concrete recovery advice.
- Whether validation errors return field-level detail (e.g. an `errors[]` array) beyond `detail`.
- Confirmation of which HTTP statuses each endpoint can return (the spec currently shows only `200` and a
  generic `default` problem on master-data endpoints).
