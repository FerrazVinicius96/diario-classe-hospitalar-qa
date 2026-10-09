import os

from apoio import app_url, entrar, esperar_url, finalizar, texto_limpo


def test_ct_001_04(page, registro):
    entrar(page, os.environ.get("QA_ADMIN_CPF", "00000000000"), "QA-senha-errada-1")
    titulo = texto_limpo(page.locator("h1").inner_text())
    mensagem = texto_limpo(page.locator(".auth-text").inner_text())
    registro.passo(acao="login com senha errada (1 tentativa)", url_final=page.url, titulo=titulo, mensagem=mensagem)
    registro.evidencia(page)
    registro.conferir("/welcome/credenciaisInvalidas" in page.url, f"URL final {page.url}")
    registro.conferir(titulo == "Credenciais inválidas.", f"Título {titulo!r}")
    registro.conferir(mensagem == "CPF ou senha incorretos. Verifique os dados e tente novamente.", f"Mensagem {mensagem!r}")

    page.goto(f"{app_url()}/dashboard")
    voltou = esperar_url(page, r"/welcome")
    registro.passo(acao="abrir /dashboard depois da falha", url_final=page.url)
    registro.conferir(voltou, f"Sessão criada após senha errada: /dashboard abriu ({page.url})")
    finalizar(registro)
