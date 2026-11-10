---
name: application-security
description: Owns application-layer security — OWASP Top 10, secure coding practices, input validation, output encoding, and common vulnerability prevention — for any software project.
version: 0.1.0
---

# Application Security

Owns application-layer security across any codebase. Activates when a change touches untrusted input, rendering, authentication boundaries, data storage, or any path an attacker could reach from the public surface.

## Purpose

Keep every application trust boundary honest: validate at entry, encode at exit, and never let attacker-controlled data reach a sensitive sink. Work cross-project — language-agnostic where principles apply, technology-aware where implementations differ.

## Scope

Owns:

- OWASP Top 10 application risks and their prevention (injection, broken access control, cryptographic failures, insecure design, security misconfiguration, vulnerable components, identification/authentication failures, software/data integrity failures, logging failures, SSRF)
- Secure coding principles: least privilege, deny by default, fail securely, defense in depth, economy of mechanism, complete mediation, open design, psychological acceptability
- Input validation: type, format, length, range, allowed values, coercion at trust boundaries
- Output encoding/escaping: HTML, attribute, JavaScript, CSS, URL, command, SQL contexts
- Common vulnerability prevention: XSS, injection, broken access control, IDOR, insecure deserialization, insecure direct object references
- Secure defaults: safe configurations shipped without opt-in

Does NOT own:

- Infrastructure/network hardening → infrastructure-security
- API protocol-specific controls → api-security
- Server-side database/session/secrets implementation → backend-security
- Client-side browser controls → frontend-security
- Vulnerability scanning/audit methodology → security-audit
- Dependency supply chain → dependency-security

## When This Skill Activates

- Adding or changing any feature that accepts user input
- Rendering stored or third-party content (HTML, Markdown, JSON, email)
- Building forms, search, file uploads, comment fields, or import flows
- Introducing a new authentication or authorization check
- Changing output rendering (escaping, sanitization, `dangerouslySetInnerHTML` equivalents)
- Reviewing a codebase for application-layer exposure

## Core Responsibilities

1. Enumerate trust boundaries before implementing any change; classify each input as trusted, semi-trusted, or untrusted.
2. Validate every untrusted input at its entry point — before it influences behavior, queries, or rendering.
3. Encode every untrusted output at its sink, matched to the output context.
4. Apply deny-by-default: every privileged operation is gated unless explicitly allowed.
5. Distinguish confirmed vulnerabilities from theoretical risks; report each with exploit path and impact.
6. Never weaken an existing security control or make destructive changes "in the name of security."

## Engineering Principles

- **Validation ≠ sanitization ≠ encoding.** Validate for correctness/bounds, sanitize only when intentionally allowing a subset (e.g. HTML allowlist), encode for the output context.
- **Validate at the boundary, encode at the sink.** Ingest-time sanitization protects one path; render-time encoding protects every reader.
- **Allowlists over denylists.** Denylists are bypassable; allowlist schemes, hosts, types, characters, and values.
- **Fail closed.** A missing token, key, or config must disable the feature predictably, not silently permit traffic.
- **Complete mediation.** Every request to every resource is checked; no bypass via alternate paths or methods.
- **No security through obscurity.** Hiding UI or relying on client-side checks is not access control.

## Decision-Making Framework

| Question | Correct answer |
| :--- | :--- |
| Where to validate? | At every trust boundary entry point, before use. |
| Where to encode? | At the output sink, matched to context (HTML/attr/JS/CSS/URL/SQL). |
| Allowlist or denylist? | Allowlist. Denylists only as defense-in-depth. |
| Fail open or closed? | Closed for security dependencies; open only for defense-in-depth where shutdown harms legitimate users, and log it. |
| Confirmed vs potential? | A confirmed vuln has a reproducible exploit path; a potential risk lacks one. Label accordingly. |

## Workflow

1. Map trust boundaries: who can call this, what can they supply, what does it read/write/call outbound.
2. Classify each input/output as trusted/untrusted, including data read back from storage.
3. Add validation at entry (type, format, length, range, allowed values).
4. Add encoding/sanitization at the sink matched to context.
5. Confirm authorization is server-side and covers the specific resource/method.
6. Bound resources (size, count, time) to prevent exhaustion.
7. Write the finding with exploit path, impact (confirmed vs potential), and specific fix.
8. Verify the fix actually executes on the failure branch; re-test exploit path and legitimate path.

## Implementation Guidelines

- Validate and coerce at the top of the handler; pass the validated value downstream, never raw input.
- Escape by default; sanitize deliberately with a maintained allowlist-based sanitizer where HTML is intended.
- Parameterize queries; never concatenate caller input into SQL, command, or template strings.
- Cap body size, upload size, array length, page size, and execution time on every public endpoint.
- Return generic errors to users; log details server-side without tokens or personal data.
- Never log full request bodies, tokens, authorization headers, or secrets from public endpoints.

## Security Requirements

- Validate all untrusted input for type, format, length, range, and allowed values before it influences behavior.
- Encode all untrusted output matched to context; sanitize stored/third-party HTML with an explicit allowlist.
- Parameterize every query; no string-concatenated caller input into SQL/command/template.
- Apply authorization server-side on every privileged operation, including object-level ownership.
- Constrain every server-side fetch of caller-influenced targets (scheme/host allowlist, private-range block, timeout).
- Keep secrets server-side only; compare presented secrets in constant time.
- Bound every input and resource that can trigger expensive work.
- Apply rate limiting to public endpoints that write state or consume paid resources.

## Performance Considerations

- Security checks are on the hot path; keep them cheap, avoid per-request expensive lookups.
- Reject oversized/malformed payloads before expensive processing — validation is also a performance control.
- Sanitization/encoding cost scales with content size; cap length at the boundary.

## Reliability Considerations

- A security check that throws on failure is an outage; decide explicitly fail-open vs fail-closed and log the choice.
- Misconfigured security features must fail safe and legibly.
- Verify the control executes on the failure branch, not just the success branch.

## Testing Requirements

- Test authorization with a second unauthorized identity and a resource owned by someone else.
- Test each validation failure mode and boundary values (empty, max length, one over, wrong type, unexpected field).
- Test output encoding with payloads that would execute if unsanitized (script tags, event handlers, URL schemes).
- Test SSRF constraints against loopback, link-local, private, non-HTTP targets.
- Test rate limiting with burst traffic; confirm 429, not unbounded acceptance or a crash.
- Verify secrets never reach client bundles by inspecting built output, not source.

## Observability Requirements

- Log authorization denials with actor, target, and reason.
- Log rate-limit events and validation rejections by category.
- Log secret comparison failures and SSRF target rejections.
- Alert on new public routes, outbound fetch targets, dependencies, and write endpoints.
- Ensure logs contain no tokens, personal data, or full untrusted payloads.

## Common Failure Modes

- Identity verified but ownership never checked (IDOR).
- Server-side fetch of caller-supplied URL with no allowlist (SSRF).
- Uploads trusted on client-supplied MIME type, no size cap, fully buffered in memory.
- Public write endpoints with truthiness-only validation and no rate limit.
- Client-side validation or hidden UI treated as access control.
- Secrets in logs, error messages, or client bundles.
- Stored HTML rendered without sanitization because "the current writer is trusted."
- In-process rate limiting treated as real control in serverless (resets per instance).

## Troubleshooting

For a suspected injection or XSS, confirm whether the value is escaped/parameterized/sanitized at the exact sink — not somewhere upstream another writer could bypass. For authz bypass, enumerate every method and path parameter on the resource and check each for an ownership check. For SSRF, log the resolved address, not just the supplied hostname (redirects/DNS defeat input-only checks). After a fix, re-test the exploit path itself plus the legitimate path, and confirm the control actually executes.

## Tool Usage

Read the actual handler, the actual auth helper it calls, and the actual sink where data is rendered or used. Most findings live in the gap between those three. Verify claims with a request, payload, or built-bundle inspection — never report a control as present because a helper is imported; confirm it is called on the path that matters.

## Interaction With Other Skills

- **api-security**: this skill defines general application controls; api-security specializes them to the API protocol layer (JWT, OAuth, CORS, rate limiting).
- **backend-security**: coordinates on database, session, and secrets implementation details.
- **frontend-security**: defines what must not reach the client; client-side rendering safety.
- **infrastructure-security**: hands off server config, headers, TLS, and deployment hardening.
- **security-audit**: this skill provides the remediation patterns; security-audit runs the discovery and severity process.
- **dependency-security**: coordinates on vulnerable component risk (OWASP A06).

## Expected Output

A review or implementation where every trust boundary is named, every untrusted input is bounded and validated at entry, every privileged operation is gated server-side, every caller-influenced outbound target is constrained, every output is encoded at its sink, and every secret is confirmed absent from client code/logs/responses. Findings reported with concrete exploit path, real impact, and specific fix — ordered by impact, no generic "consider adding security" advice.

## Examples

**Request**: "Add a user bio field that supports basic Markdown."

**Approach**: Treat bio as untrusted input entering a trust boundary → validate length/format at entry → on render, do not store raw Markdown as trusted HTML; render through a maintained Markdown-to-HTML pipeline with an allowlist sanitizer (permit only `b`, `i`, `em`, `strong`, `a` with `href` allowlist of `http`/`https`, no `javascript:`) → encode any leftover attributes → test with an XSS payload (`<script>`, `onerror`, `javascript:`) confirming it is neutralized → confirm no client bundle receives the raw value → document the allowlist decision so the next editor doesn't expand it silently.

**Request**: "A search page reflects the query in the results heading."

**Approach**: The reflected query is untrusted output reaching an HTML sink → HTML-escape at the sink (convert `<`, `>`, `&`, `"`, `'`) → test with `<img src=x onerror=alert(1)>` confirming it renders as text, not executable → confirm the same escaping applies when the query comes from a stored search history, not just the live request → log validation rejections by category so probing is distinguishable from bugs.
