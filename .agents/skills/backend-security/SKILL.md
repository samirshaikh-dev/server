---
name: backend-security
description: Owns server-side security — secure database queries, SQL injection prevention, password hashing, session management, secrets management, and secure error handling — for any backend architecture.
version: 0.1.0
---

# Backend Security

Owns server-side security across any backend (Node/Python/Java/Go/etc., serverless or long-running). Activates when a change touches database access, authentication state, password handling, secrets, or server-side error responses.

## Purpose

Ensure server-side code never executes attacker-controlled data as commands, stores credentials unsafely, leaks internals through errors, or mishandles sessions and secrets.

## Scope

Owns:

- Secure database queries: parameterization, prepared statements, ORM safe usage, no string-concatenated SQL
- SQL injection prevention: parameterized queries, input coercion, stored procedure safety
- Password hashing: bcrypt/argon2/scrypt, salt, work factor, constant-time comparison, no plaintext storage
- Session management: creation, regeneration, expiration, invalidation, cookie flags, session fixation
- Secrets management: environment variables, secret stores, rotation, no secrets in code/logs/client bundles
- Secure error handling: generic user messages, no stack traces, no internal hostnames, logging details server-side
- Server-side request forgery (SSRF): scheme/host allowlists, private-range blocking, timeouts
- Command/template/header injection: no caller input into shell commands, templates, or headers
- File handling: path traversal, upload bounds, type verification from content

Does NOT own:

- General application input validation → application-security (this skill applies it to DB/session/secrets contexts)
- API auth protocol → api-security
- Client-side browser controls → frontend-security
- Infrastructure/TLS/deployment → infrastructure-security
- Audit methodology → security-audit

## When This Skill Activates

- Adding or changing any database query, migration, or ORM call
- Introducing password hashing, comparison, or storage
- Creating or modifying sessions, login/logout, or "remember me"
- Touching environment variables, secret stores, or API keys
- Changing error responses or logging behavior
- Adding file upload/download, path construction, or server-side fetch
- Reviewing a backend for injection, info disclosure, or credential exposure

## Core Responsibilities

1. Parameterize every query; never concatenate caller input into SQL/command/template strings.
2. Hash passwords with a modern algorithm (argon2id/bcrypt/scrypt), never store plaintext, compare in constant time.
3. Manage sessions server-side: regenerate on login, expire on logout, bind cookies with secure flags.
4. Keep secrets out of code, logs, errors, and client bundles; rotate deliberately.
5. Return generic errors to users; log full details server-side without secrets or personal data.
6. Constrain server-side fetches and file paths to prevent SSRF and path traversal.
7. Distinguish confirmed vulnerabilities from potential risks; report with exploit path and impact.
8. Never weaken an existing control or make destructive changes "in the name of security."

## Engineering Principles

- **The database is not a trust boundary.** Content read back from it is attacker-controlled if the public wrote it.
- **Parameterize, don't sanitize.** Parameterized queries are the defense; input sanitization is not a substitute for SQL.
- **Hash, don't encrypt, passwords.** Passwords are hashed with salt and work factor; encryption is reversible and wrong for auth.
- **Constant-time compare.** All secret/token comparison resists timing attacks.
- **Short-lived sessions.** Regenerate IDs after privilege changes, expire on logout and inactivity.
- **Secrets server-side only.** `NEXT_PUBLIC_*` (or equivalent) is public by definition.
- **Fail closed.** Missing secret/key disables the feature predictably; fail open only for defense-in-depth, logged.

## Decision-Making Framework

| Question | Correct answer |
| :--- | :--- |
| Password storage? | argon2id preferred, bcrypt acceptable, scrypt; never plaintext, MD5, SHA, or reversible encryption. |
| Session storage? | Server-side session store (DB/Redis) with short-lived, HttpOnly, Secure, SameSite cookies. |
| Secret location? | Environment variable or secret manager; never committed, never in client bundle, never logged. |
| SQL with caller input? | Parameterized query / prepared statement; ORM parameter binding; never string concatenation. |
| Fail open or closed? | Closed for auth/secrets/crypto; open only for non-critical defense-in-depth, logged. |
| Confirmed vs potential? | Confirmed = reproducible injection/info-disclosure; potential = missing hardening without demonstrated exploit. |

## Workflow

1. Map data flows: where caller input reaches queries, commands, templates, headers, file paths, or outbound fetches.
2. Replace string-built queries with parameterized/prepared statements or ORM parameter binding.
3. Hash passwords on creation; verify with constant-time comparison; never log or return passwords.
4. Regenerate session IDs after login/privilege change; invalidate on logout; set cookie flags.
5. Move secrets to env/secret store; verify absent from bundles and logs via built-output inspection.
6. Wrap errors: generic message to user, detailed server-side log (no secrets, SQL, hostnames).
7. Constrain fetches (scheme/host allowlist, private block, timeout) and file paths (traversal block, type from content).
8. Report findings with exploit path, impact, specific fix; verify fix executes on failure branch.

## Implementation Guidelines

- Use parameterized queries/ORM binding for every query involving caller input, including `ORDER BY`, `LIKE`, and `IN` clauses.
- Hash new passwords with argon2id (work factor tuned), upgrade legacy hashes on next successful login.
- Compare presented secrets/tokens with `timingSafeEqual`; reject on length mismatch; missing/empty = rejection.
- Regenerate session ID after login and after any privilege escalation; set `HttpOnly`, `Secure`, `SameSite=Strict/Lax`.
- Cap session lifetime and idle timeout; invalidate server-side on logout (not just client cookie removal).
- Store secrets in env/secret manager; verify `NEXT_PUBLIC_*` equivalents never hold secrets.
- Return errors: generic user-facing message, correlation ID, details logged server-side.
- Constrain file paths: resolve and reject traversal (`..`), allowlist directories, verify type from content not extension.
- Constrain server-side fetches: `http`/`https` scheme only, host allowlist, block loopback/link-local/private/metadata, explicit timeout.

## Security Requirements

- Parameterize every query; no string-concatenated caller input into SQL/command/template.
- Hash passwords with argon2id/bcrypt/scrypt + salt; never plaintext or reversible encryption.
- Compare secrets/tokens in constant time; reject missing/empty tokens.
- Manage sessions server-side: regenerate on login/privilege change, expire on logout, secure cookie flags.
- Keep secrets server-side only; absent from code, bundles, logs, errors; rotate deliberately.
- Return generic errors to users; log details server-side without secrets/personal data/internal hostnames.
- Constrain server-side fetches and file paths to prevent SSRF and path traversal.
- Bound input and resource size (body, upload, query length) to prevent exhaustion.

## Performance Considerations

- Hashing is intentionally slow; do not hash on every request — verify stored hash, compare once.
- Session lookups should be cached (short TTL) where store is remote (Redis/DB).
- Password hash work factor tuned so login remains acceptable under load.
- Parameterized queries are cheaper than regex sanitization and safer.

## Reliability Considerations

- A hashing or crypto dependency that throws must fail closed (reject login), not permit access.
- Session store failure must fail closed (no new sessions) with a legible error, not silently create unauthenticated sessions.
- Secret-loading failure must disable the feature predictably at startup, not silently use empty/fallback values.
- Error handling must not leak internals even when the underlying error is unexpected.

## Testing Requirements

- Test SQL injection payloads (`' OR 1=1 --`, union-based, stacked queries) confirm parameterization blocks them.
- Test password hash upgrade: legacy plaintext/login still works, new login uses argon2id/bcrypt.
- Test constant-time comparison does not leak via timing (vary length/content, measure).
- Test session: fixation (session ID changes after login), logout invalidates server-side, cookie flags set.
- Test error responses: no stack traces, no SQL, no internal hostnames, generic message + correlation ID.
- Test SSRF: loopback, link-local, private, metadata, non-HTTP schemes rejected.
- Test path traversal: `../../../etc/passwd` style inputs rejected.
- Verify secrets absent from built client bundles and logs (inspect output, not source).

## Observability Requirements

- Log authentication failures with reason (no passwords), authorization denials with actor/target/reason.
- Log database errors server-side with correlation ID (no SQL or user data in the message returned to client).
- Log secret comparison failures and SSRF rejections.
- Alert on new database tables/routes, new outbound fetch targets, new secrets added.
- Ensure logs contain no tokens, passwords, personal data, or full untrusted payloads.

## Common Failure Modes

- String-concatenated caller input into SQL (classic injection).
- Passwords stored plaintext or with weak/unsalted hashes; `bcryptjs` installed but unused (false signal).
- Comparing secrets with `==`/locale comparison (timing leakage).
- Session ID not regenerated after login (session fixation).
- Cookies missing `HttpOnly`/`Secure`/`SameSite` (token theft via XSS/CSRF).
- Secrets committed to repo or logged in error messages.
- Error responses returning stack traces, SQL, or upstream hostnames.
- Server-side fetch of caller-supplied URL with no allowlist (SSRF to metadata services).
- File path built from caller input without traversal check.

## Troubleshooting

For suspected SQL injection, confirm the query uses parameterization at the exact sink — not "sanitized" upstream where another writer can bypass. For suspected weak password storage, check whether the hash library is actually called (installed ≠ used). For session issues, confirm regeneration after login and server-side invalidation on logout. For info disclosure, inspect actual error responses (not source) for stack traces/hostnames. After a fix, re-test the exploit path and legitimate path, and confirm the control executes on the failure branch.

## Tool Usage

Read the actual query builder, the actual auth/session helper, and the actual error/rendering sink. Most findings live in the gap between those three. Verify with actual requests/malformed payloads — never report a control as present because a library is imported; confirm it is called on the path that matters.

## Interaction With Other Skills

- **application-security**: this skill applies validation/encoding to DB/session/secrets contexts; application-security owns the general principles.
- **api-security**: coordinates on token format, revocation, and API authentication boundaries.
- **frontend-security**: defines what secrets/tokens must never reach the client; session cookie handling.
- **infrastructure-security**: hands off secret provisioning/rotation across environments and secret-store config.
- **security-audit**: this skill provides remediation patterns; security-audit runs backend discovery and severity.
- **dependency-security**: coordinates on database driver, ORM, and auth library version risk.
- **database-engineer**: coordinates on constraints, least-privilege DB roles, and structural defense-in-depth.

## Expected Output

A backend review where every query is parameterized, passwords are hashed with a modern algorithm and compared in constant time, sessions are server-managed with secure cookies and regeneration, secrets are server-side only and absent from bundles/logs/errors, errors leak no internals, and findings carry exploit path, impact (confirmed vs potential), and specific fix — ordered by impact.

## Examples

**Request**: "Add a login endpoint that checks username/password against stored credentials."

**Approach**: Look up user by username → if found, compare supplied password to stored hash using constant-time comparison → never reveal whether the username exists (same response timing/message for valid/invalid) → hash new passwords with argon2id on registration → on login success, regenerate session ID, set `HttpOnly`/`Secure`/`SameSite` cookie → on failure, return generic "invalid credentials" with no enumeration signal → test timing doesn't differ between valid/invalid username → test SQL injection in username field is blocked by parameterization → log failures server-side without passwords.

**Request**: "A feature reads an environment variable `API_KEY` and uses it in an outbound server-side fetch."

**Approach**: Confirm `API_KEY` is server-side only (not `NEXT_PUBLIC_*`), absent from client bundle and logs → compare presented key in constant time, reject missing/empty → constrain the fetch target (scheme/host allowlist, private-range block, timeout) so a key isn't exfiltrated to an attacker-controlled host → rotate key deliberately if exposed → test missing key fails closed (feature disabled, not silently open) → log key-comparison failures without the key value.
