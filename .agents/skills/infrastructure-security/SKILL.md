---
name: infrastructure-security
description: Owns infrastructure and configuration security — environment variables, Docker security, HTTP security headers, TLS, and deployment configuration — for any deployment target.
version: 0.1.0
---

# Infrastructure Security

Owns the environment surrounding the application: configuration, container images, transport security, headers, and deployment settings. Activates when a change touches environment variables, Dockerfiles, server headers, TLS certificates, CI/CD deployment, or hosting configuration.

## Purpose

Ensure the infrastructure layer enforces secure defaults: secrets never exposed, containers run unprivileged, transport is encrypted, headers protect the browser, and deployment configuration doesn't weaken application controls.

## Scope

Owns:

- Environment variables: secret vs public (`NEXT_PUBLIC_*` semantics), no secrets in code/repo, no secrets in logs/errors, per-environment values
- Docker security: non-root user, minimal base images, no secrets in layers, read-only filesystems where possible, resource limits
- HTTP security headers: CSP, `X-Frame-Options`, `X-Content-Type-Options: nosniff`, `Strict-Transport-Security`, `Referrer-Policy`, `Permissions-Policy`
- TLS: enforced HTTPS, HSTS, certificate management, weak cipher/protocol disablement, mixed-content prevention
- Deployment configuration: CI/CD secrets handling, least-privilege deployment roles, zero-downtime/security regression gates, rollback
- Cloud/metadata exposure: blocking instance metadata endpoints from app reach, least-privilege IAM roles
- Secure defaults: configurations ship secure without opt-in

Does NOT own:

- Application-layer input validation/encoding → application-security
- API auth/protocol → api-security
- Server-side DB/session/secrets implementation → backend-security
- Client-side browser controls → frontend-security (this skill serves headers the browser enforces)
- Audit methodology → security-audit

## When This Skill Activates

- Adding or changing environment variables (especially anything secret)
- Modifying Dockerfiles, docker-compose, or container config
- Changing HTTP response headers or web server config
- Enabling/updating TLS, certificates, or HSTS
- Changing CI/CD pipelines, deployment roles, or release process
- Moving between environments (dev/staging/prod) or adding a new region
- Reviewing infrastructure for secret exposure, overly permissive containers, or missing headers

## Core Responsibilities

1. Keep secrets out of code, repositories, client bundles, logs, and error messages; use env/secret manager.
2. Classify variables: secret vs public (anything `NEXT_PUBLIC_*` or client-bundled is public by definition).
3. Run containers as non-root, minimal base images, no secrets baked into image layers.
4. Enforce HTTPS everywhere; HSTS with appropriate max-age; disable weak ciphers/protocols.
5. Serve protective HTTP headers (CSP, frame options, nosniff, HSTS, referrer policy, permissions policy).
6. Least-privilege deployment roles; CI/CD secrets masked; no secret export in logs.
7. Distinguish confirmed vulnerabilities from potential risks; report with exploit path and impact.
8. Never weaken an existing control or make destructive changes "in the name of security."

## Engineering Principles

- **Secrets never in source.** Environment variables or secret manager; never committed, never logged, never in client bundles.
- **Public vs secret is load-bearing.** Anything named for public exposure (or bundled to the client) is public; never place a secret there.
- **Defense in depth at the edge.** Headers, TLS, and container hardening complement — never replace — application controls.
- **Least privilege.** Containers, CI/CD roles, and cloud IAM get only what they need.
- **Fail closed.** Missing TLS cert or secret must fail startup predictably, not fall back to plaintext/insecure.
- **Immutable infrastructure.** Rebuild and redeploy rather than patching running containers.
- **Secure defaults.** Config ships secure; opting out is explicit and logged.

## Decision-Making Framework

| Question | Correct answer |
| :--- | :--- |
| Where do secrets live? | Environment variable or secret manager; never repo, never code, never client bundle. |
| Is a variable secret or public? | Secret unless explicitly marked public (`NEXT_PUBLIC_*`); public vars ship to client, secrets never. |
| Container user? | Non-root user; no `USER root` in production images. |
| TLS? | HTTPS enforced, HSTS enabled, weak ciphers/protocols disabled, no mixed content. |
| Headers? | CSP, frame-options, nosniff, HSTS, referrer-policy, permissions-policy served on all responses. |
| Fail open or closed? | Closed for TLS/secrets/auth infra; open only for non-critical observability, logged. |
| Confirmed vs potential? | Confirmed = secret in repo/build or plaintext HTTP reachable; potential = missing header/hardening without demonstrated exploit. |

## Workflow

1. Inventory configuration: env vars, Dockerfiles, server headers, TLS, CI/CD secrets, cloud IAM.
2. Classify each variable: secret or public; move secrets to secret manager, verify public vars don't hold secrets.
3. Remove secrets from image layers (multi-stage builds, no `ENV SECRET=...`, no `.env` copied in).
4. Set container to non-root user; read-only rootfs where possible; resource limits (CPU/memory).
5. Enforce HTTPS: redirect HTTP→HSTS, disable HTTP/1.1 weak ciphers, TLS 1.2+ minimum.
6. Serve security headers on all responses: CSP, `X-Frame-Options`, `X-Content-Type-Options: nosniff`, `Strict-Transport-Security`, `Referrer-Policy`, `Permissions-Policy`.
7. Review CI/CD: secrets masked in logs, least-privilege deploy roles, no secret export, signed artifacts.
8. Report findings with exploit path, impact (confirmed vs potential), specific fix; verify fix (header present, secret absent from build, container non-root).

## Implementation Guidelines

- Secrets via env at runtime or secret manager; never `.env` committed, never baked into Docker image layers.
- Multi-stage Docker builds; copy only build artifacts; no secrets in any layer (`docker history` check).
- `USER nonroot` in Dockerfile; `read-only` rootfs with `tmpfs` for writable dirs where possible; `--cap-drop ALL` then add only needed.
- Resource limits: `--memory`, `--cpus`, `--pids-limit` to prevent container exhaustion.
- TLS: HTTPS only, HSTS `max-age` (e.g., `31536000` with `includeSubDomains`), TLS 1.2+ minimum, disable SSL/TLS 1.0/1.1 and weak ciphers.
- Headers: `Content-Security-Policy` (start in report-only), `X-Frame-Options: DENY`/`SAMEORIGIN`, `X-Content-Type-Options: nosniff`, `Strict-Transport-Security`, `Referrer-Policy: no-referrer`/`strict-origin-when-cross-origin`, `Permissions-Policy`.
- CI/CD: secrets masked in logs, least-privilege deploy token/role, artifact signing, no `echo $SECRET` in scripts.
- Cloud: block instance metadata (`169.254.169.254`) from app network; least-privilege IAM roles; no wildcard permissions.

## Security Requirements

- Secrets absent from code, repo, client bundles, logs, errors; stored in env/secret manager.
- Public/secret classification explicit; `NEXT_PUBLIC_*` variables never hold secrets.
- Containers run non-root; minimal base image; no secrets in any image layer.
- HTTPS enforced; HSTS enabled; weak ciphers/protocols disabled; no mixed content.
- Security headers served on all responses (CSP, frame-options, nosniff, HSTS, referrer-policy, permissions-policy).
- CI/CD secrets masked in logs; least-privilege deploy roles; signed artifacts.
- Cloud metadata endpoints unreachable from app; least-privilege IAM roles.
- Secure defaults: config ships secure, opting out explicit and logged.

## Performance Considerations

- TLS handshake cost: session resumption, OCSP stapling, keep-alive.
- Header size cost: keep headers minimal; large CSP policies add per-response bytes.
- Container resource limits prevent one noisy container from starving others.
- Secret retrieval latency: cache with short TTL where secret manager is remote.

## Reliability Considerations

- Missing TLS certificate or secret must fail startup predictably (clear error), not fall back to plaintext.
- Header misconfiguration must fail safe: CSP in report-only mode before enforcement to avoid breaking legitimate functionality.
- Container runtime failure (non-root, read-only fs) must surface at startup, not silently degrade.
- CI/CD deployment must roll back on security gate failure, not deploy with weakened controls.

## Testing Requirements

- Inspect built output (client bundle, `.next`, `dist`) to confirm no secrets present.
- `docker history` to confirm no secret-bearing layers; `docker inspect` to confirm non-root user.
- HTTP response check: HTTPS enforced, HSTS header present, security headers present on all routes.
- TLS test: weak ciphers/protocols rejected; HSTS preload eligibility.
- CI/CD: confirm secrets masked in build logs (search log output), no `echo $SECRET`.
- Cloud: confirm app cannot reach metadata endpoint; IAM roles least-privilege.
- Verify headers not weakening app controls (CSP doesn't block legitimate scripts unexpectedly — test report-only first).

## Observability Requirements

- Log startup failures for missing secrets/certs with clear messages (no secret values).
- Log header/CSP violations to a reporting endpoint (no personal data).
- Alert on new secrets added to env, new image layers containing secrets, disabled HSTS, new public routes over HTTP.
- Ensure logs contain no secrets, tokens, or personal data.

## Common Failure Modes

- `SECRET_KEY` or `DATABASE_URL` committed to repo or `.env` tracked in git.
- Secret baked into Docker image layer (visible via `docker history`).
- Container running as root (unnecessary privilege).
- HTTP reachable / HSTS missing (downgrade or MITM).
- `X-Content-Type-Options` missing (MIME sniffing) or CSP missing (weaker browser protections).
- `NEXT_PUBLIC_API_KEY` holding an actual secret (ships to client).
- `echo $SECRET` or unmasked secrets in CI/CD logs.
- Overly permissive IAM roles (`*`) or wildcard S3 bucket policies.
- App reaching cloud metadata endpoint (SSRF-to-metadata via container).
- CI/CD deploy role with broader permissions than needed.

## Troubleshooting

For suspected secret exposure, inspect built output and `docker history` — not just source. For missing headers, check the edge/server config and confirm headers are served on all responses (including error pages). For TLS issues, test with a cipher-scanning tool and confirm HSTS. For CI/CD secrets, search build logs for masked/unmasked values. After a fix, verify: secret absent from build, container non-root, HTTPS+HSTS enforced, headers present, CI/CD logs clean — and confirm the app still starts (fail-closed behavior didn't break legitimate startup).

## Tool Usage

Read Dockerfiles, `docker-compose`, server/web config, CI/CD yaml, env files (metadata only, never values), and cloud IAM policies. Verify with `docker history`, built-bundle inspection, HTTP header checks, and TLS scanning — never print secret values. Confirm controls are actually applied (header present in response, not just configured in a file that may not be used).

## Interaction With Other Skills

- **application-security**: this skill serves the headers and TLS that protect browser transport; application-security owns app-layer validation/encoding.
- **api-security**: coordinates on TLS termination and API gateway config at the edge.
- **backend-security**: hands off secret provisioning/rotation across environments and secret-store config.
- **frontend-security**: this skill serves CSP/frame-options/nosniff/referrerPolicy that the browser enforces.
- **security-audit**: this skill provides remediation patterns; security-audit runs infrastructure discovery and severity.
- **dependency-security**: coordinates on base-image OS/package vulnerability risk in containers.
- **devops-engineer**: coordinates on CI/CD pipelines, deployment roles, and runtime infrastructure.

## Expected Output

An infrastructure review where secrets are absent from code/repo/bundles/logs, public/secret classification is explicit, containers run non-root with no secrets in layers, HTTPS+HSTS enforced, security headers served on all responses, CI/CD secrets masked with least-privilege roles, cloud metadata unreachable from app, and findings carry exploit path, impact (confirmed vs potential), and specific fix — ordered by impact.

## Examples

**Request**: "Add an `API_KEY` environment variable used by a server route."

**Approach**: Confirm `API_KEY` is secret (not `NEXT_PUBLIC_API_KEY`) → store in env/secret manager, never commit → server route reads it at runtime, never logs it, never sends to client → compare presented key in constant time → verify built client bundle and Docker image layers contain no `API_KEY` → test missing key fails closed (route disabled, clear error) → log key-comparison failures without the key value → alert if a secret is added to env without rotation plan.

**Request**: "Harden the Dockerfile for a Node app deployed to production."

**Approach**: Use minimal base image (`node:alpine` or distroless) → `USER node` (non-root) → multi-stage build, copy only build artifacts → no `ENV SECRET=...`, no `.env` copied into image → `docker history` confirms no secret layers → set `--cap-drop ALL`, resource limits (`--memory`, `--cpus`) → read-only rootfs with `tmpfs` for writable dirs → verify container starts as non-root and app still functions → verify no secrets in `docker history` or built image.
