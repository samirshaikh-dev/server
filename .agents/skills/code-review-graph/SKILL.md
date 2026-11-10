---
name: code-review-graph
description: Use to query codebase dependencies, analyze architecture impact, inspect execution flows, detect change blast radius, and maintain the SQLite knowledge graph (.code-review-graph/graph.db) via CLI or MCP.
---

# Code Review Graph — Codebase Intelligence Skill

Use this skill whenever you need structural intelligence about the repository without broad, expensive context-window file scans.

## Core Capabilities

1. **Dependency Analysis**: Identifies upstream and downstream callers, imports, component usages, and cross-module relationships.
2. **Blast Radius / Impact Detection**: Assesses which components, pages, routes, or utilities are affected when a specific file or symbol changes.
3. **Execution Flow Tracing**: Maps execution flows across server actions, route handlers, service layers, and UI components.
4. **Dead Code & Risk Detection**: Surfaces unreferenced functions, components, or circular dependencies.

---

## Operating Protocol for Agents

### 1. Before Making Changes (Context & Impact Mapping)
- Query or inspect the existing codebase graph (`.code-review-graph/graph.db`).
- Check graph status and health:
  ```bash
  python -m code_review_graph status
  ```
- Understand the relevant architecture, imports, and execution flows before touching code.
- Identify all dependent components and callers before modifying shared utilities, hooks, or primitives.
- Avoid unnecessary repository-wide globbing or grepping when the graph already indexes symbol references.

### 2. While Making Changes (Surgical Edits)
- Follow existing architecture and conventions without introducing unneeded abstractions.
- Avoid modifying shared APIs without verifying that all dependents can accept the change.
- Respect component boundaries (e.g., Client Components vs. Server Components).

### 3. After Making Changes (Verification & Synchronization)
- Analyze the change impact and potential regressions:
  ```bash
  python -m code_review_graph detect-changes --brief
  ```
- Re-index and update the graph so subsequent agent turns and peer subagents see the latest state:
  ```bash
  python -m code_review_graph update
  ```

---

## Direct CLI Commands Reference

| Command | Purpose |
| :--- | :--- |
| `python -m code_review_graph status` | Shows total nodes, edges, indexed files, and graph statistics. |
| `python -m code_review_graph update` | Incrementally re-parses changed files and updates SQLite indexes. |
| `python -m code_review_graph detect-changes --brief` | Analyzes blast radius and risk summary for recent edits. |
| `python -m code_review_graph dead-code` | Identifies potentially unused functions and components. |
| `python -m code_review_graph build` | Complete re-build of the codebase knowledge graph. |
| `python -m code_review_graph visualize` | Generates interactive HTML graph visualization for debugging. |

