---
name: frontend-security
description: Owns client-side security — XSS, CSRF, clickjacking, secure token storage, browser security, and dependency hygiene — for browser-based applications.
version: 0.1.0
---

# Frontend Security

Owns security for code that runs in the browser (SPA, SSR hydration, static sites, browser extensions). Activates when a change touches rendering, user input handling, token storage, cookies, headers, or any client-side code path an attacker can reach from the browser.

## Purpose

Keep untrusted data from executing in the browser, prevent cross-origin abuse, keep tokens out of reach of XSS, and ensure the client never becomes the weakest link in the security chain.

## Scope

Owns:

- XSS (reflected, stored, DOM-based): escaping by default, sanitizer allowlists, `innerHTML`/`dangerouslySetInnerHTML` discipline, Trusted Types
- CSRF: SameSite cookies, anti-CSRF tokens, origin/referer verification for state-changing requests
- Clickjacking: `X-Frame-Options`, `Content-Security-Policy frame-ancestors`, frame-busting as defense-in-depth
- Secure token storage: HttpOnly/Secure/SameSite cookies vs localStorage/sessionStorage trade-offs, in-memory only where appropriate
- Browser security: CSP, Subresource Integrity (SRI), `referrerPolicy`, `sandbox` attributes, feature policy/permissions policy
- Dependency security (frontend): vulnerable/outdated npm packages, supply-chain risk in client bundles
- Safe rendering of user-generated content: sanitization at render time, not just ingest
- MIME sniffing: `X-Content-Type-Options: nosniff`

Does NOT own:

- General application validation → application-security (applies to client input too)
- API auth protocol → api-security (token issuance/validation)
- Session/password server-side implementation → backend-security
- Infrastructure/TLS/deployment → infrastructure-security
- Audit methodology → security-audit

## When This Skill Activates

- Rendering user-generated or third-party content (comments, bios, HTML, Markdown, editor output)
- Using `innerHTML`, `dangerouslySetInnerHTML`, `v-html`, or template interpolation with untrusted data
- Storing tokens in localStorage/sessionStorage/cookies
- Making cross-origin fetch/XHR requests with credentials
- Embedding third-party content (iframes, widgets, scripts)
- Setting response headers served to the browser (CSP, frame options, content type options)
- Adding frontend dependencies or changing the build/bundle
- Reviewing client code for XSS, data leakage, or insecure storage

## Core Responsibilities

1. Escape by default; sanitize deliberately with a maintained allowlist-based sanitizer where HTML is intended.
2. Keep tokens in HttpOnly/Secure/SameSite cookies where possible; avoid localStorage/sessionStorage for access tokens.
3. Apply CSRF protection (SameSite cookies + anti-CSRF tokens) to state-changing browser requests.
4. Deploy CSP with nonce/hash or strict-dynamic; avoid `unsafe-inline`/`unsafe-eval` unless justified.
5. Prevent clickjacking with `X-Frame-Options: DENY`/`SAMEORIGIN` and CSP `frame-ancestors`.
6. Use SRI for third-party scripts/styles; `referrerPolicy` to limit referrer leakage.
7. Distinguish confirmed vulnerabilities from potential risks; report with exploit path and impact.
8. Never weaken an existing control or make destructive changes "in the name of security."

## Engineering Principles

- **Sanitize at render time.** Ingest-time sanitization protects one writer; render-time encoding protects every reader, present and future.
- **Cookies over localStorage for tokens.** localStorage is accessible to any script on the origin (XSS can steal it); HttpOnly cookies are not.
- **Escape matched to context.** HTML, attribute, JavaScript, CSS, URL — each needs its own encoding.
- **Allowlists over denylists.** Permit only known-safe tags/attributes/schemes; denylists are bypassable.
- **CSP is defense in depth, not the only control.** Combine with escaping, sanitization, and SRI.
- **SameSite cookies mitigate CSRF** but are not a complete replacement for anti-CSRF tokens on high-value actions.
- **Fail closed.** A missing CSP or token should degrade the feature predictably, not expose data.

## Decision-Making Framework

| Question | Correct answer |
| :--- | :--- |
| Token storage? | HttpOnly/Secure/SameSite cookie preferred; localStorage/sessionStorage only for non-sensitive, short-lived, non-auth data; in-memory for highest sensitivity. |
| Render untrusted HTML? | Escape by default; sanitize at render time with explicit allowlist only when HTML is intended. |
| CSRF protection? | SameSite=Strict/Lax cookies + anti-CSRF token (double-submit or same-site) for state-changing actions. |
| Third-party scripts? | SRI hash + CSP; only load from trusted domains; sandbox iframes. |
| Clickjacking? | `X-Frame-Options: DENY` + CSP `frame-ancestors 'none'` (or `'self'`). |
| Confirmed vs potential? | Confirmed = reproducible XSS/CSRF/clickjacking exploit; potential = missing hardening without demonstrated exploit. |

## Workflow

1. Enumerate rendering sinks: where untrusted data reaches the DOM (innerHTML, attributes, URLs, script blocks).
2. Escape all untrusted output at the sink matched to context.
3. Sanitize stored/third-party HTML at render time with an allowlist; test with XSS payloads.
4. Move tokens to HttpOnly/Secure/SameSite cookies; audit localStorage/sessionStorage for secrets.
5. Apply CSRF protection to state-changing requests (cookies + tokens/origin checks).
6. Set CSP with nonce/hash or strict-dynamic; remove `unsafe-inline`/`unsafe-eval`.
7. Set `X-Frame-Options`, `X-Content-Type-Options: nosniff`, `referrerPolicy`.
8. Add SRI to third-party scripts/styles; sandbox iframes.
9. Report findings with exploit path, impact (confirmed vs potential), specific fix; verify fix executes on failure branch.

## Implementation Guidelines

- Escape by default in templates/frameworks; use `dangerouslySetInnerHTML` only for application-authored, never user-controlled, content.
- Sanitizer allowlist: permitted tags, attributes, schemes (`http`/`https`, block `javascript:`/`data:`), strip event handlers.
- Access tokens in HttpOnly cookies; refresh tokens in HttpOnly cookies; avoid localStorage for auth tokens.
- CSRF: SameSite=Lax/Strict cookies plus anti-CSRF token validated server-side for POST/PUT/DELETE.
- CSP default: `default-src 'self'`; script/style via nonce or hash; `object-src 'none'`; `base-uri 'self'`.
- `referrerPolicy: no-referrer` or `strict-origin-when-cross-origin`; limit sensitive URL leakage.
- Third-party scripts: SRI integrity hash; only from trusted domains; CSP `script-src` restrict origins.
- Iframes: `sandbox` attribute, `allow` minimal permissions, CSP `frame-ancestors`.
- Never log tokens, passwords, or personal data to console in production builds.

## Security Requirements

- Escape all untrusted output matched to context; sanitize stored/third-party HTML at render time with explicit allowlist.
- Tokens in HttpOnly/Secure/SameSite cookies; no auth tokens in localStorage/sessionStorage.
- CSRF protection on all state-changing browser requests (SameSite cookies + anti-CSRF tokens/origin verification).
- CSP deployed with nonce/hash or strict-dynamic; no `unsafe-inline`/`unsafe-eval` without documented justification.
- Clickjacking protection: `X-Frame-Options: DENY`/`SAMEORIGIN` + CSP `frame-ancestors`.
- `X-Content-Type-Options: nosniff`; `referrerPolicy` set to limit leakage.
- SRI hashes for third-party scripts/styles; sandboxed iframes with minimal permissions.
- No tokens/passwords/personal data in console logs or client-side error reports.

## Performance Considerations

- Sanitization/encoding cost scales with content size; cap input length at the boundary.
- CSP evaluation cost is minimal; avoid overly broad or frequently re-evaluated policies.
- SRI hash verification is a one-time fetch cost; cache third-party assets appropriately.
- Avoid per-request client-side security checks that block rendering.

## Reliability Considerations

- A missing CSP or sanitizer must fail closed (content not rendered), not render unsanitized.
- Cookie rejection by the browser must degrade the feature predictably, not silently send tokens in the clear.
- Sanitizer dependency failure must not fall back to raw rendering; fail to a safe default or error.
- Misconfigured CSP must not break legitimate functionality silently; test in report-only mode first.

## Testing Requirements

- Test XSS: payloads (`<script>`, `onerror`, `javascript:`, `data:`, SVG) confirm neutralization at every sink.
- Test stored content rendered later (second writer) — sanitization at render time, not just ingest.
- Test token storage: inspect DevTools/Application to confirm no auth tokens in localStorage/sessionStorage.
- Test CSRF: cross-origin state-changing request without token is rejected; SameSite cookie behavior.
- Test clickjacking: page cannot be framed by attacker origin (`frame-ancestors`, `X-Frame-Options`).
- Test CSP: violations reported in report-only mode; no `unsafe-inline` scripts execute.
- Test SRI: tampered third-party script is blocked by browser.
- Verify no tokens/personal data in console or client error reports (production build inspection).

## Observability Requirements

- Log client-side security violations via CSP `report-uri`/`report-to` endpoint (server-side ingestion, no personal data).
- Log auth-token access patterns server-side (cookie rotation, refresh).
- Log XSS sanitization events (what was stripped) for tuning the allowlist.
- Alert on new third-party script origins, new `eval`/`innerHTML` usage, new localStorage writes.
- Ensure client logs/reports contain no tokens, passwords, or personal data.

## Common Failure Modes

- Rendering user input via `innerHTML`/`dangerouslySetInnerHTML` without sanitization (XSS).
- Storing access tokens in localStorage (stealable by any XSS).
- Missing SameSite on auth cookies (CSRF via cross-origin POST).
- State-changing endpoint accepting cross-origin requests with cookies and no anti-CSRF token.
- CSP with `unsafe-inline` or `*` script sources (defeats CSP).
- Page frameable by attacker origin (clickjacking).
- Third-party script without SRI (supply-chain tampering).
- Referrer leaking sensitive URLs to third parties.
- Console logging tokens/personal data in production.

## Troubleshooting

For suspected XSS, confirm the value is escaped/sanitized at the exact DOM sink — not just "cleaned" on ingest where a second writer bypasses it. For token theft risk, inspect the Application tab for auth tokens in localStorage/sessionStorage; HttpOnly cookies won't show there (correct). For CSRF, test a cross-origin state-changing request from a different origin without a token. For clickjacking, attempt to frame the page from an attacker-controlled origin. After a fix, re-test the exploit payload and legitimate rendering, and confirm the control executes (CSP violations report, sanitizer strips).

## Tool Usage

Read the actual component/template, the sanitizer call, and the token-storage code. Most findings live in the gap between rendering sink and storage. Verify with actual payloads and DevTools inspection — never report a control as present because a sanitizer library is imported; confirm it is called on the path that matters.

## Interaction With Other Skills

- **application-security**: this skill applies escaping/sanitization to browser contexts; application-security owns the general principles.
- **api-security**: coordinates on token format and CSRF token issuance/validation for API calls.
- **backend-security**: defines session/cookie flags server-side; this skill ensures the client honors them.
- **infrastructure-security**: hands off CSP headers, `X-Frame-Options`, `nosniff` served by the edge/server.
- **security-audit**: this skill provides remediation patterns; security-audit runs frontend discovery and severity.
- **dependency-security**: coordinates on frontend/npm package vulnerability risk in client bundles.

## Expected Output

A frontend review where all untrusted output is escaped at its sink, stored/third-party HTML is sanitized at render time with an allowlist, tokens are in HttpOnly/Secure/SameSite cookies (not localStorage), CSRF protection covers state-changing requests, CSP/frame-options/nosniff/referrerPolicy are set, third-party assets use SRI, and findings carry exploit path, impact (confirmed vs potential), and specific fix — ordered by impact.

## Examples

**Request**: "Display user comments with basic HTML formatting (bold, links)."

**Approach**: Comments are untrusted stored content → escape by default → where HTML formatting is intended, sanitize at render time with an allowlist (`b`, `strong`, `i`, `em`, `a[href]` with `http`/`https` scheme only, strip `javascript:`/`data:` and all event handlers) → never store raw HTML as trusted → test with `<script>`, `onerror`, `<svg onload>`, `javascript:`, `data:` payloads confirming neutralization → test a second writer (edited comment) also sanitized → confirm no auth token leaks via comment rendering → log sanitization events for allowlist tuning.

**Request**: "Store the JWT access token after login."

**Approach**: Prefer HttpOnly/Secure/SameSite cookie set by the server (not accessible to JS) → if JS must read it, that's a signal the design needs revisiting → avoid localStorage/sessionStorage for access tokens (XSS-readable) → use in-memory only for highest sensitivity → apply SameSite=Lax/Strict + anti-CSRF token for state-changing API calls → test DevTools Application tab confirms no auth token in localStorage/sessionStorage → confirm cookie flags set → test cross-origin state-changing request without CSRF token is rejected.
