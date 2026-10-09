"""Confere o seed local contra data/manifest.json. Não imprime senha nem hash.

Uso: python scripts/verify_seed.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from envfile import carregar
from seed_local import ENV, MANIFESTO, MASSA, SENTINELA, conectar, cpf_massa


def main() -> int:
    env = carregar(ENV)
    manifesto = json.loads(MANIFESTO.read_text(encoding="utf-8"))
    problemas: list[str] = []
    with conectar(env, manifesto["banco"]) as c, c.cursor() as cur:
        cur.execute("SELECT usu_senha, usu_visivel FROM tb_usuarios WHERE REPLACE(REPLACE(usu_cpf,'.',''),'-','')=%s", (SENTINELA,))
        admin = cur.fetchone()
        esperado = hashlib.sha256(env["QA_ADMIN_SENHA"].encode("utf-8")).hexdigest()
        if not admin or admin[0] != esperado or admin[1] != 1:
            problemas.append("MD-01: admin principal ausente, inativo ou com senha diferente do .env")
        for pessoa in MASSA:
            cur.execute(
                "SELECT u.usu_nome, p.perfil_descricao, u.usu_visivel FROM tb_usuarios u JOIN tb_perfis p USING (perfil_id) WHERE u.usu_cpf=%s",
                (cpf_massa(pessoa["indice"]),),
            )
            linha = cur.fetchone()
            if linha != (pessoa["nome"], pessoa["perfil"], pessoa["visivel"]):
                problemas.append(f"{pessoa['md']}: esperado {pessoa['nome']}/{pessoa['perfil']}/{pessoa['visivel']}, obtido {linha}")
        cur.execute("SELECT perfil_descricao FROM tb_perfis ORDER BY perfil_id")
        perfis = [r[0] for r in cur.fetchall()]
    print("Perfis:", ", ".join(perfis))
    if problemas:
        print("Divergências no seed:\n- " + "\n- ".join(problemas))
        return 1
    print(f"Seed conferido em {manifesto['banco']}: MD-01 a MD-05 conforme o manifesto.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
