from apoio import finalizar


def test_ct_001_07(registro):
    # TODO: automatizar quando a dependência for resolvida. Esperado: Dashboard com o menu do perfil do cadastro interno.
    registro.impedir('Depende de: client_secret do Conecta (sem data, segundo o Gilberto). Sem login de Gestão/Professor/Conecta no ambiente local.')
    finalizar(registro)
