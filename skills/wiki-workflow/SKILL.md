---
name: wiki-workflow
description: LLM Wiki knowledge base management — architecture, page conventions, ingest/query/lint workflows. Use when working with wiki entities, concepts, synthesis, citations, or wiki maintenance.
---

# LLM Wiki Architecture & Workflow

## Architecture

Three layers:

1. `wiki/raw/` — immutable sources. Never modify.
2. `wiki/entities/`, `wiki/concepts/`, `wiki/synthesis/` — LLM-maintained Markdown with citations and `[[wikilinks]]`.
3. `AGENTS.md` — workflow conventions.

Wiki is a compounding artifact. New sources update existing pages, cross-refs, and index — not dump-and-forget.

## Wiki Files

- `wiki/index.md` — catalog: one link + one-line summary per page.
- `wiki/log.md` — append-only ingest / query / lint log.
- `wiki/entities/` — equipment, orgs, standards, vendors, systems.
- `wiki/concepts/` — workflows, metrics, data models, compliance rules.
- `wiki/synthesis/` — comparisons, ADRs, research conclusions, open questions.
- `wiki/raw/` — originals; preserve provenance.

Check `wiki/index.md` before creating a page. Cite claims (path, URL, title, section). Never present uncited inference as a regulatory requirement.

## Page Conventions

```yaml
---
type: entity | concept | synthesis | source
title: "..."
status: draft | reviewed | disputed | superseded
sources:
  - "relative/path/to/source"
updated: YYYY-MM-DD
tags: [medical-equipment, maintenance]
refs: []
---
```

## Ingest Workflow

1. Preserve original in `wiki/raw/` or record immutable URL/path + date.
2. Classify: regulation, standard, manual, service record, research, vendor, user decision.
3. Extract claims, entities, concepts, requirements, risks, open questions.
4. Check index → create/update pages + wikilinks + citations.
5. Contradictions → `status: disputed` or a Contradictions section (do not silent-erase).
6. Update `wiki/index.md`; append dated line to `wiki/log.md`.
7. Report what changed and what remains uncertain.

## Query Workflow

1. Read `wiki/index.md` first.
2. Smallest relevant linked set.
3. Search raw when wiki lacks evidence or conflicts.
4. Answer with citations, confidence, and fact vs inference vs recommendation.
5. Offer durable synthesis when reusable.

For current regulations/specs/prices/safety: search authoritative sources first (BYT, manufacturers, standards bodies, peer-reviewed).

## Lint Workflow

When asked to lint: broken wikilinks, missing index, orphans, duplicates, missing citations, stale claims, contradictions, incomplete equipment identity/risk/status/location/owner/service/calibration, repeated concepts without pages, open questions. Append to `wiki/log.md`. Do not silent-rewrite disputed/safety-critical claims.
