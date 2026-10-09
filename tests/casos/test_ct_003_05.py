from apoio import finalizar


def test_ct_003_05(registro):
    # TODO: automatizar quando a dependência for resolvida. Esperado: Registros 'login_negado_sem_cadastro' e 'login_negado_cadastro_inativo' com data e hora.
    registro.impedir('Depende de: client_secret do Conecta. Sem login de Gestão/Professor/Conecta no ambiente local.')
    finalizar(registro)
