# API Proxy Error Analysis

## Problem Summary

The setup script (`scripts/setup.sh`) reports an HTTP 502 error when testing the API endpoint at `http://localhost:8080/v1/chat/completions`, even though the API itself is confirmed to be running and accessible at `127.0.0.1:8080/v1`.

## Root Cause

The HTTP 502 error is **not** caused by the setup script or the API server directly. Instead, it originates from a **reverse proxy** sitting in front of the API server.

### Error Response

```json
{
  "error": {
    "message": "Upstream proxy failed: Too much data for declared Content-Length",
    "type": "PROXY_CONNECTION_ERROR",
    "code": 502
  }
}
```

### What This Means

The reverse proxy (e.g., nginx, Traefik, Caddy) forwarding requests to your OpenAI-compatible API on port 8080 encountered a mismatch:

- The upstream API server declared a `Content-Length` header indicating a certain response size.
- The actual response body sent by the upstream server was **larger** than the declared `Content-Length`.
- The proxy, unable to reconcile this mismatch, returned a 502 Bad Gateway error.

### Why Simple Endpoints Work But POST Fails

- **GET requests** (e.g., `GET /v1`) typically return small responses (or just a 404), so the Content-Length mismatch doesn't occur.
- **POST requests** to `/v1/chat/completions` generate larger responses (model output), triggering the proxy's Content-Length validation and causing the 502 error.

## Affected Component

| Component | Status |
|-----------|--------|
| Setup script (`scripts/setup.sh`) | ✅ Working correctly |
| `.env` configuration | ✅ Correctly configured |
| API server (port 8080) | ✅ Running and accessible |
| Reverse proxy in front of API | ❌ Misconfigured |

## Resolution Steps

### Option 1: Fix the Proxy Configuration

If using **nginx**, add or adjust the following in your server block:

```nginx
location /v1/ {
    proxy_pass http://127.0.0.1:8080;
    proxy_buffering off;
    proxy_request_buffering off;
}
```

If using **Traefik**, ensure the upstream service doesn't have conflicting content encoding middleware.

### Option 2: Bypass the Proxy Temporarily

Update `.env` to point directly to the API server without going through the proxy:

```env
API_BASE=http://127.0.0.1:<direct-api-port>
```

### Option 3: Check the Upstream API Server

Review the API server logs for errors related to:
- Response encoding issues
- Incorrect `Content-Length` header calculation
- Chunked transfer encoding conflicts

## Verification

After applying a fix, re-run the setup script to confirm the API check passes:

```bash
bash scripts/setup.sh
```

Expected output:
```
[5/5] Checking API connectivity...
  Testing: http://localhost:8080/v1/chat/completions
  ✓ API is reachable and responded with HTTP 200.