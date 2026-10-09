#!/usr/bin/env python
"""Adapta o guard do QA para os hooks do Cursor."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".claude" / "hooks"))

import guard  # noqa: E402


def normalizar(evento: dict) -> dict:
    if evento.get("tool_name") or evento.get("tool_input"):
        evento.setdefault("tool_name", "Bash")
        return evento
    if "command" in evento:
        return {
            "tool_name": "Bash",
            "tool_input": {"command": evento.get("command") or ""},
            "cwd": evento.get("cwd") or "",
        }
    if evento.get("file_path") or evento.get("path"):
        return {
            "tool_name": "Read",
            "tool_input": evento,
            "cwd": evento.get("cwd") or "",
        }
    return evento


def main() -> int:
    bruto = sys.stdin.read()
    if not bruto.strip():
        sys.stdout.write(json.dumps({"permission": "allow"}))
        return 0
    try:
        evento = json.loads(bruto)
    except json.JSONDecodeError:
        sys.stdout.write(json.dumps({"permission": "allow"}))
        return 0
    if not isinstance(evento, dict):
        sys.stdout.write(json.dumps({"permission": "allow"}))
        return 0

    bloqueado, motivo = guard.avaliar(normalizar(evento))
    if bloqueado:
        sys.stdout.write(
            json.dumps(
                {
                    "permission": "deny",
                    "user_message": motivo,
                    "agent_message": motivo,
                },
                ensure_ascii=False,
            )
        )
        return 0
    sys.stdout.write(json.dumps({"permission": "allow"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
