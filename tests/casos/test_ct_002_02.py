from apoio import finalizar


def test_ct_002_02(registro):
    # TODO: automatizar quando a dependência for resolvida. Esperado: Conforme a seção 2 do Requisitos: catálogo e recursos em leitura; usuários só para criar Professor; trilha de auditoria; escolas de origem.
    registro.impedir('Depende de: Login de Gestão. Sem login de Gestão/Professor/Conecta no ambiente local.')
    finalizar(registro)
