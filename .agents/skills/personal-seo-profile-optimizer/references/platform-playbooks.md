# Platform Playbooks

Contents:
1. LinkedIn
2. GitHub
3. Personal website / portfolio
4. Technical SEO checklist
5. Resume / CV
6. Project descriptions

---

## 1. LinkedIn

LinkedIn is usually the highest-leverage fix because recruiter search runs heavily on headline and skills, and changes take minutes.

### Headline

Structure:

```
[Target Role] | [Primary Tech] · [Secondary Tech] | [Specialization or value]
```

Examples:

```
Frontend Developer | React · TypeScript | Building accessible, performant web apps
Backend Engineer | Node.js · PostgreSQL | REST APIs and system design
Automation Engineer | n8n · Python | Workflow automation for operations teams
```

Rules worth following:

- Lead with the role title, because that's the field recruiters search first.
- Two to four technologies, not eight. A wall of tools reads as inexperience.
- End with a specialization or an outcome, not "passionate about technology" — that phrase carries zero search value and appears on millions of profiles.
- Keep it under roughly 220 characters so it doesn't truncate in search results.

Always offer 2–3 variations with different emphasis (role-forward, tech-forward, outcome-forward). Fit is personal.

### About section

Aim for a short opening line stating role and specialization, a paragraph on what they build and with what, a paragraph on notable projects or domains, and a closing line on what they're looking for.

Place keywords where they read naturally: role terms in the opening line, technologies inside sentences about actual work, engineering concepts in the projects paragraph. If a keyword can't sit in a real sentence, it doesn't go in.

Anti-pattern to flag if you see it:

```
React | Node | Python | AWS | Docker | Kubernetes | MongoDB | GraphQL | Redis | ...
```

### Experience

Weave technologies into responsibility statements rather than listing them at the end. `Built a PostgreSQL-backed reporting API in Node.js serving 40k daily requests` carries the same keywords as a tech list plus evidence of scale.

### Skills

Recommend only skills their history supports, ordered so the top three — the ones LinkedIn surfaces most prominently — match the target role.

---

## 2. GitHub

GitHub profiles surface in Google results for a person's name, and recruiters read repo descriptions before code.

### Bio

One line: role, core technologies, current focus.

```
Backend engineer · Node.js, PostgreSQL · building API automation tools
```

### Repository names

Descriptive over clever. `invoice-parser-api` tells a visitor and a search engine what it is; `project-2` and `zenith` do not. Never recommend a name that misrepresents what the code does.

### Repository descriptions

One sentence: what it does, what it's built with.

```
REST API for parsing and categorizing PDF invoices. Node.js, Express, PostgreSQL, Tesseract OCR.
```

### Topics

Five to eight relevant topic tags per repo — GitHub topic pages are browsable and indexed.

### README

Recommend structure: H1 with the project name and what it is, a one-paragraph summary, the problem it solves, tech stack, features, setup, and a screenshot or demo link. Headings should contain real terminology, since they become anchor links and appear in search snippets.

### Profile README

Worth having: role, stack, selected projects with one-line descriptions, contact. It's the first thing on the profile and indexes well.

---

## 3. Personal website / portfolio

### Homepage

- **Title tag** — `[Name] — [Role] | [Primary Tech]`, under ~60 characters
- **Meta description** — 140–155 characters, includes role and main technologies, reads as a sentence
- **H1** — one per page, containing the primary role keyword
- **Intro copy** — states role, technologies, and specialization within the first two sentences

### Project pages

Each significant project deserves its own indexable page, since project pages rank for specific technology combinations that a homepage never will. For each:

- SEO title and H1 containing the project type plus technology
- The problem it solved
- Technical implementation and architecture decisions
- Technology list
- Results or outcome where there is one
- Links to live demo and repo

### Internal linking

Link homepage → projects → related projects, using descriptive anchor text (`the n8n order-sync automation`, not `click here`).

---

## 4. Technical SEO checklist

Check what's observable and recommend what isn't:

- `sitemap.xml` present and submitted to Search Console
- `robots.txt` present, not blocking anything important
- Canonical URLs set
- Open Graph and Twitter card tags (controls how links look when shared — this is where most portfolio links get seen)
- Structured data: `Person` schema on the homepage, `CreativeWork` or `SoftwareApplication` on project pages
- Unique title and meta description per page
- Page speed — especially images and unnecessary JavaScript
- Mobile responsiveness
- Descriptive image alt text
- HTTPS
- Clean, readable URL slugs
- No orphan pages

For SPA portfolios, flag whether project pages are actually server-rendered or pre-rendered. Client-only rendering with no static HTML is a common and invisible reason portfolio projects never appear in search.

---

## 5. Resume / CV

ATS keyword matching is closer to literal string matching than to semantic search, so exact terminology from the target postings matters more here than anywhere else.

- Use the exact technology spellings from postings (`Node.js` and `JavaScript`, not `node` and `JS`)
- Include the target job title near the top if it's an honest description
- Put technologies inside bullet points describing real work, not only in a skills block
- Avoid tables, columns, text boxes, and images for anything load-bearing — many parsers drop them
- Standard section headings: Experience, Education, Skills, Projects

---

## 6. Project descriptions

The same project usually needs three lengths, and it's worth writing all three so they can reuse them:

- **One line** (GitHub description, portfolio card): what it does, built with what
- **Short paragraph** (LinkedIn projects, resume): problem, approach, technologies, outcome
- **Full page** (portfolio project page): context, problem, architecture, decisions and tradeoffs, results

Keywords appear naturally in all three when the description explains the actual problem and stack — which is why describing the work well and optimizing for search mostly turn out to be the same task.
