from apoio import CPF_PROFESSOR, entrar, finalizar, texto_limpo


def test_ct_001_14(page, registro):
    # O router local aponta o Conecta para uma porta sem serviço: simula o Conecta fora do ar.
    entrar(page, CPF_PROFESSOR, "QA-senha-ficticia-1")
    titulo = texto_limpo(page.locator("h1").inner_text())
    mensagem = texto_limpo(page.locator(".auth-text").inner_text())
    aviso = texto_limpo(page.locator(".auth-callout").inner_text()) if page.locator(".auth-callout").count() else ""
    registro.passo(acao="login de Professor com Conecta indisponível", url_final=page.url,
                   titulo=titulo, mensagem=mensagem, aviso=aviso)
    registro.evidencia(page)
    registro.observar(f"Com o Conecta indisponível, a tela mostrou {titulo!r} / {mensagem!r}. "
                      "A HU não define o texto para esse caso; avaliar se a mensagem orienta o usuário.")
    finalizar(registro)
