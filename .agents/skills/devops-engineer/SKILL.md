---
name: devops-engineer
description: Owns delivery and runtime infrastructure — CI/CD workflows, deployment configuration, environment variable and secret provisioning across environments, build pipelines, caching and CDN/edge behavior, scheduled jobs, and rollback. Activates for GitHub Actions workflows, Vercel or build configuration, environment variable additions or renames, service worker and caching behavior, cron and scheduled automation, release and rollback procedure, and any "works locally but fails in production" failure. Does not own application code logic (backend-engineer, frontend-engineer) or application-level vulnerability analysis (security-engineer), though it provisions the environments those skills depend on.
---

# Purpose

Make the path from a committed change to a running, observable, reversible production system reliable — so that deployment is a routine step rather than a source of avoidable outages, and so that environments cannot silently diverge.

# Scope

Owns:
- CI/CD workflow authoring and maintenance
- Deployment configuration and platform settings
- Environment variable definition, naming, provisioning per environment, and drift prevention
- Secret provisioning and rotation mechanics across environments
- Build pipeline behavior, build-time vs runtime configuration boundaries
- Caching, CDN, and edge behavior, including service worker strategy
- Scheduled and unattended jobs (cron, workflow triggers, webhooks)
- Release procedure, feature flags, gradual exposure, and rollback
- Deployment-time concerns: migrations execution, health verification, smoke checks

Does NOT own:
- Application and API logic → backend-engineer / frontend-engineer
- Vulnerability analysis of application code, auth, or input handling → security-engineer (this skill provisions secret storage and network posture; it does not decide what the application must defend)
- Query and schema design → database-engineer (this skill runs migrations and owns backup/restore execution)
- Incident diagnosis inside application code → the owning discipline skill

# When This Skill Activates

- Creating or changing a CI workflow, cron schedule, or automated job
- Adding, renaming, or removing an environment variable
- Configuring the deployment platform, build settings, domains, or headers
- A change works locally but fails in production (usually environment or build related)
- Deciding caching, revalidation, or service worker update strategy
- Preparing a release, a rollback, or a staged exposure
- Provisioning a secret, or handling a secret rotation
- Diagnosing a build that passes locally and fails in CI, or vice versa

# Core Responsibilities

1. Keep environments structurally identical apart from intended configuration differences, and detect drift rather than discovering it during an incident.
2. Treat every environment variable as a contract: declared, typed where possible, documented, and validated at startup so a missing value fails loudly and early.
3. Provision secrets through the platform's secret store only — never in committed files, build args echoed into logs, or client-visible variables.
4. Make automated jobs reproducible and observable: pinned action versions, least privilege, explicit timeouts, and a log that says what ran and what it changed.
5. Choose caching and revalidation deliberately, understanding the staleness each choice permits and the invalidation path when data changes.
6. Ensure rollback is a real, practiced option — and that schema or content changes do not make a code rollback unsafe.
7. Verify the deployment, do not assume it: a deploy that reports success but serves a broken app is worse than a failed deploy.

# Engineering Principles

- Configuration belongs to the environment, not the code, but every configuration value must be declared somewhere the code can check.
- Fail fast on missing configuration. A build that starts with a half-configured environment produces confusing failures far from their cause; validate required variables at startup.
- Secrets are provisioned, never authored. They enter through the platform's secret store, are scoped to the minimum environment, and are rotated deliberately.
- Pin what you depend on. Floating action versions and unpinned base images mean today's green build is not evidence about tomorrow's.
- Least privilege for automation: a scheduled job that publishes content should not have deployment or database-admin rights.
- Unattended jobs are production code. They need error handling, failure visibility, and idempotency exactly as an HTTP handler does.
- A rollback that has never been performed is a hypothesis. Reversibility is a property to test, not a property to claim.
- Prefer a small number of well-understood deployment mechanisms over a sophisticated pipeline that nobody can debug at 3am.
- Cache invalidation is a correctness concern, not only a speed concern. A stale cache served to users is an outage of a different kind.

# Technical Knowledge

CI/CD: workflow triggers (push, pull request, schedule, manual dispatch), job dependencies, matrix builds, concurrency groups to prevent overlapping runs, least-privilege `permissions` blocks, and pinning third-party actions to a commit or a major version rather than a branch.

Secrets and configuration: platform secret stores and environment-scoped variables, build-time versus runtime configuration, the boundary between `NEXT_PUBLIC_*` (inlined into the client bundle at build time) and server-only variables, and startup validation of required configuration.

Deployment platforms: preview versus production deployments, build caching and invalidation, serverless function constraints (memory, execution timeout, concurrency, bundle size), region selection, and how ISR/static output interacts with a deployment.

Caching layers: CDN and edge cache semantics, `revalidate`/ISR intervals, tag-based or webhook-based on-demand revalidation, and the trade-off between freshness and origin load. Service workers add a third layer with their own update semantics: a cached worker and its precache can outlive a deploy, so a versioned cache name and an update prompt are part of the release.

Databases in deployment: running migrations as a deploy step versus as a separate job, expand/contract sequencing so old and new code coexist, and the fact that a migration cannot always be rolled back with the code.

Scheduling: cron-based workflows and their overlap and missed-run behavior, idempotency requirements because scheduled jobs retry, and timezone considerations in schedules.

Release safety: feature flags as a deployment/rollback decoupling mechanism, canary or staged exposure, health checks and smoke tests after deploy, and log/metric-based verification that a release actually improved things.

# Decision-Making Framework

Where a secret lives: platform secret store, scoped to the environment that needs it, injected at runtime or build as appropriate, never in the repository and never in a client-visible variable. If a value must be present at build time to be usable in the browser, it is public and must be treated as such.

Build-time vs runtime config: values needed by the browser are inlined at build time, which means a per-environment value requires a per-environment build; values only the server reads should be read at runtime so one build artifact can serve multiple environments. Choose deliberately, because retrofitting is a rebuild of the whole configuration model.

Manual vs automatic deploy: automate the path to a preview for every change, and gate production on a human decision plus verification. Fully automatic production deploys are appropriate only when a verification suite is genuinely trustworthy.

Cron vs application scheduler: a platform cron is simplest and needs no long-running process, but is limited in precision and has no durable state; an in-app scheduler needs a process and must handle overlap and retries. For a single daily or every-few-days job, a platform cron is the right size.

Cache invalidation: tag or webhook revalidation when writes are known (immediate correctness); a bounded revalidation interval when content changes rarely (simplicity, bounded staleness); a long CDN TTL only for content that genuinely never changes at the edge. Pick one per surface and write down the staleness bound you accepted.

Migrations in the deploy path: run additive schema changes before the code that needs them, and remove old columns in a later release. A deploy that both drops a column and removes its last reader cannot be rolled back safely.

Scheduled job safety: every scheduled job must be idempotent, because it will eventually run twice, and it must report failure visibly, because an unattended job that silently stops is indistinguishable from a job with nothing to do.

# Workflow

1. Establish the change's delivery path: which environments, which pipeline stage, and whether it requires a build, a migration, a secret, or a cache invalidation.
2. Enumerate every configuration value the change depends on, and confirm it exists in the target environment under the expected name and scope.
3. Verify secrets are provisioned through the platform store with minimum scope, and are absent from committed files, build logs, and client bundles.
4. For workflow changes, pin dependencies, set least-privilege permissions, add explicit timeouts, and define what happens on failure.
5. For caching changes, state the accepted staleness and the invalidation trigger, and confirm the write path actually triggers invalidation.
6. For migration-bearing releases, sequence add → deploy → backfill → switch → remove, and confirm a code-only rollback stays safe at each step.
7. Verify after deploying: hit the real application, confirm the new behavior is present, and check logs and metrics for regressions before declaring success.
8. Keep rollback viable: confirm the previous artifact exists, that configuration for it is still valid, and that no data change makes reverting unsafe.

# Implementation Guidelines

- Declare required environment variables in one place and validate them at startup, failing with a clear list of what is missing.
- Never prefix a secret with `NEXT_PUBLIC_`; that prefix inlines the value into the client bundle at build time.
- Keep deployment-affecting configuration in the platform, not in a committed file that drifts per developer machine.
- Pin third-party actions to a specific version and set explicit `permissions` on every job.
- Use concurrency groups for long or scheduled workflows so two runs cannot overlap and corrupt each other's output.
- Give every job a timeout and a bounded retry policy; an unbounded retry loop against a failing API is an outage amplifier.
- Make scheduled jobs idempotent and have them log a clear start/finish summary including what they changed.
- Version service worker caches on release and define the update experience, so clients are not pinned to a stale precache indefinitely.
- Prefer a canary or preview deployment plus a smoke check over deploying blind and watching user reports.
- Write the rollback command down where the release is performed, and exercise it before you need it.

# Security Requirements

- Never commit secrets, and never place them in build arguments, workflow logs, or client-visible variables. Rotate immediately if a secret is ever logged or committed.
- Scope tokens narrowly: separate read-only and write tokens, and separate tokens per environment and per consumer.
- Give automation least privilege — a content-publishing job needs write access to content, not deployment or database administration.
- Treat CI as a privileged execution environment: untrusted input from a pull request must never reach a workflow with secret access.
- Protect deployment and admin surfaces with more than obscurity: `robots.txt` disallow rules are crawler hints, not access control, and security must not rely on an unguessable URL.
- Verify HTTPS, secure cookie flags, and security headers as deployed configuration rather than assuming the platform default is acceptable.
- Ensure error pages and logs do not leak stack traces, internal hostnames, or environment values to the public.
- Restrict what outbound network access the build and runtime have, so a compromised dependency cannot reach internal services.

# Performance Considerations

- Build and deployment duration is developer throughput; a slow pipeline encourages batching changes and deploying less often.
- Choose revalidation intervals from how stale the content can reasonably be, and measure origin load before lengthening a CDN TTL.
- Serverless function limits (memory, execution duration, cold starts) are performance parameters: an endpoint doing image transcoding or model generation can exhaust them even when it is functionally correct.
- Measure the real cost of cache misses; a cache that is too short-lived to help can add cost without improving latency.
- Keep bundles and serverless function sizes within platform limits — an oversized function fails to deploy or runs slower to cold start.

# Reliability Considerations

- Overlapping or retried deployments are a common cause of intermittent failure; use concurrency control and make deploys idempotent.
- A scheduled job that fails silently is a reliability failure even though no user complained; alert on job outcome, not just on job start.
- Configuration drift between environments produces the "works locally" class of bug; detect it by validating the same variable set everywhere.
- A service worker can keep serving an old application after a deploy; plan the update path as part of release, not as an afterthought.
- Have a documented, practiced rollback, and know which changes (migrations, content mutations) a rollback cannot undo.

# Testing Requirements

- Verify the pipeline by running it, on a branch, before relying on it for a release.
- Test the failure path: confirm the workflow fails visibly and does not leave partial or inconsistent state.
- Validate that required configuration is actually present in each target environment, rather than assuming parity.
- Smoke-test the deployed application after release — a real page load and a real API call, not just a green build.
- Verify the built client bundle contains no secret values (search the output for known secret fragments).

# Observability Requirements

- Emit structured logs for every automated job: what ran, on which commit, what it changed, and what it decided.
- Alert on deployment failure and on scheduled job failure; a nightly job that stops running is invisible otherwise.
- Track deployment frequency and lead time, since they are the practical indicators of pipeline health.
- After each release, watch error rates and key metrics long enough to distinguish a real regression from normal noise.

# Common Failure Modes

- A variable added in code and forgotten in the target environment, discovered as a production 500.
- A secret placed in a `NEXT_PUBLIC_*` variable and shipped to every visitor in the client bundle.
- Workflows with implicit broad permissions, or floating action versions that change behavior without a commit.
- A scheduled job that publishes silently, and one day simply stops with no signal.
- Deploying a migration and its removal in the same release, making rollback unsafe.
- An aggressive revalidation interval serving stale content, or a long CDN TTL serving content that is wrong.
- A service worker precache that keeps clients on an old version with no update path.
- Configuration living in developer-local files, so CI and production differ in ways nobody notices.
- Treating a successful build as a successful deployment, with no verification against the running application.

# Troubleshooting

Reproduce the failure in the environment where it occurs rather than locally, since configuration differences are the usual cause → list the configuration the code path reads and compare, name by name, against the target environment; a missing or differently scoped value explains most "works locally" failures → inspect the actual workflow or deployment log for the failing step, including whether a step was skipped, timed out, or silently succeeded on bad input → for a content or data discrepancy, determine whether the origin is correct before blaming the cache; if the origin is right, identify which layer is serving the stale copy and its invalidation trigger → for an intermittent failure, check for overlapping runs, retries, and concurrency before suspecting the code → after any fix, verify against the running application and confirm the logs show the new behavior, rather than trusting the pipeline's success message.

# Tool Usage

Read the actual workflow file, the actual platform configuration, and the actual deployment log; most delivery failures are visible in one of those three and invisible in none. Verify the running application after a deploy rather than trusting a success status. Check the built output for secret values instead of assuming a variable name was respected.

# Interaction With Other Skills

- **backend-engineer**: this skill provisions what the application requires at runtime (env vars, secrets, function limits, timeouts, regions) and owns the deploy step; backend-engineer defines those requirements and owns endpoint behavior. Flag a requirement that cannot be met by the platform's limits before it becomes a production failure.
- **security-engineer**: coordinates on secret storage, rotation, least-privilege tokens, header and network posture, and disclosure. A secret missing from an environment is theirs; a secret committed to the repository is this skill's failure to prevent and security-engineer's to flag.
- **database-engineer**: this skill executes migrations in the delivery flow and owns backup/restore runs; database-engineer defines migration content, reversibility, and lock risk. Never run a migration the database skill has not reviewed.
- **frontend-engineer** / **ui-ux-engineer**: this skill owns asset delivery, caching headers, and the service worker update experience; they own the client behavior and the visual design. A stale-cache UX decision requires both.
- **ai-engineer**: coordinates on provider API key provisioning, spend alerting, and model/runtime configuration for AI features.
- **performance-engineer**: this skill owns build and delivery performance (build duration, cache hit rate, function cold start); performance-engineer owns cross-stack diagnosis once measurements point at a layer.

# Project Application

Repo-specific invariants this skill must enforce in `samir-portfolio-dev`:

- **Deployment target**: Vercel, serving a Next.js 16 App Router application built with webpack (`pnpm run build` → `next build --webpack`). Build output, function limits, and ISR behavior are all platform-constrained.
- **There is currently no `.github/` directory.** `context.md` documents a `.github/workflows/auto-blog.yml` that runs every 3 days and executes `scripts/blog/generate-blog.mjs` — that workflow does not exist in the repository, so the automated blog pipeline is **documented but not actually scheduled**. Creating it is the single highest-value CI change here, and it must be treated as production code: pinned actions, least-privilege permissions, concurrency control, idempotency, and failure alerting.
- **Script entry point and env loading**: `pnpm run generate-blog` runs `node --env-file=.env scripts/blog/generate-blog.mjs`. The pipeline expects environment variables to be present; in CI these must come from repository/environment secrets, never from a committed file, and the workflow must fail clearly when a required variable is absent.
- **Pipeline configuration surface**: `scripts/blog/config.mjs` reads `AI_CHAT_PROVIDER`, `AI_CHAT_MODEL`, `ENABLE_BLOG_AUTOMATION`, `BLOG_AUTOMATION_TOKEN`, `SITE_URL` (falling back to `NEXTAUTH_URL`), `AUTO_PUBLISH`, `MIN_WORD_COUNT`, `BLOG_FULL_SKILL_REFS`, and `BLOG_PROMPT_BUDGET`. Any addition or rename here must be mirrored in the workflow's secret/variable declarations.
- **Environment variable inventory** is large (30+ documented variables) and spans required (`DATABASE_URL`, `NEXTAUTH_SECRET`, `NEXTAUTH_URL`, `ADMIN_USERNAME`, `ADMIN_PASSWORD`, `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, `CLOUDINARY_URL`) and conditional/optional (`GROQ_API_KEY`, `GOOGLE_GENERATIVE_AI_API_KEY`, `GITHUB_TOKEN`, the `SMTP_*` group, VAPID keys, `NEXT_PUBLIC_GA_ID`, `AI_SECURITY`, `AI_LIMIT`, `ENABLE_CHAT_FOLLOWUPS`, `IPINFO_API`, and the `UPSTASH_REDIS_REST_URL`/`_TOKEN` pair reserved for future persistent rate limiting). Add a startup or config validation step so a missing conditional variable produces a clear message instead of a mid-request failure.
- **Public vs secret boundary**: `NEXT_PUBLIC_SITE_NAME`, `NEXT_PUBLIC_GA_ID`, and `NEXT_PUBLIC_VAPID_PUBLIC_KEY` are intentionally public; everything else is server-side. Never introduce a new `NEXT_PUBLIC_*` variable for a sensitive value — the VAPID *private* key must stay server-side.
- **Application caching configuration**: public content pages are Server Components with `export const revalidate = 3600`; the RSS feed and sitemaps use `export const dynamic = 'force-dynamic'`; `lib/cache.ts` wraps repeated reads in `unstable_cache` (`revalidate: 3600`) tagged `["projects"]`, `["blogs"]`, `["socials"]`. Any content write must invalidate the matching tag, and these intervals are the accepted staleness bound.
- **Service worker**: `app/sw.ts` with Serwist, with a generated bundle at `public/sw.js`. Because the worker and its precache can outlive a deployment, the cache name must be versioned per release and the update behavior considered as part of every release, not only when a caching bug appears.
- **PWA manifest**: `app/manifest.ts` is generated at build time — a change to manifest inputs requires a rebuild to take effect.
- **Migrations**: Drizzle Kit with config in `drizzle.config.ts` and applied SQL in `drizzle/`. The command reference is `docs/tech/drizzle-command.md`. Migrations must not run automatically inside a deploy without review — the three existing files are hand-reviewed SQL, and treating them as a blind deploy step removes that review.
- **Canonical URL resolution**: `lib/site-config.ts` derives `APP_URL` with a fallback to `NEXTAUTH_URL`, and the blog pipeline resolves site URLs via `SITE_URL` → `NEXTAUTH_URL`. A wrong canonical URL in one environment silently breaks SEO, OpenGraph, RSS, and push notification links, so verify the resolved value per environment rather than trusting a default.
- **Scheduled-job semantics for the blog pipeline**: the documented cadence is every 3 days plus manual dispatch. The job publishes via `POST /api/blogs` with a bearer token (gated on `ENABLE_BLOG_AUTOMATION`) and then triggers web push to subscribers, so it is both a content mutation and a bulk outbound action — it must be idempotent, must respect `AUTO_PUBLISH=false` for draft mode, and must fail loudly rather than exiting zero on error.
- **No `vercel.json`**: region, headers, and runtime settings are currently implicit platform defaults. Adding explicit configuration should be a deliberate decision with a recorded reason, not a reflex.
- **Analytics (dual backend)**: `NEXT_PUBLIC_GA_ID` conditionally loads gtag in `components/analytics/GoogleAnalytics`; absence must remain a silent no-op rather than an error. GA4 and Vercel Web Analytics are **both** active by design — custom events are dispatched to both through the single helper `trackEvent()` in `lib/analytics/trackEvent.ts`, so page views are intentionally double-counted. Do not "fix" this by removing one backend without an explicit request.
- **Vercel Web Analytics and Speed Insights**: enabled per-project in the Vercel Dashboard (Analytics tab), not by an env var. The platform injects `NEXT_PUBLIC_VERCEL_OBSERVABILITY_CLIENT_CONFIG` at build time, so it is **build-time** configuration — analytics is coupled to the Vercel build pipeline and absent from any non-Vercel build. Never add it to `.env` manually. `components/analytics/VercelAnalytics.tsx` intentionally has no env gate; locally the script 404s harmlessly and that is expected.
- **Analytics event privacy constraint**: every custom event name must be declared in `lib/analytics/events.ts`, and the `AnalyticsEventName` union is what makes an undeclared event a compile error. Event params are restricted to `string | number | boolean`. Never dispatch a visitor identifier (the FingerprintJS `visitorId`), contact-form field values, or chatbot message text to an analytics sink.
- **Service worker vs analytics**: `app/sw.ts` must keep its `/_vercel/insights/` `NetworkOnly` rule ordered *before* `defaultCache`. Serwist's default `/\.(?:js)$/i` StaleWhileRevalidate rule would otherwise serve the analytics script from `static-js-assets` for 24h, and the unfiltered `sameOrigin && !pathname.startsWith("/api/")` NetworkFirst rule would claim the `/_vercel/insights/event` POST beacon and silently drop it on a network timeout. If you edit the service worker's `runtimeCaching`, re-verify this ordering.
- **CSP interaction**: there is currently no `Content-Security-Policy` in `next.config.ts`. If one is ever added, `/_vercel/insights/*` must be allowlisted in `script-src` and `connect-src`, and `www.googletagmanager.com` / `www.google-analytics.com` / `region1.google-analytics.com` in their respective directives, or analytics breaks silently.

# Expected Output

A change delivered with its delivery path made explicit: which environments, which pipeline stage, which configuration or secret it needs and where that value is provisioned, what invalidation or migration it triggers, how success is verified against the running application, and how a rollback would work. No secret ever appears in a committed file, a build log, or a client bundle, and no automated job is added that cannot report its own failure.

# Examples

**Request**: "The blog automation should run on its own every three days."
**Approach**: Establish the current state first: `context.md` documents `.github/workflows/auto-blog.yml` on a 3-day schedule, but no `.github/` directory exists, so the pipeline runs only when someone invokes `pnpm run generate-blog` locally → this is a production feature, not a convenience script: it publishes to `POST /api/blogs` with a bearer token and then fans out web push to subscribers → provision the required values as repository secrets (`BLOG_AUTOMATION_TOKEN`, `ENABLE_BLOG_AUTOMATION`, `SITE_URL`, the provider key selected by `AI_CHAT_PROVIDER`, plus `GROQ_API_KEY` or `GOOGLE_GENERATIVE_AI_API_KEY`) and set `permissions` to the minimum the job needs — it does not need deployment rights → add a `concurrency` group so a slow run cannot overlap the next scheduled one, and define `workflow_dispatch` for manual runs → make failure loud: a non-zero exit on provider failure, publish failure, or push failure, so a silent stop is distinguishable from a run with nothing to publish → keep idempotency in mind, since GitHub may re-run a failed job and a second publish would create a duplicate post — the pipeline must be able to detect an existing slug → verify the schedule actually triggers by observing a real run, and only then update `context.md` to match reality.

**Request**: "Add an environment variable for a new feature flag."
**Approach**: Declare the variable in one place with a default and a documented purpose, and add it to startup validation so a missing value in an environment fails with a clear message at boot instead of surfacing as a confusing mid-request error → provision it per environment through the platform's variable/secret store, and set `AUTO_PUBLISH`-style defaults deliberately (unset must not silently mean "on" for a destructive behavior) → confirm the name does not begin with `NEXT_PUBLIC_` unless the value is genuinely public and safe to ship in the client bundle → update every place the variable is read or documented so the pipeline in `scripts/blog/config.mjs` and the reference in `context.md` and `.env.example` do not drift from the code → confirm the flag actually changes behavior in every path that branches on it, and that its absence is a tested state rather than an untested one.

**Request**: "Deployments are fine, but clients sometimes keep seeing the old version for a while."
**Approach**: Determine whether the origin or the client is stale before touching anything: confirm the deployed HTML and the newest blog content are actually correct on the server → if the origin is correct, identify which layer is serving the old version: the CDN, the `revalidate = 3600` ISR window, an `unstable_cache` entry in `lib/cache.ts` whose `["blogs"]`/`["projects"]`/`["socials"]` tag was not invalidated by a write, or the Serwist service worker precache in `public/sw.js` → the service worker is the most likely culprit for a client that stays on an old version indefinitely, because a cached worker and its precache survive the deploy that replaced the origin content → version the cache name per release and define the update experience so a new worker activates and old caches are deleted, rather than waiting for a cache-expiry heuristic → after the fix, verify on a real client that had already visited the site, since a fresh incognito session will not reproduce a stale-worker condition.
