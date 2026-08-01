---
name: graphify
description: Knowledge Graph extraction & traversal for codebase, markdown documentation, medical wiki entities, and SQL schemas via Graphify Labs. Use when exploring entity relationships, blast-radius code impact, wiki entity links, or architecture visualization without dumping large context into prompt. Triggers: graphify, knowledge graph, entity links, code graph, blast radius, architecture graph.
---

# Skill: graphify (Nanobot & Medical Wiki Knowledge Graph)

Upstream: https://github.com/Graphify-Labs/graphify (`graphifyy` package)

## Overview

Graphify parses Python code, Markdown docs, SQL schemas, and Medical Equipment Wiki entities into a queryable local Knowledge Graph (AST-driven, zero API cost).

## Usage

### 1. Build / Update Graph
Run from shell:
```bash
graphify build --repo /home/tan/.nanobot/workspace
# or update incremental changes
graphify update --repo /home/tan/.nanobot/workspace
```

### 2. Querying Knowledge Graph
- Explore code & wiki entity relationships:
  `graphify search "Nihon Kohden ECG-3350K"`
- Blast-radius / Impact analysis:
  `graphify impact "nanobot_self_improve.py"`
- Interactive Graph Visualization:
  `graphify export --format html`

## Workflow Integration
- Prioritize `graphify` traversal before broad `grep` or dumping full `wiki/` folders.
- After creating new Wiki Entities or major code refactors, run `graphify update`.
