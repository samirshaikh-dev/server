---
name: security-audit
description: Owns security auditing — analyzing codebases, identifying vulnerabilities, assessing severity, and providing actionable remediation steps — for any software project.
version: 0.1.0
---

# Security Audit

Owns the disciplined process of finding, triaging, and remediating security issues in codebases. Activates when a codebase (or a subset of it) needs a security review: before launch, after a major feature, in response to a report, or on a recurring schedule.

## Purpose

Find real security issues, distinguish confirmed vulnerabilities from theoretical risks, assess severity honestly, and give developers specific, verifiable remediation — without false positives, destructive changes, or weakening existing controls.

## Scope

Owns:

- Codebase security analysis: manual and tool-assisted review of trust boundaries, inputs, outputs, auth, sessions, secrets, crypto, dependencies
- Vulnerability identification: injection, broken access control, XSS, CSRF, SSRF, IDOR, insecure deserialization, missing headers, hardcoded secrets
- Severity assessment: impact × likelihood, CVSS-style scoring adapted to context, confirmed vs potential labeling
- Remediation planning: specific fixes, exploit-path verification, priority ordering, rollback-safe changes
- Audit reporting: findings with evidence, affected code paths, fix verification steps, false-positive filtering
- Re-audit verification: confirming fixes actually work and didn't introduce regressions

Does NOT own:

- Implementing the fixes → the relevant skill/engineer (application-security, api-security, backend-security, frontend-security, infrastructure-security, dependency-security)
- Setting security policy → governance/security leadership
- Running production incident response → security operations

## When This Skill Activates

- Pre-launch security review of a feature, service, or site
- Scheduled recurring audit (quarterly, per-release)
- Response to a vulnerability disclosure or bug bounty report
- After a major refactor touching auth, data, or external integrations
- Before adopting a new dependency with security-relevant surface
- When requested to "review this codebase for security"

## Core Responsibilities

1. Enumerate the attack surface: all public routes, inputs, outputs, auth boundaries, outbound calls, dependencies.
2. Read actual code paths (handler → auth → sink), not just configs or imports.
3. Identify vulnerabilities with concrete exploit paths (reproducible where safe to demonstrate).
4. Label each finding confirmed (exploit path demonstrated) or potential (missing control, no demonstrated exploit).
5. Assess severity using impact × likelihood, adapted to the system's data and users.
6. Provide specific remediation steps, not generic "add security" advice.
7. Include verification steps so the fix can be confirmed to work.
8. Never make destructive changes or weaken existing controls during the audit itself.

## Engineering Principles

- **Evidence over assumption.** A finding names the file, line, input, sink, and (for confirmed) the payload that exploits it.
- **Confirmed ≠ potential.** Confirmed = reproducible exploit path; potential = missing hardening or control without demonstrated exploit. Never inflate severity.
- **Remediation is specific.** "Sanitize input" is not specific; "HTML-escape `comment.body` at `components/Comment.jsx:42` before insertion" is.
- **Fixes must be verifiable.** Every finding includes a verification step (request, payload, built-output check).
- **No false positives.** A control that is imported but not called is not reported as present; a control that is called is verified.
- **No destructive audit changes.** The audit identifies and recommends; it does not rewrite code or delete controls.
- **Prioritize by real impact.** Authz bypass and data exposure outrank missing header on an internal admin page.

## Decision-Making Framework

| Question | Correct answer |
| :--- | :--- |
| Is it confirmed? | Only if an exploit path is demonstrated/reproducible; otherwise potential. |
| How to score severity? | Impact (data, users, privilege) × likelihood (exploitability, exposure), contextualized. |
| What's the fix? | Specific code change at the exact sink/boundary, with the control named. |
| How to verify? | A request, payload, or build inspection that proves the control executes. |
| Order of fixes? | By real impact on this system, not scan order or CVSS alone. |

## Workflow

1. Scope the audit: which codebase, routes, data stores, external integrations, and users are in scope.
2. Map trust boundaries: every place untrusted input enters (forms, APIs, uploads, third-party responses, stored content read back).
3. Review each boundary: validation at entry, authorization server-side, encoding at sink, secrets absent, outbound targets constrained.
4. Run tool-assisted scans (SAST/dependency scanning) as a starting point, then manually verify every hit (eliminate false positives).
5. For each finding: document evidence (file:line, input, sink, payload), label confirmed/potential, score severity, specify remediation, specify verification.
6. Prioritize by real impact; group related findings; identify root causes (missing pattern vs one-off bug).
7. Deliver the audit report; re-audit after fixes to confirm remediation and check for regressions.

## Implementation Guidelines (for the audit report)

Each finding includes:
- **Title** — short, specific (e.g. "IDOR on `PATCH /api/users/:id` — no ownership check")
- **Location** — file:line(s)
- **Type** — injection / broken access control / XSS / CSRF / SSRF / secrets exposure / missing header / vulnerable dependency
- **Confirmed / Potential** — with rationale
- **Severity** — Critical / High / Medium / Low / Info, with impact × likelihood rationale
- **Exploit path** — reproducible steps or payload (confirmed only)
- **Impact** — data exposed, users affected, privilege gained
- **Remediation** — specific fix at the exact location
- **Verification** — how to confirm the fix works (request/payload/build check)
- **References** — OWASP, CWE, or standard where applicable

## Severity Guidelines (context-adapted)

- **Critical:** Confirmed remote code execution, unauthenticated data exfiltration, or full account takeover with broad impact.
- **High:** Confirmed authz bypass / IDOR / injection affecting sensitive data, or confirmed secret exposure in client bundle/repo.
- **Medium:** Potential authz issue, missing rate limit on public write, potential XSS with limited scope, missing security headers on public pages.
- **Low:** Missing header on internal/admin-only page, information disclosure of non-sensitive data, potential dependency risk with no known exploit.
- **Info:** Best-practice hardening, documentation gaps, defense-in-depth suggestions.

## Testing / Verification Requirements

- For each confirmed finding, re-run the exploit path after the fix to confirm it no longer works.
- For each fix, confirm the legitimate path still works (no regression).
- For encoding/sanitization fixes, test with XSS/injection payloads at the exact sink.
- For authz fixes, test with a second unauthorized identity and a resource owned by someone else.
- For secret-exposure fixes, inspect built output/bundle/repo to confirm absence (not just source).
- For header fixes, confirm headers present on all responses including error pages.
- Document verification results in the re-audit report.

## Observability Requirements

- Audit findings feed monitoring: authz denials, rate-limit events, validation rejections, secret-comparison failures.
- Re-audit on a schedule or after major changes; track fix closure rate and time-to-remediate.
- Maintain an audit trail: who reviewed, what was found, what was fixed, when verified.

## Common Failure Modes

- Reporting "missing security" generically without a location, payload, or fix.
- Inflating a potential risk to confirmed severity without an exploit path.
- False positives: reporting an imported-but-unused control as a gap, or a present control as missing.
- Recommending destructive changes (deleting auth, removing validation) "to simplify."
- Scoring by CVSS alone without considering this system's data and exposure.
- Skipping verification: reporting a fix without confirming it executes on the failure branch.
- Audit changes that weaken an existing control in the name of "cleanup."

## Troubleshooting

If a scan flags SQL injection, confirm parameterization at the exact sink — not a sanitizer upstream another writer can bypass. If authz is flagged, enumerate every method/path parameter on the resource and check each for an ownership check. If SSRF is flagged, log the resolved address (not just the supplied hostname) because redirects/DNS defeat input-only checks. If a secret is flagged, inspect built output and image layers, not just source. Always re-test exploit path + legitimate path after a fix, and confirm the control executes on the failure branch.

## Tool Usage

Read actual handlers, auth helpers, sinks, configs, Dockerfiles, CI/CD, lockfiles. Use SAST/dependency scanners as starting points only; manually verify every hit. Confirm with requests, payloads, built-bundle inspection — never report a control as present because a library is imported; confirm it is called on the path that matters. Never print secret values during the audit.

## Interaction With Other Skills

- **application-security**: provides remediation patterns for application-layer findings; this skill finds and scores them.
- **api-security**: provides remediation patterns for API findings (authN/authZ, CORS, rate limiting).
- **backend-security**: provides remediation patterns for DB/session/secrets findings.
- **frontend-security**: provides remediation patterns for XSS/CSRF/token-storage findings.
- **infrastructure-security**: provides remediation patterns for header/TLS/container/secret findings.
- **dependency-security**: provides remediation patterns for vulnerable-dependency findings; this skill scores and prioritizes them.

## Expected Output

An audit report: every finding with file:line, type, confirmed/potential label, severity (impact × likelihood rationale), exploit path (confirmed only), impact, specific remediation at the exact location, and verification step — ordered by real impact, no generic advice, no false positives, no destructive recommendations. Followed by a re-audit confirming fixes work and no regressions.

## Examples

**Request**: "Audit this codebase before launch."

**Approach**: Enumerate public routes → find `POST /api/contact` validates only truthiness, no rate limit → potential abuse (High? Medium → Medium because durable row + email amplification but no demonstrated exploit) → remediation: add field format/length bounds + rate limit returning 429 → verification: submit oversized/malformed payload (rejected), burst traffic (429). → find `GET /api/pdf-proxy` fetches caller URL with no allowlist → confirmed SSRF → exploit: `http://169.254.169.254/` returns metadata → remediation: https scheme + host allowlist + private-range block + timeout → verification: request loopback/private/metadata URLs, all rejected. → find auth cookie missing `HttpOnly` → potential XSS token theft → remediation: add `HttpOnly`/`Secure`/`SameSite` → verification: DevTools confirms flag, JS `document.cookie` excludes it. → Report ordered: confirmed SSRF (Critical) first, then potential abuse, then potential cookie issue. → Re-audit after fixes: SSRF payloads rejected, rate limit returns 429, cookie flagged HttpOnly, legitimate paths still work.
