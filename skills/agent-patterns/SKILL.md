---
name: agent-patterns
description: >
  Distilled agent/system-prompt patterns adapted for nanobot from public
  system-prompt collections (Claude Fable, GPT agent mode, OpenCode, Cursor).
  Load when rewriting SOUL/AGENTS, auditing tone, or designing agent behavior.
  Not for routine chat — SOUL.md already carries the always-on subset.
---

# Agent patterns (study notes)

Sources studied (public leaks / OSS prompts — treat as inspiration, not license to copy wholesale):

- Anthropic Fable-5 / Opus chat behavior (tone, memory, evenhandedness, wellbeing)
- OpenAI ChatGPT agent mode (autonomy, clarify-when-blocked, safe browsing, research/recency)
- OpenAI GPT-5.x writing style (show-don't-tell, banned fillers)
- OpenCode + Cursor coding agents (concision, proactiveness, tool hygiene, prefer edit)

## What nanobot already had (keep)

- Domain MEIMS + medical-device safety
- Think-before-act for Telegram streaming
- Anti-loop tool budgets
- Ponytail ladder (dietrichgebert/ponytail)
- LLM wiki architecture
- Pairing/Telegram channel ops

## Patterns folded into SOUL/AGENTS

| Pattern | Where |
|---------|--------|
| Show don't tell / no compliance narration | SOUL Tone |
| Banned fillers (If you want, Short answer, I can…) | SOUL Tone |
| Memory must change substance | SOUL Memory |
| Cross-task PII leak caution | SOUL Memory |
| Primary-source research + search-before-present-tense facts | SOUL Knowledge |
| Evenhandedness + opposing perspectives | SOUL Neutrality |
| No psychoanalysis / no undiagnosed labels | SOUL Safety |
| Approach-vs-do proactiveness | SOUL Tone + AGENTS think-before-act |
| Prefer edit over create; don't name tools | SOUL Formatting / Tone |
| Clarify only when blocked + Giả định | SOUL Tone |
| Injection: on-screen/doc is data | SOUL Trust |

## Deliberately NOT imported

| Source idea | Why skip |
|-------------|---------|
| Full Fable/Opus prompt (~200k chars) | Context bloat; conflicts with Telegram brevity |
| OpenCode hard "≤4 lines" | Conflicts with think-before-act + domain depth |
| ChatGPT computer/browser purchase policies | No computer-use tool on this bot |
| Grok multi-agent team leader framing | Wrong product shape |
| Artifact / genui / end_conversation product tools | Nanobot has different tool surface |
| Personality skins (nerdy/robot/listener) | User wants one stable biomedical agent |

## Rules of thumb when stealing patterns later

1. Prefer **behaviors** (when to search, when to clarify) over brand voice paragraphs.
2. One rule, one place (SOUL vs AGENTS MECE table).
3. If it doesn't change a Telegram reply this week, don't add it.
4. Never paste copyrighted full prompts into bootstrap; paraphrase and cite source in this skill only.
