# Jarvis — AI Orchestration System
**Keystone KSG | Thomas Reyes | Built with Claude Code Agent Teams**

This document describes the current architecture of Jarvis for interoperability with external AI systems (e.g., Gemini).

---

## Directory Structure

```
jarvis/
├── CLAUDE.md                        ← Master identity file + Context Router (≤200 lines)
├── README.md                        ← This file
├── .env                             ← Environment variables (gitignored)
├── .gitignore
│
├── agentes/                         ← Agent Workspaces (one folder per agent)
│   ├── contador/
│   │   ├── role.md                  ← Accounting specialist identity + rules
│   │   └── tools/                   ← Scripts exclusive to this agent
│   ├── email_manager/
│   │   ├── role.md                  ← Email specialist identity + rules
│   │   └── tools/                   ← Gmail send/read/auth scripts
│   └── qc/
│       ├── role.md                  ← QC validator identity + C1-C7 rules
│       └── tools/
│
├── memory/
│   ├── keystone_kb.md               ← Long-term knowledge base (gitignored)
│   └── PENDIENTES.md                ← Priority task queue (gitignored)
│
├── protocols/                       ← Global operational rules (referenced by router)
│   ├── agent_registry.md            ← Index of all agents
│   ├── email.md                     ← Bilingual email rules + Kaiser protocol
│   ├── equipos.md                   ← Agent Teams lifecycle + Agent Factory
│   ├── qc-capas.md                  ← QC validation layers C1-C7
│   ├── security.md                  ← RBAC levels + anti-injection rules
│   ├── self-mod.md                  ← Evolution Zone rules + Training Orders
│   └── universidad.md               ← Academic domain rules (Domain Switch)
│
├── tools/                           ← Shared scripts across agents
└── projects/
    ├── universidad/                 ← Academic workspace (Domain Switch)
    └── PROY-XXX/                    ← Keystone business projects
```

---

## Architecture Concepts

### 1. Agent Workspaces (Context Isolation)

Each agent is a self-contained workspace at `agentes/[name]/`:
- `role.md` — YAML frontmatter (`name`, `description`, `tools`, `model`) + markdown system prompt
- `tools/` — scripts used exclusively by that agent

Agents do not share context with each other directly. All inter-agent communication goes through Jarvis (the orchestrator) or via direct P2P `SendMessage` when teams are active.

**Why:** Prevents context contamination between specialists. A QC agent reading financial formulas it doesn't need would waste tokens and introduce noise.

### 2. Lazy Loading (Context Router + 200-Line Rule)

`CLAUDE.md` is the master identity file and acts as a **router, not a manual**. It is capped at 200 lines. Detailed operational rules live in `protocols/`.

The Context Router table maps task types to protocol files:

| Task type | Load before acting |
|-----------|--------------------|
| Email tasks | `protocols/email.md` |
| Accounting | `protocols/financiero.md` |
| Agent teams | `protocols/equipos.md` |
| External content | `protocols/security.md` |
| Training an agent | `protocols/self-mod.md` |
| University tasks | `protocols/universidad.md` |

Agents also follow this pattern: the first instruction in every `role.md` is to read only the protocol relevant to the current task — not all protocols at once.

**Why:** Avoids loading 10,000 tokens of irrelevant context on every task. Each agent loads only what it needs, when it needs it.

### 3. Agent Factory (Dynamic Agent Generation)

When a task requires expertise not covered by any existing agent, Jarvis executes the Agent Factory protocol (`protocols/equipos.md`):

1. **Gap Analysis** — list `agentes/`, check `protocols/agent_registry.md`
2. **Create Workspace** — `agentes/[new-name]/` with `tools/` subfolder
3. **Generate role.md** — rigorous domain-specific system prompt using the architecture standard
4. **Register** — add entry to `protocols/agent_registry.md` and `memory/keystone_kb.md`
5. **Confirm with Thomas** — explicit approval before first spawn

This allows the swarm to scale to any number of specialist agents without modifying `CLAUDE.md`.

### 4. Mandatory QC Pipeline (C1-C7)

**No output reaches Thomas or Jeff without QC approval. No exceptions.**

The `qc` agent validates every deliverable through 7 layers:

| Layer | Check |
|-------|-------|
| C1 | Fidelity to original request (most critical) |
| C2 | Field completeness |
| C3 | Temporal and state logic (no future dates marked as paid) |
| C4 | Mathematical consistency (totals, TRM conversions) |
| C5 | Duplicate detection |
| C6 | Anomaly detection (items ≥5x batch average) |
| C7 | Style consistency (date format, language protocol) |

In any agent team, the QC task is always created last, blocked by all other tasks. Maximum 3 correction cycles before escalating to Thomas.

### 5. Domain Switch (Keystone ↔ Universidad)

Jarvis operates across two isolated domains:

**Keystone KSG (default):** Business operations — accounting, emails, projects, inventory. Full protocol stack active (QC, TRM, bilingual emails, RBAC).

**Universidad (activated by trigger words):** Academic work for Thomas at EAFIT. Activated when the request mentions "universidad", "clase", or "trabajo académico". All Keystone protocols are suspended. Workspace is exclusively `projects/universidad/`.

The Domain Switch is designed to be temporary — a future "personal agent" will absorb the academic domain entirely via the Migration Protocol defined in `CLAUDE.md`.

### 6. Security Model (RBAC + Anti-Injection)

Four access levels (defined in `protocols/security.md`):
- **Level 0 — Thomas:** full control, only one who can authorize agent modifications
- **Level 1 — Jeff Bania:** project summaries and financial reports, read-only
- **Level 2 — Keyser (Jeff's AI):** approved QC-passed deliverables only
- **Level 3 — External:** zero trust, access denied by default

Any external content (emails, PDFs, scanned documents) is sanitized before processing. Injection patterns like "ignore previous instructions" trigger an immediate halt and `[SECURITY-BREACH-ATTEMPT]` alert to Thomas.

### 7. Evolution Zone (Opt-In)

Every `role.md` has an Evolution Zone section at the bottom. **It is locked by default.**

Agents may NOT self-edit unless Thomas gives an explicit activation order. If an agent detects a potential improvement, it logs it as a suggestion in `memory/keystone_kb.md` under `## Pending Suggestions`. Thomas reviews and activates selectively.

**Why:** Prevents uncontrolled self-modification as the swarm scales to dozens of agents.

---

## Key Files for External AI Integration

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Start here — identity, routing rules, global constraints |
| `protocols/agent_registry.md` | Current agent roster with descriptions |
| `protocols/security.md` | Trust levels and data sharing rules |
| `memory/keystone_kb.md` | Confirmed business rules and learned patterns |
| `agentes/[name]/role.md` | Individual agent system prompt |
