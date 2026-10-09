from apoio import finalizar, senha_admin


def test_ct_001_12(api, registro):
    api.get("/welcome/index/")
    resposta = api.post("/welcome/processarLogin", max_redirects=0,
                        form={"login": "00000000000", "password": senha_admin()})
    registro.passo(acao="POST de login sem dch_csrf", status_http=resposta.status,
                   redireciona_para=resposta.headers.get("refresh", ""))
    registro.conferir(resposta.status == 403, f"POST sem CSRF devolveu HTTP {resposta.status}")

    painel = api.get("/dashboard", max_redirects=0)
    destino = painel.headers.get("refresh", "")
    registro.passo(acao="abrir /dashboard depois", status_http=painel.status, redireciona_para=destino)
    registro.conferir("/welcome" in destino, "Sessão criada mesmo sem CSRF")
    registro.observar("Cobre parte do DEF-DCH-006 (Ricardo): combinar antes de registrar.")
    finalizar(registro)
