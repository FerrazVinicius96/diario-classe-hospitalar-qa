from apoio import finalizar


def test_ct_003_04(registro):
    # TODO: automatizar quando a dependência for resolvida. Esperado: Volta ao login do sistema e a sessão do Keycloak é encerrada.
    registro.impedir('Depende de: client_secret do Conecta. Sem login de Gestão/Professor/Conecta no ambiente local.')
    finalizar(registro)
