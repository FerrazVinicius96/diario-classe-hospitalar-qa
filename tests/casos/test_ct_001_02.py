from apoio import finalizar

ROTAS = ["/dashboard", "/usuario", "/permissoes", "/auditoria", "/catalogo", "/escola", "/recurso", "/tipoaula"]


def test_ct_001_02(api, registro):
    for rota in ROTAS:
        resposta = api.get(rota, max_redirects=0)
        destino = resposta.headers.get("refresh") or resposta.headers.get("location") or ""
        corpo = resposta.text()
        registro.passo(rota=rota, status_http=resposta.status, redireciona_para=destino, tamanho_corpo=len(corpo))
        registro.conferir("/welcome" in destino, f"{rota}: não redirecionou ao login (status {resposta.status}, destino {destino!r})")
        registro.conferir(len(corpo.strip()) == 0, f"{rota}: devolveu {len(corpo)} bytes de conteúdo sem sessão")
    finalizar(registro)
