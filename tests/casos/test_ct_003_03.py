from apoio import finalizar


def test_ct_003_03(registro):
    # TODO: automatizar quando a dependência for resolvida. Esperado: Mesma tela e mesmo texto do CT-003-02.
    registro.impedir('Depende de: client_secret do Conecta. Sem login de Gestão/Professor/Conecta no ambiente local.')
    finalizar(registro)
