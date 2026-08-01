---
name: code-review-graph
description: >
  Structural code graph (Tree-sitter → SQLite) via MCP for blast-radius review,
  impact analysis, and targeted search. Use when reviewing changes, debugging
  call chains, finding dead code, or exploring architecture without dumping the
  whole repo into context. Triggers: code review, blast radius, impact, callers,
  graph, CRG, refactor safely.
---

# code-review-graph (nanobot)

Upstream: https://github.com/tirth8205/code-review-graph

MCP server name in nanobot: **`code-review-graph`**  
Default repo: `C:\Users\tantt\.nanobot\workspace`  
CLI: `code-review-graph` (pip package `code-review-graph`)

## When to use

Prefer graph MCP tools **before** broad `grep`/`find_files` on multi-file code tasks:

- "What calls X?" / blast radius of a change
- Safe refactor / dead code
- Review diff impact + missing tests
- Architecture / flow overview

Not needed for pure markdown/wiki prose or one-file greets.

## Workflow

1. If graph empty or stale after big edits:  
   `code-review-graph update --repo C:\Users\tantt\.nanobot\workspace`  
   (full rebuild: `build`)
2. Query via MCP (tools vary by version; typical names):  
   `search` / `query_graph` / `impact` / `detect_changes` / flows / communities
3. Read **only** the files the graph returns — then edit.
4. After substantial code changes: `update` again (or rely on next session build).

## CLI cheatsheet (shell)

```text
code-review-graph status --repo <path>
code-review-graph build  --repo <path>
code-review-graph update --repo <path>
code-review-graph impact --repo <path> <target>
code-review-graph search --repo <path> <query>
code-review-graph dead-code --repo <path>
```

## Nanobot constraints

- Graph indexes **git-tracked** source files. New `.py` must be `git add`ed (or tracked) or it stays invisible.
- Workspace `.gitignore` uses `/*` with allowlists — keep `!*.py` and `!skills/` so code stays indexable.
- Default MCP `--repo` is the nanobot workspace. For another project:  
  run CLI with `--repo <that/path>` or temporarily change config MCP args + restart gateway.
- Companion skills (from upstream, under `skills/crg-*`):  
  `crg-build-graph`, `crg-review-changes`, `crg-explore-codebase`, `crg-refactor-safely`, `crg-debug-issue`.

## Ponytail note

Graph is the lazy path: fewer tokens than dumping the tree. Still climb the ladder — graph query first, then minimal reads.
