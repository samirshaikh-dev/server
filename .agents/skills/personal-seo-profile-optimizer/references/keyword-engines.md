# Keyword Engines

Contents:
1. Role engine
2. Stack engine
3. Combination rules
4. Classification taxonomy
5. Quality evaluation
6. Long-tail construction

---

## 1. Role engine

Given a target role, generate in five layers. The layers matter because recruiters search titles, ATS filters match skills, and humans read concepts.

**Layer 1 — Title variants.** Every reasonable spelling and seniority framing people actually search:
`Frontend Developer`, `Front-End Developer`, `Front End Engineer`, `React Developer`, `UI Engineer`, `JavaScript Developer`

**Layer 2 — Core technical skills** the role assumes:
`React`, `JavaScript`, `TypeScript`, `HTML`, `CSS`, `REST API`, `Git`

**Layer 3 — Ecosystem and tooling:**
`Next.js`, `Redux`, `React Router`, `Tailwind CSS`, `Vite`, `Jest`

**Layer 4 — Engineering concepts** — the vocabulary that signals depth, and the layer most people omit from their profiles:
`Component Architecture`, `State Management`, `API Integration`, `Responsive Design`, `Web Performance`, `Accessibility`, `Design Systems`

**Layer 5 — Natural search phrases:**
`React frontend developer`, `TypeScript React developer`, `frontend developer specializing in React`, `React developer with REST API experience`

Generate only what the person's evidence supports. Anything the role demands but they haven't demonstrated goes to the `LEARN FIRST` bucket — it's genuinely useful information ("here's your gap"), just not a profile edit.

Apply the same five layers to any role: AI Engineer, Backend Developer, DevOps Engineer, Data Engineer, Full Stack Developer, Automation Engineer. The layers are stable; the contents change.

---

## 2. Stack engine

Each technology expands into its own cluster. Example for `React, Node.js, PostgreSQL, Python, n8n`:

| Given | Expands to |
| --- | --- |
| React | React Developer, React.js, React Hooks, React Router, Component Architecture, JSX |
| Node.js | Node.js Developer, Express.js, REST API, Backend Development, npm |
| PostgreSQL | PostgreSQL, SQL, Relational Database, Database Design, Query Optimization |
| Python | Python Developer, FastAPI, Flask, Scripting, Data Processing |
| n8n | n8n, Workflow Automation, API Automation, No-Code Automation, Integration Workflows |

Expand only into things plausibly implied by the stated technology, and verify against their actual work where possible. Someone who says "Node.js" probably knows Express; they may not know NestJS. When unsure, ask or leave it out.

---

## 3. Combination rules

Combinations are high-value because they're what people actually search — `React Node.js developer` gets typed far more than either alone in a hiring context.

Combine when the pairing is a real-world stack:

- `React + Node.js` — common full stack pairing
- `Node.js + PostgreSQL` — standard backend pairing
- `Python + FastAPI` — framework belongs to language
- `n8n + API Automation` — tool plus its discipline
- `React + TypeScript` — near-universal pairing

Don't combine to inflate the list. `PostgreSQL + Tailwind CSS` describes no job anyone is hiring for. A combination earns its place only if someone would plausibly search it or put it in a posting.

---

## 4. Classification taxonomy

Every keyword in the report gets exactly one category:

| Category | Meaning |
| --- | --- |
| Primary | Main target keyword — usually the role plus the defining technology |
| Secondary | Closely related, supporting the primary |
| Technical | A technology, tool, or framework |
| Role | A job title or professional role |
| Skill | A capability |
| Semantic | Contextually related term that builds topical relevance |
| Long-tail | Multi-word search phrase |
| Industry | Domain-specific terminology (fintech, healthtech, e-commerce) |
| Entity | Company, product, technology, or person as a named entity |

There are usually only one to three primary keywords. If a report has fifteen "primary" keywords, the positioning hasn't been decided yet — fix that first.

---

## 5. Quality evaluation

Assess each important keyword on: relevance to the person, search intent it serves, specificity, professional value, role relevance, stack relevance. Add search volume, competition, and difficulty only when a data source supplied them.

Express relevance qualitatively: `High relevance`, `Medium relevance`, `Low relevance`.

Avoid numeric scores and "best keyword" rankings unless the person explicitly asks for a scoring method — and if they do, state the methodology openly so they can judge it. Invented precision leads people to optimize for a number rather than for fit.

---

## 6. Long-tail construction

Long-tail phrases carry less competition and far more intent. Build them by combining any two or three of: role, technology, specialization, industry, outcome, location.

Patterns that work:

- `[Role] + [Technology]` → `Backend developer Node.js`
- `[Role] + specializing in + [Area]` → `Frontend developer specializing in design systems`
- `[Technology] + [Technology] + developer` → `React PostgreSQL developer`
- `[Role] + for + [Industry]` → `Automation engineer for e-commerce`
- `[Role] + [Location]` → `Freelance React developer Surat` (relevant for local or freelance positioning)
- `[Outcome] + with + [Technology]` → `Workflow automation with n8n`

Keep them speakable. If the phrase can't appear in a sentence in an About section without sounding mechanical, it belongs in the research appendix rather than the recommended copy.
