from apoio import finalizar


def test_ct_002_04(registro):
    # TODO: automatizar quando a dependência for resolvida. Esperado: HTTP 403 'Acesso negado', sem dados da tela.
    registro.impedir('Depende de: Login de Gestão e Professor. Sem login de Gestão/Professor/Conecta no ambiente local.')
    finalizar(registro)
