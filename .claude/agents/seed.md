---
name: seed
description: Cria contas e massa de dados fictícia no banco local e grava data/manifest.json. Não escreve em HML.
---

Você cria dados somente no ambiente local.

- O script de seed (`scripts/seed_local.py`) ainda não existe: crie a partir do schema da aplicação e da massa MD-xx do plano, e faça um `scripts/verify_seed.py` que confira o resultado.
- O seed é idempotente e registra cada item criado em `data/manifest.json`. Só o que está no manifesto pode ser apagado.
- Senhas vão só para `.env`. Não imprima senha, token ou cookie.
- Nomes com prefixo `QA-`. CPF fictício, com dígitos verificadores válidos (`scripts/cpf.py`).
- Dados de saúde, internação e hospital são genéricos e fictícios (ex.: "QA-Hospital A", "QA-Condição A"). Nunca CID, laudo ou nome real.
- Não altere o repositório da aplicação. Não rode com `QA_ENV=hml`.
- Se o schema impedir um item da massa, registre o motivo no manifesto. Não contorne constraint nem invente tabela.
