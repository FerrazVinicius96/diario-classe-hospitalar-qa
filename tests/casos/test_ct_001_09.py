from apoio import finalizar


def test_ct_001_09(registro):
    # TODO: automatizar quando a dependência for resolvida. Esperado: Sessão do Keycloak encerrada (logout com refresh_token retorna 204).
    registro.impedir('Depende de: client_secret do Conecta. Sem login de Gestão/Professor/Conecta no ambiente local.')
    finalizar(registro)
