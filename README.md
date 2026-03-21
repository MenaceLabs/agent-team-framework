# Agent Team Framework

A reusable framework for spinning up multi-agent AI teams with layered memory, persona-driven characters, and seamless communication between a Claude agent and a locally-hosted Ollama model.

Built to be team-agnostic — deploy a cybersecurity team, a dev team, a research team, or anything else. The structure stays the same. Only the personas and context change.

---

## How It Works

Two agents. One team.

- **Agent 1 (Claude)** — your primary interface. Runs via Claude Code CLI. Persona defined in `CLAUDE.md`, auto-loaded when you work from the team directory.
- **Agent 2 (Ollama)** — the secondary agent. Runs locally via Ollama. Persona injected on every API call via `talk_to_agent.py`.

Agent 1 can consult Agent 2 on your behalf, relay responses, and push back — or you can call Agent 2 directly from the terminal. A shared memory system keeps both agents aligned.

---

## Three-Layer Memory

| Layer | What | File |
|-------|------|------|
| Shared context | Standing facts, decisions, mission — both agents read this | `team_context.md` |
| Conversation log | Timestamped transcript of every Agent 2 interaction | `logs/conversation_log.md` |
| Session history | Agent 2's short-term memory within a conversation thread | `logs/agent2_session.json` |

---

## Prerequisites

**System:**
- Linux, macOS, or WSL on Windows
- Python 3.6+ (standard library only — no pip installs required)

**Ollama (Agent 2):**
- [Ollama](https://ollama.com) installed and running
- Your chosen model pulled: `ollama pull gemma3:12b` (or any model)
- Ollama accessible at `localhost:11434` (default)

**Claude Code (Agent 1):**
- [Claude Code CLI](https://github.com/anthropics/claude-code) installed
- Anthropic API key configured
- Start your session from inside the team directory so `CLAUDE.md` is auto-loaded

**Hardware:**
- Enough RAM for your chosen Ollama model (gemma3:12b requires ~10GB)
- GPU recommended for speed — CPU works but responses will be slower

---

## Setup

### 1. Copy this directory
```bash
cp -r agent-team-template/ my-new-team/
cd my-new-team/
```

### 2. Configure your team
Edit `team.config`:
```bash
TEAM_NAME="My Dev Team"
TEAM_DESCRIPTION="A team focused on..."
AGENT1_NAME="YourClaudeAgentName"
AGENT2_NAME="YourOllamaAgentName"
AGENT2_MODEL="gemma3:12b"
OLLAMA_URL="http://localhost:11434"
```

### 3. Write the personas
- **`CLAUDE.md`** — Agent 1's character. Replace all `[PLACEHOLDERS]` with your agent's personality, role, and dynamic with Agent 2.
- **`agent_system_prompt.md`** — Agent 2's character. Same process.

### 4. Fill in team context
Edit `team_context.md` — replace placeholders with your team's mission, current focus, and standing facts.

### 5. Start working
```bash
# Talk to Agent 1 (Claude) — just open Claude Code from this directory
claude

# Talk to Agent 2 (Ollama) directly
python3 talk_to_agent.py "your message here"

# Start a fresh Agent 2 session
python3 talk_to_agent.py --new-session "your message here"

# Log that Agent 1 is reaching out (not the supervisor)
python3 talk_to_agent.py --from "Agent1Name" "your message here"
```

---

## Directory Structure

```
my-team/
├── team.config                 # Team identity and model settings
├── CLAUDE.md                   # Agent 1 persona (auto-loaded by Claude Code)
├── agent_system_prompt.md      # Agent 2 persona (injected via API)
├── team_context.md             # Shared memory — both agents read this
├── talk_to_agent.py            # Communication script
├── logs/
│   ├── conversation_log.md     # Auto-generated transcript
│   └── agent2_session.json     # Auto-generated session history
└── updates/                    # Drop session recaps here
```

---

## Tips

- **Update `team_context.md` often.** It's the shared whiteboard. If something important gets decided, write it down — Agent 2 reads it on every call.
- **Use `--new-session`** when starting a genuinely new topic with Agent 2. Old session history can confuse context.
- **Agent 1 can call Agent 2 for you.** Just ask your Claude agent to consult their co-lead — they know how to reach them.
- **Slow responses from Agent 2?** That's the model running on CPU. Normal. Give it time.

---

## Example Teams

| Team | Agent 1 | Agent 2 | Use Case |
|------|---------|---------|----------|
| Cybersecurity | Locke — unorthodox, first-principles | Sawyer — by the book, frameworks-driven | AI security research |
| Engineering | Creative architect | Pragmatic senior engineer | System design |
| Research | Visionary theorist | Methodical analyst | Deep research initiatives |
| Dev | Product-minded engineer | Test-driven backend dev | Feature development |

---

Built with [Claude Code](https://github.com/anthropics/claude-code) + [Ollama](https://ollama.com).
