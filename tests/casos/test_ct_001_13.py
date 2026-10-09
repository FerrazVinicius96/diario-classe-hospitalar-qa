from apoio import app_url, entrar_admin, esperar_url, finalizar


def test_ct_001_13(page, registro):
    entrar_admin(page)
    page.goto(f"{app_url()}/welcome")
    chegou = esperar_url(page, r"/dashboard")
    registro.passo(acao="abrir /welcome já logado", url_final=page.url)
    registro.conferir(chegou, f"Não redirecionou ao painel (URL final {page.url})")
    finalizar(registro)
