#!/usr/bin/env python3
"""
talk_to_agent.py

Sends a message to the Ollama-based team agent with:
  - Agent system prompt injected
  - Shared team context prepended
  - Multi-turn session history maintained
  - All interactions logged

Usage:
  python3 talk_to_agent.py "your message"
  python3 talk_to_agent.py --new-session "your message"
  python3 talk_to_agent.py --from "Agent1Name" "your message"

Configuration is read from team.config in the same directory.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent.resolve()
CONFIG_FILE = SCRIPT_DIR / "team.config"
SYSTEM_PROMPT_FILE = SCRIPT_DIR / "agent_system_prompt.md"
TEAM_CONTEXT_FILE = SCRIPT_DIR / "team_context.md"
LOGS_DIR = SCRIPT_DIR / "logs"
SESSION_FILE = LOGS_DIR / "agent2_session.json"
CONVO_LOG = LOGS_DIR / "conversation_log.md"


def load_config(config_path: Path) -> dict:
    """Parse key=value pairs from team.config, ignoring comments and blanks."""
    config = {}
    with open(config_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                config[key.strip()] = value.strip().strip('"')
    return config


def load_text(path: Path) -> str:
    return path.read_text() if path.exists() else ""


def load_session(new_session: bool) -> list:
    LOGS_DIR.mkdir(exist_ok=True)
    if new_session or not SESSION_FILE.exists():
        SESSION_FILE.write_text("[]")
    return json.loads(SESSION_FILE.read_text())


def save_session(history: list) -> None:
    SESSION_FILE.write_text(json.dumps(history, indent=2))


def append_log(sender: str, agent2_name: str, user_message: str, reply: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = (
        f"\n---\n"
        f"**[{timestamp}] {sender} → {agent2_name}**\n"
        f"{user_message}\n\n"
        f"**[{timestamp}] {agent2_name}**\n"
        f"{reply}\n"
    )
    with open(CONVO_LOG, "a") as f:
        f.write(entry)


def call_ollama(ollama_url: str, model: str, messages: list) -> str:
    payload = json.dumps({
        "model": model,
        "stream": False,
        "messages": messages
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{ollama_url}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=300) as response:
            data = json.loads(response.read())
            return data.get("message", {}).get("content", "").strip()
    except urllib.error.URLError as e:
        print(f"Error reaching Ollama at {ollama_url}: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Talk to the Ollama-based team agent.")
    parser.add_argument("message", help="Message to send")
    parser.add_argument("--new-session", action="store_true", help="Start a fresh conversation session")
    parser.add_argument("--from", dest="sender", default="User", help="Who is sending the message (for logging)")
    args = parser.parse_args()

    # Load config
    if not CONFIG_FILE.exists():
        print(f"Error: team.config not found at {CONFIG_FILE}", file=sys.stderr)
        sys.exit(1)

    config = load_config(CONFIG_FILE)
    agent2_name = config.get("AGENT2_NAME", "Agent2")
    model = config.get("AGENT2_MODEL", "gemma3:12b")
    ollama_url = config.get("OLLAMA_URL", "http://localhost:11434")

    # Build system prompt
    system_prompt = load_text(SYSTEM_PROMPT_FILE)
    if not system_prompt:
        print(f"Error: agent_system_prompt.md not found at {SYSTEM_PROMPT_FILE}", file=sys.stderr)
        sys.exit(1)

    team_context = load_text(TEAM_CONTEXT_FILE)
    if team_context:
        full_system = f"{system_prompt}\n\n---\n## Shared Team Context\n{team_context}"
    else:
        full_system = system_prompt

    # Load session history
    history = load_session(args.new_session)

    # Append user message to history
    history.append({"role": "user", "content": args.message})

    # Build messages: system + history
    messages = [{"role": "system", "content": full_system}] + history

    # Call Ollama
    print(f"[Reaching {agent2_name}...]", file=sys.stderr)
    reply = call_ollama(ollama_url, model, messages)

    if not reply:
        print(f"Error: No response from {agent2_name}. Is Ollama running?", file=sys.stderr)
        sys.exit(1)

    # Save updated session history
    history.append({"role": "assistant", "content": reply})
    save_session(history)

    # Log the exchange
    append_log(args.sender, agent2_name, args.message, reply)

    # Output reply
    print(reply)


if __name__ == "__main__":
    main()
