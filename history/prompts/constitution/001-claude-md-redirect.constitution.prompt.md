---
id: "001"
title: "CLAUDE.md Redirect"
stage: "constitution"
date: "2026-01-04"
surface: "agent"
model: "claude-opus-4-5-20251101"
feature: "none"
branch: "003-ai-chatbot"
user: "apple"
command: "Update CLAUDE.md to redirect to AGENTS.md"
labels: ["configuration","spec-driven-development","redirect"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - "/Users/apple/Data/Certified-Cloud-Applied-Generative-AI-Engineering/Q4-Agentic-AI/ai_driven_development/Hackathons/02-evolution-of-todo/CLAUDE.md"
tests: []
---

## Prompt

```
Connect Claude Code via the "Shim"
Copy the default CLAUDE.md file and integrate the content within AGENTS.md . Claude Code automatically looks for CLAUDE.md. To keep a single source of truth, use a redirection pattern.
Create CLAUDE.md in your root:
\`\`\`markdown
@AGENTS.md
\`\`\`

This "forwarding" ensures Claude Code loads your comprehensive agent instructions into its context window immediately upon startup.
```

## Response snapshot

```
I've successfully updated the CLAUDE.md file to contain only a reference to the AGENTS.md file. This creates the redirection pattern as requested, where CLAUDE.md now points to AGENTS.md, ensuring that Claude Code will load the comprehensive agent instructions from AGENTS.md into its context window immediately upon startup.
```

## Outcome

- ✅ Impact: CLAUDE.md now redirects to AGENTS.md maintaining single source of truth
- 🧪 Tests: No tests needed for this configuration change
- 📁 Files: Modified CLAUDE.md to contain only "@AGENTS.md"
- 🔁 Next prompts: User can now continue with their workflow
- 🧠 Reflection: Successfully implemented the redirection pattern as requested

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Not applicable
- Prompt variant (if applicable): Not applicable
- Next experiment (smallest change to try): Not applicable
