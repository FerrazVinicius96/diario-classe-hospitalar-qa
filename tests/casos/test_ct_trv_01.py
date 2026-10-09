from apoio import app_url, esperar_url, finalizar


def test_ct_trv_01(page, registro):
    resposta = page.goto(f"{app_url()}/")
    chegou = esperar_url(page, r"/welcome")
    page.wait_for_load_state("networkidle")
    registro.passo(acao="abrir /", status_http=resposta.status if resposta else None, url_final=page.url, titulo=page.title())
    registro.evidencia(page)
    registro.conferir(resposta is not None and resposta.status == 200, f"HTTP {resposta.status if resposta else 'sem resposta'} ao abrir /")
    registro.conferir(chegou, f"Não chegou à tela de login (URL final {page.url})")
    registro.conferir("Diário de Classe Hospitalar" in page.title(), f"Título inesperado: {page.title()!r}")
    registro.conferir(page.locator("#login").count() == 1 and page.locator("#password").count() == 1,
                      "Formulário sem os campos CPF e Senha")
    finalizar(registro)
