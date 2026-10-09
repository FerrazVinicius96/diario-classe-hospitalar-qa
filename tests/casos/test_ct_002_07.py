from apoio import finalizar


def test_ct_002_07(registro):
    # TODO: automatizar quando a dependência for resolvida. Esperado: Tudo o que o Professor pode, a Gestão também pode.
    registro.impedir('Depende de: Login de Gestão e Professor. Sem login de Gestão/Professor/Conecta no ambiente local.')
    finalizar(registro)
