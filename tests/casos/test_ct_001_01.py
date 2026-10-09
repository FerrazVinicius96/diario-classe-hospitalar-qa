from apoio import abrir_login, finalizar, texto_limpo


def test_ct_001_01(page, registro):
    abrir_login(page)
    botao = texto_limpo(page.locator("button[type=submit]").inner_text())
    aviso = texto_limpo(page.locator(".auth-note").inner_text()) if page.locator(".auth-note").count() else ""
    registro.passo(acao="abrir tela de login", url_final=page.url, botao=botao, aviso=aviso)
    registro.evidencia(page)
    registro.conferir(botao == "Entrar com Conecta Recife", f"Botão com texto {botao!r}")
    registro.conferir("acesso é restrito a profissionais autorizados" in aviso,
                      f"Aviso de acesso restrito ausente ou diferente: {aviso!r}")
    registro.observar("Decisão aceita: CPF e senha na própria tela (ROPC), em vez de redirect ao Conecta (HU-001 crit. 2).")
    finalizar(registro)
