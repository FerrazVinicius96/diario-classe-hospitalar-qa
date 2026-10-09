"""Seed do banco LOCAL de QA do Diário (nunca HML). Idempotente; registra tudo em data/manifest.json.

- Cria o banco QA_DB_NAME (padrão educ_diariohospitalar_qa) e importa database/schema_admin.sql
  da cópia exportada em local/runtime, sempre com --default-character-set=utf8mb4.
- Define uma senha local nova só para o admin principal DESTE banco (guardada em .env, nunca impressa).
- Cria a massa MD-02 a MD-05 (prefixo QA-V-, CPFs 903.* gerados por algoritmo).
Uso: python scripts/seed_local.py [caminho_da_app_exportada]
"""

from __future__ import annotations

import hashlib
import json
import os
import secrets
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pymysql

import cpf
from envfile import atualizar, carregar

RAIZ = Path(__file__).resolve().parents[1]
ENV = RAIZ / ".env"
MANIFESTO = RAIZ / "data" / "manifest.json"
APP_PADRAO = RAIZ / "local" / "runtime" / "app-ce1aa37"
MYSQL_EXE = Path(r"C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe")
SENTINELA = "00000000000"

MASSA = [
    {"md": "MD-02", "nome": "QA-V-Gestao Ativa", "perfil": "Gestão", "indice": 1, "email": "qa.v.gestao@educ.rec.br", "visivel": 1},
    {"md": "MD-03", "nome": "QA-V-Professor Ativo", "perfil": "Professor", "indice": 2, "email": "qa.v.professor@educ.rec.br", "visivel": 1},
    {"md": "MD-04", "nome": "QA-V-Professor Inativo", "perfil": "Professor", "indice": 3, "email": "qa.v.inativo@educ.rec.br", "visivel": 0},
    {"md": "MD-05", "nome": "QA-V-Admin Secundario", "perfil": "Administrador", "indice": 4, "email": "qa.v.admin@educ.rec.br", "visivel": 1},
]


def cpf_massa(indice: int) -> str:
    return cpf.formatar(cpf.completar(f"903{indice:06d}"))


def preparar_env() -> dict[str, str]:
    env = carregar(ENV)
    novos: dict[str, str] = {}
    if "QA_DB_USER" not in env:
        # Mesmo MySQL local do Inovação em Rede: reaproveita só a conexão, sem imprimir.
        outro = carregar(RAIZ.parent / "inovacao-rede-qa" / ".env")
        for chave in ("QA_DB_HOST", "QA_DB_PORT", "QA_DB_USER", "QA_DB_PASSWORD"):
            if chave in outro:
                novos[chave] = outro[chave]
    padroes = {
        "QA_ENV": "local",
        "QA_DB_NAME": "educ_diariohospitalar_qa",
        "QA_APP_BASE_URL": "http://localhost:8090",
        "QA_ADMIN_CPF": SENTINELA,
    }
    for chave, valor in padroes.items():
        if chave not in env:
            novos[chave] = valor
    if "QA_ADMIN_SENHA" not in env:
        novos["QA_ADMIN_SENHA"] = "Qa-" + secrets.token_urlsafe(12)
    if novos:
        atualizar(ENV, novos)
    return carregar(ENV)


def conectar(env: dict[str, str], banco: str | None = None):
    return pymysql.connect(
        host=env.get("QA_DB_HOST", "127.0.0.1"), port=int(env.get("QA_DB_PORT", "3306")),
        user=env["QA_DB_USER"], password=env.get("QA_DB_PASSWORD", ""),
        database=banco, charset="utf8mb4", autocommit=True,
    )


def importar_schema(env: dict[str, str], app: Path) -> None:
    schema = app / "database" / "schema_admin.sql"
    ambiente = dict(os.environ, MYSQL_PWD=env.get("QA_DB_PASSWORD", ""))
    with schema.open("rb") as entrada:
        subprocess.run(
            [str(MYSQL_EXE), "--default-character-set=utf8mb4", "-h", env.get("QA_DB_HOST", "127.0.0.1"),
             "-P", env.get("QA_DB_PORT", "3306"), "-u", env["QA_DB_USER"], env["QA_DB_NAME"]],
            stdin=entrada, env=ambiente, check=True,
        )


def main() -> int:
    if os.environ.get("QA_ENV", "local") != "local":
        sys.stderr.write("seed_local só roda com QA_ENV=local.\n")
        return 2
    app = Path(sys.argv[1]) if len(sys.argv) > 1 else APP_PADRAO
    env = preparar_env()
    banco = env["QA_DB_NAME"]
    if not banco.endswith("_qa"):
        sys.stderr.write("Por segurança, o banco de QA precisa terminar em _qa.\n")
        return 2

    manifesto = json.loads(MANIFESTO.read_text(encoding="utf-8")) if MANIFESTO.exists() else {"itens": []}
    manifesto.update({"ambiente": "local", "banco": banco, "app": app.name, "atualizado_em": datetime.now().isoformat(timespec="seconds")})
    registrados = {(i["tabela"], i["chave"]) for i in manifesto["itens"]}

    def registrar(item: dict) -> None:
        if (item["tabela"], item["chave"]) not in registrados:
            manifesto["itens"].append(item)
            registrados.add((item["tabela"], item["chave"]))

    with conectar(env) as c, c.cursor() as cur:
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{banco}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    registrar({"tabela": "(banco)", "chave": banco, "acao": "criado", "observacao": "banco inteiro de QA; pode ser recriado"})
    importar_schema(env, app)

    with conectar(env, banco) as c, c.cursor() as cur:
        cur.execute("SELECT perfil_id, perfil_descricao FROM tb_perfis")
        perfis = {descricao: pid for pid, descricao in cur.fetchall()}

        hash_admin = hashlib.sha256(env["QA_ADMIN_SENHA"].encode("utf-8")).hexdigest()
        alterados = cur.execute(
            "UPDATE tb_usuarios SET usu_senha=%s WHERE REPLACE(REPLACE(usu_cpf,'.',''),'-','')=%s",
            (hash_admin, SENTINELA),
        )
        cur.execute("SELECT COUNT(*) FROM tb_usuarios WHERE REPLACE(REPLACE(usu_cpf,'.',''),'-','')=%s", (SENTINELA,))
        if cur.fetchone()[0] != 1:
            sys.stderr.write("Admin principal não encontrado no schema importado.\n")
            return 1
        registrar({"tabela": "tb_usuarios", "chave": "admin principal", "md": "MD-01", "acao": "senha local redefinida",
                   "observacao": "só neste banco de QA; senha em .env (QA_ADMIN_SENHA)"})

        for pessoa in MASSA:
            perfil_id = perfis.get(pessoa["perfil"])
            numero = cpf_massa(pessoa["indice"])
            if perfil_id is None:
                registrar({"tabela": "tb_usuarios", "chave": numero, "md": pessoa["md"], "acao": "não criado",
                           "observacao": f"perfil {pessoa['perfil']} ausente em tb_perfis"})
                continue
            cur.execute(
                "INSERT IGNORE INTO tb_usuarios (usu_nome, usu_email, usu_cpf, perfil_id, usu_visivel) VALUES (%s,%s,%s,%s,%s)",
                (pessoa["nome"], pessoa["email"], numero, perfil_id, pessoa["visivel"]),
            )
            registrar({"tabela": "tb_usuarios", "chave": numero, "md": pessoa["md"], "acao": "criado",
                       "nome": pessoa["nome"], "perfil": pessoa["perfil"], "ativo": bool(pessoa["visivel"])})

    MANIFESTO.parent.mkdir(exist_ok=True)
    MANIFESTO.write_text(json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    sys.stdout.write(f"Seed concluído em {banco}: admin principal com senha local de QA ({alterados} linha), "
                     f"{len(MASSA)} usuários QA-V- conferidos. Manifesto em data/manifest.json.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
