"""Resumo do dia e rascunho da planilha a partir de results/CT-*.json.

Não escreve veredito, severidade nem natureza. A coluna Sugestão é rotulada como sugestão.
Uso: python scripts/relatorio.py [AAAA-MM-DD]
"""

from __future__ import annotations

import csv
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
RESULTADOS = RAIZ / os.environ.get("QA_RESULTS_DIR", "results")
RELATORIOS = RAIZ / "reports"
PRIORIDADES = ("Alta", "Média", "Baixa")
PROJETO = json.loads((RAIZ / "qa_projeto.json").read_text(encoding="utf-8")).get("projeto", "QA")


def carregar() -> list[dict]:
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(RESULTADOS.glob("CT-*.json"))]


def epico(r: dict) -> str:
    return (r.get("epico") or "Transversal").split(" - ")[0]


def situacao(r: dict) -> str:
    if r["situacao_execucao"] == "impedido":
        return "impedimento"
    if r["pytest"] == "failed" and not r["divergencias"]:
        return "erro de script"
    return "diverge" if r["divergencias"] else "confere"


def observado(r: dict) -> str:
    partes = []
    if r["divergencias"]:
        partes.append("Divergências: " + " | ".join(r["divergencias"]))
    if r["impedimentos"]:
        partes.append("Impedimento: " + " | ".join(r["impedimentos"]))
    if r["observacoes"]:
        partes.append("Observações: " + " | ".join(r["observacoes"]))
    if not partes:
        ultimo = r["passos"][-1] if r["passos"] else {}
        partes.append("Conferência automática sem divergência. Último passo: " + ", ".join(f"{k}={v}" for k, v in ultimo.items())[:300])
    if r.get("erro_tecnico") and not r["divergencias"]:
        partes.append("Erro técnico: " + r["erro_tecnico"].strip()[:300])
    return " ".join(partes)


def sugestao(r: dict) -> str:
    estado = situacao(r)
    if estado == "impedimento":
        return "Sugestão: tratar como impedimento (condição de execução ausente); confirmar motivo e anexar a evidência."
    if estado == "erro de script":
        return "Sugestão: refazer manualmente; a automação falhou antes de concluir a conferência."
    if estado == "diverge":
        return "Sugestão: candidato a defeito ou a observação; revisar as divergências e a evidência antes de decidir."
    return "Sugestão: conferência automática sem divergência; revisar a evidência antes de decidir."


def main() -> int:
    dia = sys.argv[1] if len(sys.argv) > 1 else date.today().isoformat()
    resultados = carregar()
    if not resultados:
        sys.stderr.write("Nenhum resultado em results/.\n")
        return 1
    RELATORIOS.mkdir(exist_ok=True)

    with (RELATORIOS / "rascunho_planilha.csv").open("w", encoding="utf-8-sig", newline="") as arquivo:
        escritor = csv.writer(arquivo, delimiter=";")
        escritor.writerow(["ID", "Observado", "Evidência", "Sugestão"])
        for r in resultados:
            escritor.writerow([r["id"], observado(r), " ; ".join(r["evidencias"]), sugestao(r)])

    por_prioridade = defaultdict(Counter)
    por_epico = defaultdict(Counter)
    for r in resultados:
        por_prioridade[r.get("prioridade") or "—"][situacao(r)] += 1
        por_epico[epico(r)][situacao(r)] += 1
    colunas = ("confere", "diverge", "impedimento", "erro de script")

    def tabela(titulo, grupos, ordem):
        linhas = [f"| {titulo} | Executados | " + " | ".join(c.capitalize() for c in colunas) + " |", "|" + " --- |" * (len(colunas) + 2)]
        for chave in ordem:
            if chave in grupos:
                contagem = grupos[chave]
                linhas.append(f"| {chave} | {sum(contagem.values())} | " + " | ".join(str(contagem.get(c, 0)) for c in colunas) + " |")
        return "\n".join(linhas)

    texto = [
        f"# Resumo de execução — {PROJETO} — {dia}",
        "",
        f"Ambiente: {resultados[0].get('ambiente')} ({resultados[0].get('base_url')}). Casos executados: {len(resultados)}.",
        "",
        "Conferência automática compara o observado com o resultado esperado da planilha. Não é veredito: veredito, severidade e natureza são decisão do QA.",
        "",
        "## Por prioridade",
        "",
        tabela("Prioridade", por_prioridade, PRIORIDADES),
        "",
        "## Por épico",
        "",
        tabela("Épico", por_epico, sorted(por_epico)),
        "",
        "## Candidatos a defeito (divergências)",
        "",
    ]
    for r in resultados:
        if situacao(r) == "diverge":
            evidencia = r["evidencias"][0] if r["evidencias"] else "—"
            texto.append(f"- **{r['id']}** ({r.get('prioridade')}) {r.get('cenario')}: " + " | ".join(r["divergencias"])[:600] + f" — evidência `{evidencia}`")
    texto += ["", "## Impedimentos", ""]
    for r in resultados:
        if situacao(r) == "impedimento":
            texto.append(f"- **{r['id']}** ({r.get('prioridade')}) {r.get('cenario')}: " + " | ".join(r["impedimentos"]))
    erros = [r for r in resultados if situacao(r) == "erro de script"]
    if erros:
        texto += ["", "## Erros de automação (refazer à mão)", ""]
        texto += [f"- **{r['id']}**: {r.get('erro_tecnico', '').strip()[:300]}" for r in erros]
    texto += ["", "## Observações registradas", ""]
    for r in resultados:
        for obs in r["observacoes"]:
            texto.append(f"- {r['id']}: {obs}")
    (RELATORIOS / f"resumo_{dia}.md").write_text("\n".join(texto) + "\n", encoding="utf-8")
    sys.stdout.write(f"reports/resumo_{dia}.md e reports/rascunho_planilha.csv gerados ({len(resultados)} casos).\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
