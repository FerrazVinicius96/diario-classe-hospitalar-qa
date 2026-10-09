from apoio import finalizar


def test_ct_002_03(registro):
    # TODO: automatizar quando a dependência for resolvida. Esperado: Sem Usuários, Permissões e Auditoria; catálogo e recursos em leitura; escolas de origem.
    registro.impedir('Depende de: Login de Professor. Sem login de Gestão/Professor/Conecta no ambiente local.')
    finalizar(registro)
