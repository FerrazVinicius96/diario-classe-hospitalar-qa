from apoio import finalizar


def test_ct_003_02(registro):
    # TODO: automatizar quando a dependência for resolvida. Esperado: URL /welcome/acessoNegado com o texto do RN-04.1; nenhuma sessão do sistema criada.
    registro.impedir('Depende de: client_secret do Conecta. Sem login de Gestão/Professor/Conecta no ambiente local.')
    finalizar(registro)
