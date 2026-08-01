---
name: learn
description: Extract an executed multi-step procedure or user correction into a reusable SKILL.md under skills/<skill-name>/SKILL.md (Hermes Agent closed-loop learning pattern).
---

# Closed-Loop Skill Extraction (/learn)

Use this skill whenever a complex multi-step task, pipeline, or troubleshooting workflow has been successfully completed, or when the user provides a direct correction/instruction on how to do a task.

## Steps

1. **Analyze the Workflow**:
   - Identify the goal, exact bash commands, Python scripts, parameters, and edge-case handling.

2. **Check Existing Skills**:
   - Inspect `/home/tan/.nanobot/workspace/skills/` to check if a relevant skill already exists.
   - If it exists, update/merge the new procedure into the existing `SKILL.md`.
   - If not, create a new directory: `/home/tan/.nanobot/workspace/skills/<skill-name>/`.

3. **Format the `SKILL.md`**:
   ```markdown
   ---
   name: <skill-name>
   description: <one sentence summary of when and why to use>
   ---

   # <Skill Title>

   ## Usage & Command Examples
   ```bash
   <concrete command line>
   ```

   ## Operational Rules & Edge Cases
   - <rule 1>
   - <rule 2>
   ```

4. **Verify & Index**:
   - Verify syntax and run `python3 /home/tan/.nanobot/workspace/nanobot_self_improve.py auto` if needed.
