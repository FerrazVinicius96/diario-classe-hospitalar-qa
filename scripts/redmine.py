"""Consulta issues do Redmine e registra notas pela API REST.

Lê REDMINE_URL e REDMINE_API_KEY do .env; a chave nunca é impressa.
Escrita (nota e status) só com --confirmar: sem ele, mostra o que seria enviado.
Recusar uma HU é decisão do QA; o agente não passa --confirmar.

Uso:
  python scripts/redmine.py testar
  python scripts/redmine.py status
  python scripts/redmine.py ver 14496
  python scripts/redmine.py comentar 14496 --arquivo reports/redmine_14496.md [--status "Teste Recusado"]
         [--anexo results/evidencias/CT-004-12_X_....png ...] [--confirmar]
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import re
import urllib.parse
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cpf as cpf_util  # noqa: E402
import envfile  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
CPF_ABERTO = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")


class ErroRedmine(Exception):
    pass


def configuracao() -> tuple[str, str]:
    env = envfile.carregar(RAIZ / ".env")
    url = env.get("REDMINE_URL", "").rstrip("/")
    chave = env.get("REDMINE_API_KEY", "")
    if not url or not chave:
        raise ErroRedmine("Defina REDMINE_URL e REDMINE_API_KEY no .env.")
    if not url.startswith("https://"):
        print("Aviso: REDMINE_URL não usa https; a chave trafega sem criptografia.", file=sys.stderr)
    return url, chave


def chamar(metodo: str, caminho: str, corpo: dict | None = None, binario: bytes | None = None) -> dict:
    url, chave = configuracao()
    if binario is not None:
        dados, tipo = binario, "application/octet-stream"
    else:
        dados, tipo = (json.dumps(corpo).encode("utf-8") if corpo is not None else None), "application/json"
    pedido = urllib.request.Request(
        f"{url}{caminho}",
        data=dados,
        method=metodo,
        headers={"X-Redmine-API-Key": chave, "Content-Type": tipo},
    )
    try:
        with urllib.request.urlopen(pedido, timeout=30) as resposta:
            texto = resposta.read().decode("utf-8")
    except urllib.error.HTTPError as erro:
        motivos = {
            401: "chave inválida ou API REST desativada no Redmine",
            403: "sem permissão para esta ação",
            404: "issue ou recurso não encontrado",
            422: "dados recusados pelo Redmine",
        }
        detalhe = erro.read().decode("utf-8", "replace")[:300] if erro.code == 422 else ""
        raise ErroRedmine(f"HTTP {erro.code}: {motivos.get(erro.code, erro.reason)} {detalhe}".strip()) from None
    except urllib.error.URLError as erro:
        raise ErroRedmine(f"Sem conexão com o Redmine ({erro.reason}). VPN conectada?") from None
    return json.loads(texto) if texto.strip() else {}


def cpfs_sem_mascara(texto: str) -> list[str]:
    return [achado for achado in CPF_ABERTO.findall(texto) if cpf_util.valido(achado)]


def cmd_testar(_args) -> None:
    usuario = chamar("GET", "/users/current.json")["user"]
    print(f"Conectado como: {usuario.get('firstname', '')} {usuario.get('lastname', '')} ({usuario.get('login', '')})")


def cmd_status(_args) -> None:
    for item in chamar("GET", "/issue_statuses.json")["issue_statuses"]:
        fechado = " (fecha a issue)" if item.get("is_closed") else ""
        print(f"{item['id']:>4}  {item['name']}{fechado}")


def cmd_ver(args) -> None:
    issue = chamar("GET", f"/issues/{args.id}.json?include=journals,allowed_statuses,attachments")["issue"]
    nome = lambda campo: (issue.get(campo) or {}).get("name", "-")  # noqa: E731
    print(f"#{issue['id']} {issue['subject']}")
    print(f"Projeto: {nome('project')} | Tipo: {nome('tracker')} | Status: {nome('status')}")
    print(f"Atribuída a: {nome('assigned_to')} | Atualizada em: {issue.get('updated_on', '-')}")
    permitidos = [item["name"] for item in issue.get("allowed_statuses", [])]
    if permitidos:
        print("Status que você pode aplicar: " + ", ".join(permitidos))
    for anexo in issue.get("attachments", []):
        print(f"Anexo: {anexo['filename']} ({anexo.get('filesize', 0) // 1024 + 1} KB, {anexo.get('created_on', '')})")
    notas = [j for j in issue.get("journals", []) if j.get("notes")]
    for jornal in notas[-3:]:
        autor = (jornal.get("user") or {}).get("name", "-")
        print(f"\n[{jornal.get('created_on', '')}] {autor}:\n{jornal['notes'][:500]}")


def cmd_comentar(args) -> None:
    texto = Path(args.arquivo).read_text(encoding="utf-8").strip()
    if not texto:
        raise ErroRedmine("Arquivo de nota vazio.")
    abertos = cpfs_sem_mascara(texto)
    if abertos:
        raise ErroRedmine(f"A nota tem {len(abertos)} CPF sem máscara. Mascare antes de enviar.")

    corpo: dict = {"issue": {"notes": texto}}
    if args.status:
        issue = chamar("GET", f"/issues/{args.id}.json?include=allowed_statuses")["issue"]
        candidatos = {item["name"].lower(): item for item in issue.get("allowed_statuses", [])}
        escolhido = candidatos.get(args.status.lower())
        if not escolhido:
            opcoes = ", ".join(item["name"] for item in candidatos.values()) or "nenhum"
            raise ErroRedmine(f"Status '{args.status}' não permitido nesta issue. Opções: {opcoes}")
        corpo["issue"]["status_id"] = escolhido["id"]

    anexos = [Path(caminho) for caminho in args.anexo or []]
    for anexo in anexos:
        if not anexo.is_file():
            raise ErroRedmine(f"Anexo não encontrado: {anexo}")
        if anexo.suffix.lower() in {".txt", ".json", ".csv", ".md", ".log"}:
            if cpfs_sem_mascara(anexo.read_text(encoding="utf-8", errors="replace")):
                raise ErroRedmine(f"O anexo {anexo.name} tem CPF sem máscara.")

    print(f"Issue #{args.id}" + (f" -> status '{args.status}'" if args.status else ""))
    print("-" * 60)
    print(texto)
    print("-" * 60)
    for anexo in anexos:
        print(f"Anexo: {anexo.name} ({anexo.stat().st_size // 1024 + 1} KB)")
    if not args.confirmar:
        print("Prévia apenas. Para enviar, repita o comando com --confirmar.")
        return
    if anexos:
        corpo["issue"]["uploads"] = []
        for anexo in anexos:
            nome = urllib.parse.quote(anexo.name)
            token = chamar("POST", f"/uploads.json?filename={nome}", binario=anexo.read_bytes())["upload"]["token"]
            tipo = mimetypes.guess_type(anexo.name)[0] or "application/octet-stream"
            corpo["issue"]["uploads"].append({"token": token, "filename": anexo.name, "content_type": tipo})
    chamar("PUT", f"/issues/{args.id}.json", corpo)
    print("Enviado.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="comando", required=True)
    sub.add_parser("testar", help="confere URL e chave").set_defaults(func=cmd_testar)
    sub.add_parser("status", help="lista os status do Redmine").set_defaults(func=cmd_status)
    ver = sub.add_parser("ver", help="mostra uma issue")
    ver.add_argument("id", type=int)
    ver.set_defaults(func=cmd_ver)
    comentar = sub.add_parser("comentar", help="adiciona nota e, opcionalmente, muda o status")
    comentar.add_argument("id", type=int)
    comentar.add_argument("--arquivo", required=True)
    comentar.add_argument("--status")
    comentar.add_argument("--anexo", nargs="+", help="evidências a anexar (prints mascarados)")
    comentar.add_argument("--confirmar", action="store_true")
    comentar.set_defaults(func=cmd_comentar)

    args = parser.parse_args()
    try:
        args.func(args)
    except ErroRedmine as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
