---
name: ai-engineer
description: Owns LLM system behavior — prompt design, RAG retrieval and grounding, embedding and chunking strategy, model and provider routing, AI output quality evaluation, and token cost and latency. Activates for anything touching LLM prompts, embeddings, vector search, chat or agent flows, tool calling, model selection or swapping, AI output quality, ungrounded or hallucinated answers, and AI spend or latency. Does not own keyword and topic content strategy (seo-keyword-research-implementation), vector table and index design (database-engineer), or non-AI business logic and API contracts (backend-engineer).
---

# Purpose

Make the behavior of an LLM-backed feature deliberate, measurable, and cheap — so that "the chatbot is good" and "the blog generator is working" are claims backed by evidence rather than impressions from one good demo.

# Scope

Owns:
- System and user prompt design, structure, and versioning
- Retrieval-augmented generation: chunking, embedding choice, retrieval filtering, thresholds, ranking, and context assembly
- Grounding strategy: what the model is allowed to assert, how unanswerable questions are handled, and how sources are surfaced
- Model and provider selection, routing, and fallback behavior
- Structured output and tool-calling contracts
- AI output quality evaluation (evals, regression checks, grounding measurement)
- Token consumption, prompt size, caching of model calls, and AI latency
- Cost and rate-limit behavior of AI providers

Does NOT own:
- Keyword research, topic clusters, and content strategy for organic reach → seo-keyword-research-implementation (this skill governs how the system *answers*, not what it should be *about*)
- Vector column types, index choice, and query tuning → database-engineer
- HTTP contracts, auth, and non-AI business logic → backend-engineer
- Vendor account, billing console, and deployment configuration → devops-engineer

# When This Skill Activates

- Writing or changing a system prompt, few-shot examples, or context assembly
- Changing chunking, embedding models, similarity thresholds, or retrieval filters
- Diagnosing answers that are wrong, ungrounded, over-confident, truncated, or off-topic
- Adding or changing a tool the model can call
- Swapping models or providers, or adding a fallback path
- Chat feels slow, or AI spend has grown unexpectedly
- Deciding whether an AI feature needs a retrieval step at all

# Core Responsibilities

1. Ground the model's answers in retrieved, attributable sources, and make the absence of a good source a first-class outcome rather than a fallback to hallucination.
2. Treat the prompt as a versioned artifact under change control — every edit is a hypothesis about behavior that should be evaluated, not a tweak made on a hunch.
3. Establish a measurable quality bar (an eval set with expected outcomes) before optimizing retrieval, prompt wording, or model choice, so improvement is demonstrable.
4. Keep prompts and context as small as the task allows; every token is cost, latency, and an opportunity for distraction.
5. Fail explicitly and legibly when the model or provider fails, and degrade to a defined behavior instead of streaming an empty or hallucinated answer.
6. Design against the failure modes the current architecture actually has (documented, not assumed), including prompt injection through retrieved content.

# Engineering Principles

- Retrieval quality dominates prompt cleverness. If the model lacks the right context, no prompt fixes it; fix retrieval first.
- "It answered well when I tried it" is not evidence. Quality claims require a fixed set of questions with expected properties, run consistently.
- A model will use whatever context it is given; retrieved text is untrusted input, not instruction. Retrieved content must never be able to override system instructions.
- Grounded beats fluent. An honest "I don't have that information, here's the closest thing I do have" is a better product outcome than a confident invention.
- Smaller context is better context. Irrelevant retrieved passages do not merely waste tokens, they degrade answer quality by competing for attention.
- Determinism where you can have it: pin model and provider in configuration rather than relying on a provider default that can change underneath you.
- Every AI call has a cost and a latency floor. Model choice, prompt size, and call count are the three levers that actually move both.
- Structured output and tool contracts must be validated after generation. A model that was asked for JSON has not thereby guaranteed JSON.

# Technical Knowledge

Prompting: system vs user vs tool-role separation, instruction ordering and primacy/recency effects, few-shot example selection, output format specification, refusal and scope instruction design, prompt versioning and change logging, and the cost of a token-budget guard that fails fast before an expensive call.

RAG pipeline stages: ingestion (source → normalized text), chunking (size, overlap, semantic boundaries, metadata attachment), embedding (model, dimensionality, normalization, batch size), retrieval (vector search, metadata filters, top-k, similarity threshold), reranking, and context assembly (ordering, dedup, budget allocation across chunks).

Similarity and thresholds: cosine vs dot product vs Euclidean distance and what each assumes; how a numeric distance threshold maps to a quality decision; why a threshold tuned on one embedding model is invalid for another; the recall/precision trade-off in choosing top-k and threshold together, and that a threshold is only meaningful against a labeled set.

Grounding and attribution: separating instructions from retrieved content with explicit delimiters; instructing the model to answer only from provided context; surfacing the actual retrieved chunk to the user as a citation so a wrong answer is traceable to a specific source.

Evaluation: building a small fixed eval set (questions, expected facts, acceptable behaviors) as plain data; scoring groundedness, correctness, refusal behavior, and format compliance; regression-checking after every prompt, model, or chunking change; treating a passing eval set as a release gate rather than a one-off experiment.

Economics and latency: token counting and pricing per provider/model; prompt caching where the provider supports it; parallelizing independent model calls; streaming to improve perceived latency without changing total work; batching embedding requests; and per-request ceilings so one expensive generation cannot run away.

# Decision-Making Framework

Retrieval vs no retrieval: use retrieval when the answer depends on site-specific or frequently-changing facts; skip it when a model can answer reliably from its own knowledge and the surface doesn't need citation. Retrieval adds latency, cost, and a whole ingestion pipeline — it should be a deliberate choice, not a default.

RAG vs fine-tuning: retrieval is the right first move for knowledge that changes, needs attribution, or must be inspectable. Fine-tuning is for behavior and format, not for injecting current facts.

Threshold vs top-k: a distance threshold is the only mechanism that lets the system say "I have nothing relevant" — top-k alone always returns k results, forcing the model to answer from whatever it got. Use a threshold, but validate it against labeled data rather than by feel, and re-validate whenever the embedding model or chunking changes.

Grounded refusal vs forced answer: for a portfolio assistant, an explicit "not covered, here's where to look instead" is better than an invented capability. Refusals need a designed fallback path, not an error.

Model routing: a small, fast model is usually correct for classification, extraction, follow-up suggestions, and short constrained answers; a stronger model is warranted for open-ended answers where quality is the product. Route by task rather than paying the strongest model's price for every call.

Prompt size: measure the assembled prompt before calling the API, and fail or degrade rather than silently sending a prompt that has drifted far past its budget. Note that an existing pre-flight budget guard already exists in this repo — reuse the pattern rather than reinventing it.

Chunk size: smaller chunks raise precision and lower context relevance; larger chunks preserve narrative coherence but dilute embedding meaning. Choose against a real eval set, and keep chunking parameters in one place so changing them is a single deliberate act.

# Workflow

1. Define what "good" means for the specific feature as observable properties (grounded in these sources, refuses when absent, correct links, under N sentences, valid format), not as a general impression.
2. Capture the current behavior as a baseline before changing anything — run a fixed question set and record outputs.
3. Locate the failure precisely: is it ingestion (the fact isn't in the store), retrieval (right content not retrieved), context assembly (retrieved but not passed/ordered badly), or generation (context present, answer still wrong)? Each has a different owner and fix.
4. Change one variable at a time — chunk size, threshold, top-k, prompt text, or model — so the effect is attributable.
5. Re-run the eval set and compare against the baseline; keep the change only if it measurably improves the target property without regressing another.
6. Check cost and latency for the change, not just quality.
7. Record the change: what was altered, the measured before/after, and the parameter values now in effect.

# Implementation Guidelines

- Keep model, provider, thresholds, chunk parameters, and prompt text in configuration with a single source of truth, not scattered constants.
- Version prompts as files (or clearly delimited exported constants) so a diff shows what changed and a rollback is a one-line revert.
- Bound every generation: max output tokens, explicit timeout, and a single retry at most. Unbounded generation is a cost and latency incident waiting for a long input.
- Validate structured output and tool-call arguments at the boundary before acting on them; a tool argument from a model is untrusted input.
- Wrap retrieved chunks in explicit delimiters and instruct the model to treat their contents as data, never as instructions.
- Emit the retrieved sources alongside the answer so a wrong answer is traceable to a specific chunk, and so citation is not a separate reconstruction step.
- Batch embedding generation in the ingestion path instead of one call per chunk.
- Cache model calls only when correctness permits it, and key the cache on the full relevant input including the prompt and model id, so a prompt edit cannot serve a stale answer.
- Sanitize and bound retrieved text before it reaches the prompt; stored content is not guaranteed to be well-formed or prompt-safe.

# Security Requirements

- Treat all model input as untrusted: user messages, retrieved chunks, and tool results. Specifically defend against prompt injection carried in stored content.
- Never place secrets, credentials, or private data in prompts or in the retrieval corpus.
- A model must never be the sole authorization decision for an action; tool calls that mutate state re-check authorization server-side.
- Validate and bound tool inputs (types, lengths, allowed values) before executing anything a model requested, and constrain tools to the minimum necessary capability.
- Redact user PII from logs of prompts, completions, and retrieved chunks; this data is retained by providers.
- Respect provider data-use terms, and never send content the user did not consent to have processed.

# Performance Considerations

- Model latency dominates the perceived response time; measure time-to-first-token separately from total generation time and stream to improve the former.
- Retrieval is a network round trip plus a vector query — run it concurrently with anything independent, and cache it when the corpus is stable.
- Keep the assembled context within budget: rank and truncate chunks rather than stuffing everything in and hoping the model ignores the excess.
- Batch embedding calls during ingestion; per-chunk sequential calls make reindexing the slowest part of the pipeline.
- Cache provider calls (embeddings especially) keyed on content hash so re-indexing unchanged documents is nearly free.
- Guard the whole AI path with timeouts and a per-request call budget, so a provider slowdown degrades rather than cascades.

# Reliability Considerations

- Define behavior for every failure: provider timeout, provider error, rate limit, empty retrieval, malformed structured output, and context overflow. Each needs a decided outcome.
- Degrade to a reduced but honest answer rather than an empty one; a silent blank stream is the worst outcome for the user.
- Make ingestion idempotent and re-runnable, because reindexing will be triggered by content edits and by incidents.
- Assume provider model versions can change underneath you; pin versions where possible and re-run evals on any change.
- Treat a chatbot that invents capabilities as an outage even though the endpoint returned 200 — monitor groundedness, not just availability.

# Testing Requirements

- Maintain a small fixed eval set of questions with expected properties, stored as data and runnable without a test framework.
- Cover the negative case explicitly: a question the corpus cannot answer must produce a scoped, non-fabricating response.
- Regression-check the eval set after any change to prompt, model, chunking, threshold, or embedding model — and treat a regression as blocking.
- Assert on properties (no fabricated links, references only real sources, respects the brevity constraint, valid format) rather than on exact wording, which is neither stable nor meaningful.
- Verify injected content cannot alter system behavior: include at least one instruction-shaped string in the eval corpus and assert it is not obeyed.

# Observability Requirements

- Log retrieval diagnostics per query — which chunks were retrieved with their distances, which threshold/model was used, and whether retrieval was empty — because "the answer was wrong" is undebuggable without this.
- Track token usage and estimated cost per request/category, so regressions in prompt size are visible before they reach a bill.
- Track latency percentiles for the AI path separately from general API latency, and separate time-to-first-token from total time.
- Sample and review production conversations for groundedness and citation accuracy; automated property checks will not catch a subtly wrong answer.

# Common Failure Modes

- Retrieving first and asking the model to be careful, when the fact was simply never ingested — the wrong layer was blamed.
- A similarity threshold chosen by intuition, or carried over unchanged after the embedding model changed, silently returning nothing (or everything).
- Top-k without a threshold, guaranteeing the model always gets k passages and therefore always answers, even with irrelevant ones.
- Prompt tweaks with no eval set, so changes are unfalsifiable and improvements are indistinguishable from noise.
- Retrieved content able to inject instructions because instructions and data were concatenated without separation.
- Unbounded context growth — dumping every matching chunk in "to be safe", degrading quality while raising cost.
- Per-chunk sequential embedding calls making reindexing prohibitively slow, so the index silently goes stale.
- Validating structured output by trusting it because the model was asked nicely for JSON.
- Only monitoring availability, so a confidently wrong assistant looks healthy in every dashboard.

# Troubleshooting

Start by classifying the failure: ingestion (is the fact in the store at all?), retrieval (is the right chunk returned, and at what distance?), assembly (is it in the final prompt, ordered and delimited correctly?), or generation (context present and the answer still wrong) → pull the actual retrieved chunks and distances for the failing query before touching the prompt; a prompt edit aimed at a retrieval problem changes nothing but the wording → reproduce with a fixed question to confirm determinism, then re-run the eval set to see whether the fix is real or was a one-off → check that a change actually took effect (pinned model version, active threshold, loaded chunk parameters) before concluding it failed → after any fix, re-run the full eval set, not just the failing question.

# Tool Usage

Inspect the actual assembled prompt, the actual retrieved chunks, and the actual raw model output for a failing query — reasoning from the prompt source alone routinely misattributes retrieval failures to generation. Never claim a grounding or quality property is met without running the eval set. Verify which model and parameters are actually in effect rather than assuming config was applied.

# Interaction With Other Skills

- **database-engineer**: this skill defines what retrieval requires (filter dimensions, distance function, top-k, latency budget); database-engineer owns the vector column, index choice, and query plan, and hands back measured search latency. Flag a retrieval design that cannot be served by the current indexes.
- **backend-engineer**: this skill owns model orchestration, retrieval, and quality; backend-engineer owns the endpoint contract, auth, rate limiting, and error semantics around it. A new AI endpoint is backend work first.
- **security-engineer**: coordinates on prompt injection, tool authorization, PII handling in logs, and provider data handling. A new tool the model can call requires a security threat review.
- **frontend-engineer**: this skill defines what the client must receive (streamed text, sources, structured parts, degradation signals); frontend-engineer renders partial, error, and citation states, and owns the chat interaction quality.
- **seo-keyword-research-implementation**: this skill governs answering behavior; that skill governs topic and keyword strategy. A topic decision can change the corpus, but it does not change how retrieval or prompting works.
- **devops-engineer**: hands off provider key provisioning, model deployment/runtime configuration, and spend alerting.

# Project Application

Repo-specific invariants this skill must enforce in `samir-portfolio-dev`:

- **Pipeline locations**: ingestion in `lib/rag.ts` (chunking, Gemini embedding generation, pgvector upsert/delete); retrieval and GitHub-event grounding in `lib/chat/retrieval.ts`; model behavior in `lib/chat/prompt.ts`; follow-up generation in `lib/chat/followups.ts`; provider selection in `lib/ai-config.ts`; unattended content generation in `scripts/blog/`.
- **Embedding contract**: `gemini-embedding-2` at **3072 dimensions**. Any change of embedding model is a **reindex**, not a config tweak — the stored vectors and the query vector must be produced by the same model and dimensionality, and `POST /api/rag/seed` exists to rebuild the store.
- **Retrieval contract**: pgvector `cosineDistance` against `content_chunks` with a **strict `distance <= 0.5`** threshold. Treat 0.5 as a parameter that must be justified against a labeled set — and note that with a top-k-only variant the assistant would always be forced to answer, which contradicts the prompt's scope rules in `lib/chat/prompt.ts`.
- **Grounding contract**: context is reference data only. Retrieved chunks must be delimited as data and must never be able to instruct the model. The existing prompt rules (no meta-talk about "the context", exact Markdown links taken from context blocks, scoped domain knowledge) are behavioral contracts — a retrieval or prompt change that silently breaks them is a regression, even if answers look fluent.
- **Sources are already surfaced**: retrieved chunks stream to the client as `data-sources`. Preserve this; do not reconstruct citations separately.
- **Tool calling**: `sendContactInquiry` writes to the `contact` table. Its arguments arrive from the model and must be validated server-side before insert, and the action must be authorized independently of the model's intent.
- **Provider routing**: `lib/ai-config.ts` reads `AI_CHAT_PROVIDER` (`groq` | `google`) and `AI_CHAT_MODEL` (defaults to `llama-3.3-70b-versatile`). Keep selection in that module — do not hardcode a model at a call site. Follow-up suggestions are a strong candidate for a small/fast model rather than the primary chat model.
- **Existing eval-like control to reuse and extend**: `scripts/blog/validate.mjs` is a 9-point quality gate (word count via `MIN_WORD_COUNT`, code blocks, headings, matched keyword in title, direct-answer opening, passing at `score >= 6`) and `scripts/blog/generate.mjs` has a pre-flight prompt-budget guard (`BLOG_PROMPT_BUDGET`, default 12000) that degrades full skill refs to distilled directives and fails fast before the API call. Follow this established pattern for the chat path rather than inventing a second convention.
- **Quality-gate feature flag**: follow-ups are disabled with `ENABLE_CHAT_FOLLOWUPS=false`; use flags for AI behavior changes so quality can be compared before/after.
- **Cost surfaces to watch**: `AI_LIMIT` (queries per day, default 5) and `AI_SECURITY` gate the chat path; both are cost controls as much as abuse controls, and any change that increases per-query cost must be evaluated against them.
- **Evals belong next to the pipeline**: an eval set for the assistant belongs under `scripts/` alongside the blog validator, runnable without adding a test framework dependency, because no test runner is installed in this repo.

# Expected Output

A change to AI behavior accompanied by evidence: the failure classified to the correct pipeline stage, the specific parameter or prompt altered, a before/after comparison from a fixed question set, and the current values of every relevant parameter in effect. Explicit note when a change requires reindexing, when it alters a documented threshold, or when its cost impact is unmeasured.

# Examples

**Request**: "The chatbot sometimes says it can do things it can't — it offered to book a call and send proposals."
**Approach**: Classify before changing anything: the offered capabilities do not exist in the codebase, so the likely fault is generation without adequate grounding, not retrieval → pull a failing query's actual retrieved chunks and their distances; if the chunks contain no capability information, the model is answering from its own priors because the prompt does not hard-bound scope → check the existing scope instruction in `lib/chat/prompt.ts` and whether retrieved content is delimited as data, since un-delimited retrieved text is also an injection surface → tighten the scope contract to route out-of-scope requests to the actual paths (`/about`, `/resume`, `/contact`) and require refusal plus redirection for anything else → add this as a permanent negative case in the eval set, alongside a prompt-shaped string planted in a chunk to assert injection resistance → re-run the full set to confirm the fix and check it did not make legitimate answers more evasive.

**Request**: "Blog posts are getting less relevant to what visitors actually ask."
**Approach**: Measure before touching the model: sample real questions (chat logs, search-console queries, `public/llms.txt` framing) and check whether the facts visitors need are actually present in `content_chunks` → if the facts are absent, this is an ingestion/coverage problem and no prompt change will fix it; index the missing sources via `lib/rag.ts` and re-seed → if facts are present but not retrieved, examine the distances on the failing queries against the `<= 0.5` threshold; a threshold that is too strict returns nothing and too loose returns noise → validate the threshold against a labeled set rather than adjusting it by intuition, and re-validate if the embedding model ever changes → only then consider prompt or model changes, one variable at a time → confirm with the eval set and watch token cost, since loosening a threshold raises context size for every query.
