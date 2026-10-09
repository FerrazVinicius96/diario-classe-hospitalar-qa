from apoio import banco, entrar_admin, finalizar, itens_menu, texto_limpo


def test_ct_001_03(page, registro):
    entrar_admin(page)
    perfil = texto_limpo(page.locator(".app-perfil strong").inner_text())
    usuario = texto_limpo(page.locator(".app-user strong").inner_text())
    with banco() as c, c.cursor() as cur:
        cur.execute("SELECT usu_nome FROM tb_usuarios WHERE REPLACE(REPLACE(usu_cpf,'.',''),'-','')='00000000000'")
        nome_cadastro = cur.fetchone()[0]
    registro.passo(acao="login MD-01", url_final=page.url, perfil_em_uso=perfil, menu=", ".join(itens_menu(page)))
    registro.evidencia(page)
    registro.conferir("/dashboard" in page.url, f"URL final {page.url}")
    registro.conferir(perfil == "Administrador", f"Perfil em uso exibido: {perfil!r}")
    registro.conferir(usuario == nome_cadastro, "Nome no topo diferente do cadastro")
    finalizar(registro)
