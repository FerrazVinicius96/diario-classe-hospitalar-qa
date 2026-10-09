from apoio import finalizar


def test_ct_002_08(registro):
    # TODO: automatizar quando a dependência for resolvida. Esperado: Nenhuma acessível ao Administrador.
    registro.impedir('Telas pedagógicas ainda não estão na desenvolvimento (reavaliar após o merge).')
    finalizar(registro)
