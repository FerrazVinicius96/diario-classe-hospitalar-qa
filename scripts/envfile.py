"""Lê e atualiza .env sem escrever os valores em log."""

from pathlib import Path


def carregar(caminho: Path) -> dict[str, str]:
    if not caminho.exists():
        return {}
    dados: dict[str, str] = {}
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        texto = linha.strip()
        if not texto or texto.startswith("#") or "=" not in texto:
            continue
        chave, _, valor = texto.partition("=")
        dados[chave.strip()] = valor.strip()
    return dados


def atualizar(caminho: Path, novos: dict[str, str]) -> None:
    linhas = caminho.read_text(encoding="utf-8").splitlines() if caminho.exists() else []
    vistas: set[str] = set()
    saida: list[str] = []
    for linha in linhas:
        texto = linha.strip()
        if not texto or texto.startswith("#") or "=" not in linha:
            saida.append(linha)
            continue
        chave, _, _valor = linha.partition("=")
        chave = chave.strip()
        if chave in novos:
            saida.append(f"{chave}={novos[chave]}")
            vistas.add(chave)
        else:
            saida.append(linha)
    for chave, valor in novos.items():
        if chave not in vistas:
            saida.append(f"{chave}={valor}")
    caminho.write_text("\n".join(saida) + "\n", encoding="utf-8")
