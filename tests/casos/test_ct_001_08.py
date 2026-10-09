from apoio import app_url, entrar_admin, esperar_url, finalizar


def test_ct_001_08(page, registro):
    entrar_admin(page)
    page.click("a.app-logout")
    esperar_url(page, r"/welcome")
    page.wait_for_load_state("networkidle")
    registro.passo(acao="clicar em Sair", url_final=page.url)
    registro.evidencia(page, "apos_sair")
    registro.conferir("saiu=1" in page.url, f"URL após Sair: {page.url}")

    page.goto(f"{app_url()}/dashboard")
    voltou = esperar_url(page, r"/welcome")
    registro.passo(acao="abrir /dashboard após sair", url_final=page.url)
    registro.conferir(voltou, f"/dashboard abriu após Sair ({page.url})")

    page.go_back()
    page.wait_for_timeout(1500)
    menu_visivel = page.locator(".app-nav").count() > 0
    registro.passo(acao="Voltar do navegador", url_final=page.url, menu_visivel=menu_visivel)
    registro.evidencia(page, "voltar")
    if menu_visivel:
        page.reload()
        esperar_url(page, r"/welcome")
        registro.passo(acao="recarregar a página exibida pelo Voltar", url_final=page.url)
        registro.observar("O Voltar exibiu a página do painel em cache; ao recarregar, a aplicação pediu login.")
        registro.conferir("/welcome" in page.url, "Página do painel recarregada sem sessão")
    finalizar(registro)
