---
name: dependency-security
description: Owns dependency supply-chain security — identifying vulnerable, outdated, or suspicious dependencies and recommending safe upgrades — for any language or package manager.
version: 0.1.0
---

# Dependency Security

Owns the software supply chain: the libraries, frameworks, and packages a project depends on. Activates when a dependency is added, upgraded, audited, or flagged by a vulnerability scanner.

## Purpose

Ensure dependencies don't introduce known vulnerabilities, abandoned or suspicious packages, or transitive risk — and that upgrades are made safely without breaking changes or weakened controls.

## Scope

Owns:

- Vulnerability identification: known CVEs, advisory databases (GitHub Advisories, npm audit, Snyk, OSV, PyPI advisory, etc.), vulnerable versions
- Outdated/abandoned dependency detection: unmaintained packages, no recent commits/releases, low community trust
- Suspicious/typosquatting detection: lookalike names, odd maintainer patterns, postinstall scripts, minified obfuscated code
- Transitive dependency risk: deep dependency trees, phantom dependencies, hoisting issues
- Safe upgrade strategy: semver compatibility, breaking-change assessment, changelog review, staged rollout, rollback plan
- Lockfile integrity: lockfile committed, `npm ci`/equivalent deterministic installs, no drift between lockfile and manifest
- Install-script risk: `preinstall`/`install`/`postinstall` scripts executing on install
- Permission/scope review: what a dependency can access (network, file system, environment)

Does NOT own:

- Application-layer use of a dependency → application-security / api-security / backend-security / frontend-security
- Vulnerability audit methodology and severity scoring → security-audit (this skill feeds it dependency findings)
- Infrastructure/container base images → infrastructure-security (this skill covers app dependencies; infra skill covers container OS/packages)

## When This Skill Activates

- Adding a new dependency to package.json / requirements.txt / go.mod / etc.
- Running `npm audit` / `snyk test` / `dependabot` / vulnerability scan
- A dependency is flagged as vulnerable or deprecated
- Considering an upgrade (major/minor/patch)
- Reviewing the lockfile for drift or phantom deps
- Assessing supply-chain risk before adopting a package

## Core Responsibilities

1. Identify vulnerable dependencies and map them to advisories with affected versions and patched versions.
2. Distinguish direct vs transitive dependencies and assess whether the vulnerability is reachable in this project's usage.
3. Label findings confirmed (vulnerable version in use, reachable) vs potential (outdated/abandoned/suspicious, no known exploit).
4. Recommend safe upgrades: minimal version bump that patches, semver-compatible where possible, breaking-change review for majors.
5. Review install scripts and permission scope before adopting new packages.
6. Verify upgrades: tests pass, build succeeds, no security control weakened.
7. Never make destructive changes or remove a control "because a dependency is old" without replacement.

## Engineering Principles

- **Vulnerable ≠ exploited.** A dependency with a CVE is only a confirmed risk if the vulnerable code path is reachable in this project; otherwise it's potential.
- **Minimal bump.** Patch with the smallest version change that fixes the issue; avoid major-version jumps unless required.
- **Lockfile is source of truth.** Deterministic installs (`npm ci`) prevent drift and surprise transitive changes.
- **Review before adopt.** New dependencies get a maintenance, license, and permission review; install scripts inspected.
- **Transitive risk counts.** A deep dependency with a CVE matters if reachable; consider the whole tree.
- **Don't remove security for convenience.** An old dependency isn't automatically replaced; an unmaintained security-critical one is a migration project, not a one-line delete.
- **Verify after upgrade.** Tests, build, and security controls must still pass.

## Decision-Making Framework

| Question | Correct answer |
| :--- | :--- |
| Is it a confirmed risk? | Only if vulnerable version is in use AND the vulnerable code path is reachable; otherwise potential. |
| How to upgrade? | Minimal patch version that fixes; semver-compatible; review changelog/breaking changes for majors. |
| New dependency adoption? | Review maintenance, releases, license, maintainers, install scripts, permission scope; add to lockfile. |
| Transitive vuln? | Assess reachability; if reachable, patch or replace; if not, track but lower priority. |
| Lockfile drift? | Regenerate with deterministic install; commit lockfile; align manifest. |
| Confirmed vs potential? | Confirmed = vulnerable reachable version in use; potential = outdated/abandoned/suspicious without known reachable exploit. |

## Workflow

1. Run a dependency scan (npm audit, snyk, osv-scanner, dependabot) as the starting point.
2. Manually verify every hit: is the version actually installed? is the vulnerable function/import used? is it reachable? (eliminate false positives).
3. Classify each: direct vs transitive, confirmed (reachable vuln) vs potential (outdated/abandoned/suspicious).
4. For confirmed: recommend the minimal patch version; assess breaking changes; plan staged rollout + rollback.
5. For potential: assess whether to upgrade, replace, pin, or accept risk; document the decision.
6. For new dependencies: review maintenance, install scripts, permission scope; add to lockfile.
7. Verify: tests pass, build succeeds, security controls intact, lockfile committed.
8. Report findings with version, advisory, reachability, severity, remediation, verification.

## Implementation Guidelines

- Pin exact versions in manifest; commit lockfile; install with `npm ci` (or equivalent deterministic command) in CI.
- Review `package.json`/`requirements.txt` for `*` or `latest` ranges; pin to exact or `~`/`^` with lockfile control.
- Inspect install scripts (`preinstall`, `install`, `postinstall`) of new packages before adopting.
- Audit transitive dependencies; use tools that show the full dependency tree (`npm ls`, `depcheck`, `snyk`).
- Before upgrading a major version, read the changelog and migration guide; test in a branch first.
- For abandoned packages (no releases/commits in 12–24 months, low downloads, unresolved issues): plan replacement or fork/maintain.
- For typosquatting/suspicious packages: compare name to the intended package, check maintainer reputation, inspect source for obfuscation.
- Never `eval` or dynamically require package names from user input.

## Security Requirements

- No known-vulnerable dependency versions in use where the vulnerable path is reachable.
- Lockfile committed and matches manifest; CI uses deterministic install.
- New dependencies reviewed for maintenance, install scripts, permission scope before adoption.
- Vulnerable dependencies upgraded to the minimal patched version; breaking changes reviewed.
- Transitive vulnerabilities assessed for reachability; patched or replaced if reachable.
- Install scripts inspected; suspicious scripts rejected.
- Dependency upgrades verified: tests pass, build succeeds, security controls intact.

## Performance Considerations

- Dependency scanning adds CI time; run on PRs and schedules, not necessarily every commit.
- Large dependency trees slow installs; prune unused dependencies (`depcheck`, `npm prune`).
- Minimal patch upgrades reduce rebuild/re-test surface.

## Reliability Considerations

- A major-version upgrade may introduce breaking changes; test in a branch, feature-flag if needed, keep rollback ready.
- Removing an unmaintained dependency that provides a security control (e.g., sanitizer, crypto) must include a replacement before removal.
- Lockfile drift in production causes non-deterministic builds; enforce lockfile-committed CI (`npm ci`).
- A dependency with install scripts can fail in restricted CI environments; review scripts before adopting.

## Testing Requirements

- After any dependency change: full test suite passes, build succeeds, lint/typecheck clean.
- For security-relevant deps (sanitizer, crypto, auth): run their specific security tests plus app tests.
- Verify vulnerable code path no longer reachable after patch (or version no longer flagged by scanner).
- Confirm no new install-script side effects after adding a package.
- Confirm lockfile is committed and `npm ci` reproduces the install.

## Observability Requirements

- Dependabot/renewal alerts routed to a tracked channel; SLA for critical patches.
- Log dependency changes in PRs (what changed, why, security impact).
- Alert on new vulnerable versions published for dependencies in use.
- Track time-to-patch for critical vulnerabilities.

## Common Failure Modes

- Treating every `npm audit` hit as equally severe (many are transitive/unreachable → potential, not confirmed).
- Upgrading major versions without reviewing breaking changes (breaks app or weakens controls).
- Installing packages with `*`/`latest` ranges and no committed lockfile (non-deterministic, surprise transitive changes).
- Adopting a package with a malicious `postinstall` script without inspection.
- Removing an unmaintained sanitizer/crypto dependency without a replacement (weakens security).
- Ignoring transitive dependencies (the vuln lives four levels deep).
- Not verifying after upgrade (tests don't run, build breaks silently).
- Committing `package-lock.json` changes without reviewing what changed in the tree.

## Troubleshooting

For a flagged dependency, confirm the version is actually in `node_modules`/installed tree (not just declared) and that the vulnerable import/function is used in your code (reachability). For an outdated package, check last release/commit and issue responsiveness before labeling abandoned. For a suspicious package, compare the name carefully to the intended one and inspect the source for obfuscation. After an upgrade, run tests + build + security-relevant checks, confirm the scanner no longer flags it, and confirm the lockfile changed only as expected. Never remove a security-critical dependency without a tested replacement.

## Tool Usage

Use the package manager's audit (`npm audit`, `pip audit`, `cargo audit`, `go vulncheck`), lockfile inspection, dependency-tree tools (`npm ls`, `snyk`, `osv-scanner`), and registry checks (last release, maintainers, downloads). Verify with build + tests. Never run install scripts from untrusted packages; never print secrets found in dependency config.

## Interaction With Other Skills

- **application-security**: this skill identifies vulnerable components (OWASP A06); application-security defines how they're used safely.
- **api-security**: coordinates on auth/framework dependency risk for API servers.
- **backend-security**: coordinates on database driver, ORM, crypto dependency versions.
- **frontend-security**: coordinates on npm package risk in client bundles and sanitizer versions.
- **infrastructure-security**: this skill covers app dependencies; infrastructure-security covers container base images/OS packages.
- **security-audit**: this skill feeds dependency findings; security-audit scores severity and prioritizes remediation.
- **devops-engineer**: coordinates on CI/CD install determinism (`npm ci`) and dependency-update policy.

## Expected Output

A dependency report: every dependency with version, direct/transitive status, advisory match (if any), confirmed/potential label, reachability assessment, severity, remediation (minimal patch / replace / accept-risk / review), and verification step — ordered by real risk, no false positives, no destructive removals without replacement. Followed by post-upgrade verification (tests/build/security controls pass, lockfile committed).

## Examples

**Request**: "`npm audit` reports a high-severity vulnerability in a dependency."

**Approach**: Confirm version is installed (not just declared) → determine direct vs transitive → check if the vulnerable import/function is used in the project's code paths (reachability) → if reachable: confirmed risk → recommend minimal patch version (e.g. `1.2.3` → `1.2.4`) → review changelog for breaking changes → upgrade in a branch → run tests + build + security checks → confirm scanner no longer flags → commit lockfile. → if not reachable: potential risk → track, lower priority, plan upgrade when convenient → document why it's not currently exploitable. → never delete `node_modules` or randomly upgrade majors "to clear the audit."

**Request**: "Adopt a new sanitization library for rendering user HTML."

**Approach**: Review maintenance (last release, commit frequency, issue responsiveness) → check downloads/community trust → compare name to intended package (typosquatting check) → inspect install scripts (`preinstall`/`postinstall`) → review permission scope (does it need network/fs access?) → add to manifest with exact version + lockfile → `npm ci` in CI → write tests confirming dangerous markup is stripped → document the allowlist policy so future maintainers don't expand it silently.
