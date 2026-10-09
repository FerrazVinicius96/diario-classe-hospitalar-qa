from apoio import app_url, entrar_admin, finalizar


def test_ct_002_10(page, registro):
    entrar_admin(page)
    resposta = page.goto(f"{app_url()}/permissoes")
    page.wait_for_load_state("networkidle")
    caixas = page.locator("input.dch-matrix-check")
    total = caixas.count()
    desabilitadas = page.locator("input.dch-matrix-check:disabled").count()
    registro.passo(acao="Admin abre Permissões (sem salvar)", status_http=resposta.status if resposta else None,
                   url_final=page.url, caixas=total, desabilitadas=desabilitadas)
    registro.evidencia(page)
    registro.conferir(resposta is not None and resposta.status == 200, "Admin não abriu Permissões")
    registro.conferir(total > 0 and desabilitadas < total, "Matriz sem caixas editáveis para o Admin")
    registro.observar("Decisão aceita: Permissões editável pelo Admin. A matriz não foi salva.")
    registro.impedir("2ª parte (Gestão recebe 403 e não vê o item) depende de login de Gestão: Conecta sem client_secret.",
                     parcial=True)
    finalizar(registro)
