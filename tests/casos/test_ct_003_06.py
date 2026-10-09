from apoio import finalizar


def test_ct_003_06(registro):
    # TODO: automatizar quando a dependência for resolvida. Esperado: A HU pede a mensagem do RN-04.1 para inativos; registrar o que aparece.
    registro.impedir('Aguarda aprovação do Vinicius para inativar e reativar o admin principal no banco local.')
    finalizar(registro)
