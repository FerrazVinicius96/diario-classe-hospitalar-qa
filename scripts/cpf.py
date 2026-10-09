"""CPF fictício com dígitos verificadores. Não use estes números fora do QA."""


def digitos_verificadores(nove: str) -> str:
    if len(nove) != 9 or not nove.isdigit():
        raise ValueError("A base do CPF precisa ter 9 dígitos.")
    numeros = [int(caractere) for caractere in nove]

    def dv(sequencia: list[int]) -> int:
        peso = len(sequencia) + 1
        soma = sum(numero * (peso - indice) for indice, numero in enumerate(sequencia))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    primeiro = dv(numeros)
    segundo = dv(numeros + [primeiro])
    return f"{primeiro}{segundo}"


def completar(nove: str) -> str:
    return nove + digitos_verificadores(nove)


def somente_digitos(valor: str) -> str:
    return "".join(caractere for caractere in valor if caractere.isdigit())


def formatar(digitos: str) -> str:
    cpf = somente_digitos(digitos)
    if len(cpf) != 11:
        raise ValueError("CPF precisa ter 11 dígitos para formatar.")
    return f"{cpf[0:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:11]}"


def valido(valor: str) -> bool:
    cpf = somente_digitos(valor)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    return cpf[9:11] == digitos_verificadores(cpf[:9])


def da_base(indice: int) -> str:
    if not 0 <= indice <= 99_999_999:
        raise ValueError("Índice de CPF fora da faixa fictícia.")
    return completar(f"9{indice:08d}")
