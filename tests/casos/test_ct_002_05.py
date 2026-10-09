from apoio import finalizar


def test_ct_002_05(registro):
    # TODO: automatizar quando a dependência for resolvida. Esperado: HTTP 403 e nenhum registro alterado.
    registro.impedir('Depende de: Login de Professor. Sem login de Gestão/Professor/Conecta no ambiente local.')
    finalizar(registro)
