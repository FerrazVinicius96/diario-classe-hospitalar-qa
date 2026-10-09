#!/usr/bin/env python
"""Bloqueia ações fora das regras do QA antes da ferramenta rodar.

Entrada: JSON do PreToolUse no stdin.
Saída: código 2 e permissionDecision=deny quando a ação é proibida.
O que é específico do projeto (repositório da aplicação, hosts de HML e de produção)
vem de qa_projeto.json, na raiz do repositório do QA.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
VEREDITO = re.compile(r"\b(aprovados?|reprovados?|bloqueados?)\b", re.I)
COLUNA_VEREDITO = re.compile(
    r"(^|[,\t;])\s*(resultado|severidade|natureza)\s*($|[,\t;])",
    re.I | re.M,
)
HML_ENV = re.compile(r"\bQA_ENV\s*=\s*['\"]?hml\b", re.I)
URL = re.compile(r"https?://([^/\s'\"?#]+)", re.I)
FERRAMENTAS_DE_ESCRITA = {"write", "edit", "multiedit", "notebookedit"}


def configuracao() -> dict:
    caminho = RAIZ / "qa_projeto.json"
    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _lista(config: dict, chave: str) -> set[str]:
    return {str(item).strip().lower() for item in config.get(chave) or [] if str(item).strip()}


def avaliar(evento: dict, config: dict | None = None) -> tuple[bool, str]:
    config = configuracao() if config is None else config
    ferramenta = str(evento.get("tool_name") or evento.get("tool") or "")
    entrada = evento.get("tool_input") or evento.get("tool_input_preview") or {}
    if not isinstance(entrada, dict):
        entrada = {"valor": entrada}
    cwd = str(evento.get("cwd") or "")
    textos = list(_textos(entrada))
    caminhos = _caminhos(entrada)
    comando = "\n".join(
        str(entrada.get(chave) or "")
        for chave in ("command", "cmd", "script")
    )
    escrita = ferramenta.lower() in FERRAMENTAS_DE_ESCRITA
    protegidas = _pastas_somente_leitura(config)
    producao = _lista(config, "hosts_producao")

    for caminho in caminhos:
        if _e_env(caminho):
            return True, "Leitura ou escrita de .env negada. Segredos ficam fora do agente."
        if not escrita:
            continue
        for pasta in protegidas:
            if pasta in _normalizar(caminho):
                return True, f"A pasta {pasta} é somente leitura."
        if _e_original_protegido(caminho):
            return True, "docs/ e os originais .docx/.xlsx não podem ser editados."

    if any(_git_proibido(comando, cwd, pasta) for pasta in protegidas):
        return True, "git commit, push e pull estão bloqueados no repositório da aplicação."

    if ferramenta.lower() in {"bash", "powershell", "shell"} and _pede_hml(comando):
        if os.environ.get("QA_ALLOW_HML") != "1":
            return True, "QA_ENV=hml sem QA_ALLOW_HML=1 definido na sessão."

    host_negado = _host_fora_da_lista(comando, config)
    if host_negado:
        return True, f"URL fora da lista permitida ({host_negado}). Produção não entra na lista."

    for caminho in caminhos:
        if _e_saida(caminho):
            bloco = "\n".join(textos)
            if VEREDITO.search(bloco) or COLUNA_VEREDITO.search(bloco):
                return True, (
                    "Arquivo de saída não pode levar veredito nem as colunas "
                    "Resultado, Severidade ou Natureza."
                )

    texto_total = ("\n".join(textos) + "\n" + comando).lower()
    for host in producao:
        if host in texto_total:
            return True, f"Host de produção bloqueado ({host})."

    return False, ""


def main() -> int:
    bruto = sys.stdin.buffer.read().decode("utf-8-sig", errors="replace")
    if not bruto.strip():
        return 0
    try:
        evento = json.loads(bruto)
    except json.JSONDecodeError:
        return 0
    if not isinstance(evento, dict):
        return 0

    bloqueado, motivo = avaliar(evento)
    if not bloqueado:
        sys.stdout.write(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "allow",
                    }
                }
            )
        )
        return 0

    sys.stderr.write(motivo + "\n")
    sys.stdout.write(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": motivo,
                }
            },
            ensure_ascii=False,
        )
    )
    return 2


def _textos(valor):
    if isinstance(valor, str):
        yield valor
    elif isinstance(valor, dict):
        for item in valor.values():
            yield from _textos(item)
    elif isinstance(valor, list):
        for item in valor:
            yield from _textos(item)


def _caminhos(entrada: dict) -> list[str]:
    chaves = (
        "file_path",
        "path",
        "target_file",
        "notebook_path",
        "target_notebook",
    )
    achados = []
    for chave in chaves:
        valor = entrada.get(chave)
        if isinstance(valor, str) and valor.strip():
            achados.append(valor)
    return achados


def _normalizar(caminho: str) -> str:
    return caminho.replace("\\", "/").lower()


def _pastas_somente_leitura(config: dict) -> list[str]:
    """Nomes das pastas protegidas: o repositório da aplicação e as de pastas_somente_leitura."""
    valores = [config.get("repo_aplicacao") or ""] + list(config.get("pastas_somente_leitura") or [])
    nomes = {Path(str(v).strip().replace("\\", "/")).name.lower() for v in valores if str(v).strip()}
    return sorted(nomes)


def _e_env(caminho: str) -> bool:
    nome = Path(caminho).name.lower()
    if nome == ".env.example":
        return False
    return nome == ".env" or nome.startswith(".env.")


def _e_original_protegido(caminho: str) -> bool:
    normal = _normalizar(caminho)
    if "/docs/" in f"/{normal}" or normal.startswith("docs/"):
        return True
    if normal.endswith(".docx"):
        return True
    if normal.endswith(".xlsx") and "/data/massa/" not in f"/{normal}":
        return True
    return False


def _e_saida(caminho: str) -> bool:
    normal = _normalizar(caminho)
    if "/results/" in f"/{normal}" or normal.startswith("results/"):
        return True
    if "/reports/" in f"/{normal}" or normal.startswith("reports/"):
        return True
    return normal.endswith(".csv") and not _e_original_protegido(caminho)


def _git_proibido(comando: str, cwd: str, repo_app: str) -> bool:
    if not re.search(r"\bgit(\.exe)?\b", comando, re.I):
        return False
    if not re.search(r"\b(commit|push|pull)\b", comando, re.I):
        return False
    contexto = f"{comando} {cwd}".replace("\\", "/").lower()
    return repo_app in contexto


def _pede_hml(comando: str) -> bool:
    if HML_ENV.search(comando):
        return True
    return os.environ.get("QA_ENV", "").lower() == "hml"


def _host_fora_da_lista(comando: str, config: dict) -> str:
    permitidos = _lista(config, "hosts_locais") or {"localhost", "127.0.0.1", "::1"}
    producao = _lista(config, "hosts_producao")
    if os.environ.get("QA_ALLOW_HML") == "1":
        permitidos |= _lista(config, "hosts_hml")
        extras = os.environ.get("QA_HML_ALLOWED_HOSTS", "")
        permitidos.update(parte.strip().lower() for parte in extras.split(",") if parte.strip())

    for host in URL.findall(comando):
        limpo = host.lower().split("@")[-1].split(":")[0]
        if limpo in producao or limpo not in permitidos:
            return limpo
    return ""


if __name__ == "__main__":
    raise SystemExit(main())
