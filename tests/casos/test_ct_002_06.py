from apoio import finalizar


def test_ct_002_06(registro):
    # TODO: automatizar quando a dependência for resolvida. Esperado: A sessão aberta mantém o perfil antigo; o novo login aplica o novo perfil.
    registro.impedir('Depende de: Login do MD-05 (Conecta ou empréstimo). Sem login de Gestão/Professor/Conecta no ambiente local.')
    finalizar(registro)
