from apoio import app_url, csrf_do_login, finalizar, senha_admin


def test_ct_001_06(playwright, registro):
    for formato, cpf in (("só dígitos", "00000000000"), ("com máscara", "000.000.000-00")):
        contexto = playwright.request.new_context(base_url=app_url())
        try:
            token = csrf_do_login(contexto)
            resposta = contexto.post("/welcome/processarLogin", max_redirects=0,
                                     form={"dch_csrf": token, "login": cpf, "password": senha_admin()})
            destino = resposta.headers.get("refresh") or resposta.headers.get("location") or ""
            registro.passo(formato=formato, status_http=resposta.status, redireciona_para=destino)
            registro.conferir("/dashboard" in destino, f"CPF {formato}: não levou ao dashboard (destino {destino!r})")
        finally:
            contexto.dispose()
    finalizar(registro)
