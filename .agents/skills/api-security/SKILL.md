---
name: api-security
description: Owns API-layer security — authentication, authorization, JWT, OAuth 2.0, RBAC, rate limiting, CORS, request validation, and API abuse prevention — for REST, GraphQL, and webhook endpoints.
version: 0.1.0
---

# API Security

Owns security for application programming interfaces across REST, GraphQL, gRPC, webhooks, and serverless endpoints. Activates when a change touches an API route, auth token, rate limit, CORS policy, or any caller-influenced request path.

## Purpose

Ensure every API endpoint authenticates callers correctly, authorizes them per-resource, validates requests completely, and resists abuse — without leaking internals or weakening existing controls.

## Scope

Owns:

- Authentication: session vs token trade-offs, cookie flags (`HttpOnly`, `Secure`, `SameSite`), bearer tokens, API keys, OAuth 2.0 flows, OIDC, mTLS where applicable
- Authorization: RBAC, ABAC, object-level ownership checks, confused-deputy prevention, IDOR protection
- JWT: signing algorithms, expiration, audience/issuer validation, revocation, rotation, storage guidance
- OAuth 2.0: grant type selection, redirect URI allowlists, scope minimization, PKCE for public clients
- RBAC: role definition, least privilege, role inheritance, separation of duties
- Rate limiting: per-IP, per-identifier, per-API-key, burst vs sustained, fail-open vs fail-closed
- CORS: origin allowlists, credentials handling, preflight, exposed headers
- Request validation: schema, content type, body size, query params, headers, method allowlisting
- API abuse prevention: scraping, credential stuffing, enumeration, business-logic abuse, webhook replay
- Error handling: generic messages, no stack traces, no internal hostnames, consistent status codes

Does NOT own:

- General application-layer input validation → application-security (this skill applies it to API request shapes)
- Database/session/secrets implementation → backend-security
- Client-side token storage → frontend-security
- Infrastructure/TLS/deployment config → infrastructure-security
- Vulnerability audit methodology → security-audit

## When This Skill Activates

- Adding or changing any API route, especially public or state-mutating ones
- Introducing auth, sessions, tokens, API keys, or webhook secrets
- Changing CORS, rate limiting, or authentication middleware
- Accepting caller-influenced query parameters, headers, or body fields
- Building a webhook receiver or third-party integration endpoint
- Reviewing an API for enumeration, scraping, or abuse exposure

## Core Responsibilities

1. Gate every privileged API operation server-side, including object-level ownership — identity is not authorization.
2. Validate every request against a schema before it reaches business logic.
3. Constrain authentication tokens: verify signature, expiration, audience, issuer; reject missing/empty tokens.
4. Apply rate limiting and abuse controls to public write endpoints and paid-resource consumers.
5. Configure CORS with explicit origin allowlists; never reflect arbitrary origins.
6. Return generic, non-leaking errors; never stack traces or internal hostnames to callers.
7. Distinguish confirmed vulnerabilities from potential risks; report with exploit path and impact.

## Engineering Principles

- **Authentication is not authorization.** Knowing who calls does not mean they may touch this resource.
- **Deny by default.** Protection is evident from the first line of the handler, not a helper the reader must trace.
- **Validate before business logic.** Reject malformed requests early; never read raw request deep in the stack.
- **Short-lived tokens.** Minimize token lifetime; rotate and revoke on compromise or logout.
- **Least privilege scopes.** OAuth scopes and API keys grant only what is necessary.
- **Constant-time comparison.** Compare presented secrets/tokens without timing leakage.
- **Fail closed.** A missing auth dependency blocks access; fail open only for defense-in-depth signals, explicitly logged.

## Decision-Making Framework

| Question | Correct answer |
| :--- | :--- |
| Session or JWT? | Session for server-rendered/browser apps; JWT/bearer for stateless APIs and mobile clients. |
| OAuth grant? | Authorization Code + PKCE for public clients; Client Credentials for machine-to-machine. |
| CORS origins? | Explicit allowlist; never reflect `Origin` or use `*` with credentials. |
| Rate limit by what? | Server-side identifier (API key, authenticated user ID); IP as secondary weak signal only. |
| Fail open or closed? | Closed for auth/authz; open only for non-critical defense-in-depth, logged explicitly. |
| Confirmed vs potential? | Confirmed = reproducible unauthorized access; potential = missing control without demonstrated exploit. |

## Workflow

1. Enumerate API boundaries: which routes are public vs authenticated, which mutate state, which call paid services.
2. Apply authentication: verify token/session on every authenticated route, constant-time comparison.
3. Apply authorization: RBAC role check plus object-level ownership on every method of a resource.
4. Validate request: schema, content type, body size, query params, headers, allowed methods.
5. Apply rate limiting: per-identifier and per-IP independent limits; return 429 on breach.
6. Configure CORS: explicit origin allowlist, credentials only with same-origin or allowlisted origins.
7. Handle errors: generic messages, correct status codes (401/403/429/400/500), no internals.
8. Report findings with exploit path, impact, and specific fix; verify fix executes on failure branch.

## Implementation Guidelines

- Verify tokens with constant-time comparison; missing/empty token = rejection, not comparison.
- Cap request body size, query parameter length, header size, and nesting depth.
- Allowlist HTTP methods per route; reject others with 405.
- Allowlist content types; reject unexpected types with 415.
- Constrain webhook receivers: verify signatures, reject replay (timestamp + nonce), idempotency keys.
- Return 429 with `Retry-After` on rate limit; keep per-user and per-IP limits independent.
- Never reflect user input in error messages, `WWW-Authenticate` challenges, or `Location` headers without validation.
- Machine callers (automation tokens, webhooks) are authenticated and authorized as strictly as browsers.

## Security Requirements

- Authenticate every non-public API route server-side; verify token signature, expiration, audience, issuer.
- Authorize every privileged operation server-side, including object-level ownership of the specific resource.
- Validate every request against a schema (type, format, length, range, allowed values) before business logic.
- Apply rate limiting to public endpoints that write state or consume paid resources; return 429.
- Configure CORS with explicit origin allowlist; no credential reflection of arbitrary origins.
- Use short-lived tokens; rotate on logout/compromise; revocation mechanism present.
- Compare secrets/tokens in constant time.
- Return generic errors; no stack traces, SQL, or internal hostnames to callers.
- Apply auth/authz/validation to machine-initiated callers as strictly as to browsers.

## Performance Considerations

- Auth checks are on the hot path; keep verification cheap, cache expensive verification with short TTL.
- Rate limiting needs shared state across instances; in-process counters reset on cold start (speed bump, not control).
- Validate before expensive operations (embeddings, third-party calls, image processing).
- Token revocation checks should not add blocking network round-trips on every request unless required.

## Reliability Considerations

- Auth dependency failure must fail closed and legibly, not silently permit traffic.
- Rate limiters degrade predictably (429, backoff) under burst, not opaquely.
- Do not let a security control silently swallow the error path it protects; verify it executes on failure.
- Misconfigured CORS/auth fails safe: missing config disables the feature predictably.

## Testing Requirements

- Test authorization with a second unauthorized identity and a resource owned by someone else (IDOR).
- Test each auth failure mode: missing token, expired token, wrong audience/issuer, revoked token.
- Test rate limiting with burst traffic; confirm 429, not unbounded acceptance or crash.
- Test CORS: disallowed origin rejected, credentials not reflected for non-allowlisted origins.
- Test webhook signature verification and replay protection (old timestamp, reused nonce).
- Test that error responses leak no internals (no stack traces, no upstream hostnames).
- Verify constant-time comparison does not leak via response timing.

## Observability Requirements

- Log authorization denials with actor, target, resource, and reason.
- Log rate-limit events and auth failures by category (distinguish attack from buggy client).
- Log every token validation failure and webhook rejection.
- Alert on new public routes, new outbound webhook targets, new API keys, and changed CORS origins.
- Ensure logs contain no tokens, authorization headers, or personal data.

## Common Failure Modes

- Identity verified but object ownership never checked (IDOR via path parameter).
- JWT accepted without signature/expiration/audience verification.
- CORS reflecting arbitrary `Origin` with `Access-Control-Allow-Credentials: true`.
- Public write endpoint with no rate limit and truthiness-only validation.
- API key compared with non-constant-time comparison or logged in plaintext.
- Webhook receiver accepting unsigned or replayed payloads.
- Error messages returning stack traces, SQL, or internal hostnames.
- Rate limit per-instance in serverless treated as real enforcement.
- Automation token treated as a "lesser user" with weaker validation.

## Troubleshooting

For suspected authz bypass, enumerate every method and path parameter on the resource and check each for an ownership check. For suspected JWT bypass, confirm signature, expiration, audience, and issuer are verified — not just presence. For CORS issues, check whether arbitrary origins are reflected and whether credentials are sent with non-allowlisted origins. For rate limiting that seems bypassed, confirm limits are server-side (not client fingerprint) and shared across instances. After a fix, re-test the unauthorized path and the legitimate path, and confirm the control executes on the failure branch.

## Tool Usage

Read the actual route handler, the auth middleware it calls, and the authorization/ownership check. Most findings live in the gap between those three. Verify with an actual request (unauthorized identity, tampered token, disallowed origin) — never report a control as present because middleware is imported; confirm it runs on the path that matters.

## Interaction With Other Skills

- **application-security**: this skill applies application controls to API request/response shapes; application-security owns general validation/encoding principles.
- **backend-security**: coordinates on session storage, token revocation, and server-side auth implementation.
- **frontend-security**: defines safe client-side token storage (HttpOnly cookies vs localStorage trade-offs) and API call hygiene.
- **infrastructure-security**: hands off TLS termination, API gateway config, WAF, and edge rate limiting.
- **security-audit**: this skill provides remediation patterns; security-audit runs API discovery and severity.
- **dependency-security**: coordinates on auth library and framework version risk.

## Expected Output

An API review where every route's authN/authZ is named, every request is validated against a schema before logic, every privileged operation checks object ownership, rate limiting and CORS are configured with explicit allowlists, errors leak no internals, and findings carry exploit path, impact (confirmed vs potential), and specific fix — ordered by impact.

## Examples

**Request**: "Add a `PATCH /api/users/:id` endpoint to update profile fields."

**Approach**: Authenticate via bearer token/session → authorize: caller must own the user record (`req.user.id === :id` or admin role) → validate request body against schema (allowed fields only, length/format bounds, no mass-assignment of `role`/`isAdmin`) → apply rate limit per-user → return 404/403 generically (don't reveal whether user exists) → test with a second user's ID confirming 403, test mass-assignment attempt confirming `role` ignored → document the ownership check so a future field addition doesn't bypass it.

**Request**: "Configure CORS for a public API consumed by a mobile app and a partner domain."

**Approach**: Explicit origin allowlist (`https://app.example.com`, `https://partner.example.com`) → no `*` when credentials are used → `Access-Control-Allow-Origin` echoes only allowlisted origins, never reflects request `Origin` → preflight handled with allowed methods/headers → test disallowed origin is rejected → test allowlisted origin with credentials succeeds → log CORS rejections by category.
