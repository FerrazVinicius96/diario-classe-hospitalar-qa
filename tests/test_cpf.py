import cpf


def test_cpf_conhecido():
    assert cpf.valido("52998224725")
    assert cpf.formatar("52998224725") == "529.982.247-25"


def test_base_ficticia_e_valida():
    gerado = cpf.da_base(4)
    assert cpf.valido(gerado)
    assert gerado.startswith("9")
    assert not cpf.valido(gerado[:-1] + ("0" if gerado[-1] != "0" else "1"))


def test_rejeita_curto_e_repetido():
    assert not cpf.valido("1234567890")
    assert not cpf.valido("11111111111")
