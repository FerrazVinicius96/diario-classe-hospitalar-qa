from apoio import finalizar


def test_ct_002_09(registro):
    # TODO: automatizar quando a dependência for resolvida. Esperado: O módulo ausente recebe o padrão (completarPermissoes) e o acesso segue a matriz.
    registro.impedir('Depende de: Login de Gestão e Professor. Sem login de Gestão/Professor/Conecta no ambiente local.')
    finalizar(registro)
