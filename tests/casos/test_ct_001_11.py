from apoio import abrir_login, entrar_admin, finalizar, resumo_hash


def _sessao(page) -> str | None:
    return next((c["value"] for c in page.context.cookies() if c["name"] == "dch_session"), None)


def test_ct_001_11(page, registro):
    abrir_login(page)
    antes = _sessao(page)
    entrar_admin(page)
    depois = _sessao(page)
    registro.passo(acao="comparar cookie dch_session (só resumo, sem o valor)",
                   antes=resumo_hash(antes), depois=resumo_hash(depois), mudou=antes != depois)
    registro.conferir(depois is not None and antes != depois, "Identificador de sessão igual antes e depois do login")
    registro.observar("Cobre o reteste do DEF-DCH-016 (Ricardo): combinar antes de registrar.")
    finalizar(registro)
