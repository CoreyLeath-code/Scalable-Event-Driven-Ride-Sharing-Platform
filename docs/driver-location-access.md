# Driver-location API access

The driver-location API may return geographic coordinates. To avoid disclosing
driver locations to unauthenticated callers, all `/driver-location/drivers*` and
`/driver-location/count` endpoints require the `X-Driver-API-Key` header.

1. Copy `.env.example` to `.env`; generate a strong key with
   `openssl rand -hex 32` and set `DRIVER_LOCATION_API_KEY`.
2. Run `docker compose up --build`. With an empty/unset key, sensitive routes
   fail closed with HTTP 503, not a permissive default.
3. Call `curl -H "X-Driver-API-Key: $DRIVER_LOCATION_API_KEY" http://localhost:8000/driver-location/count`.
   Health/readiness endpoints intentionally remain unauthenticated.
4. Compose binds the gateway to `127.0.0.1` by default. Do not make it public
   without TLS, network restrictions, and stronger per-user authentication.

This shared key is a minimum safety measure for a local portfolio/demo
deployment. It is **not** a replacement for per-user authorization, a tenant
boundary, or production identity management. Do not log the key or commit
`.env`. Rotate the key if exposed.
