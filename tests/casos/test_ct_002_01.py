from apoio import entrar_admin, finalizar, itens_menu

ESPERADOS = ["Painel", "Escolas de Origem", "Catálogo Curricular", "Configurações",
             "Usuários", "Permissões", "Recursos didáticos", "Tipos de aula", "Auditoria"]


def test_ct_002_01(page, registro):
    entrar_admin(page)
    menu = itens_menu(page)
    registro.passo(acao="listar o menu do Administrador", menu=", ".join(menu))
    registro.evidencia(page)
    faltando = [item for item in ESPERADOS if item not in menu]
    sobrando = [item for item in menu if item not in ESPERADOS]
    registro.conferir(not faltando, f"Itens ausentes no menu: {faltando}")
    if sobrando:
        registro.observar(f"Itens além do esperado: {sobrando}")
    registro.observar("Decisão aceita: Usuários, Permissões, Recursos, Tipos de aula e Auditoria dentro de Configurações.")
    finalizar(registro)
