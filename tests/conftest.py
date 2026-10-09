import os
from pathlib import Path

import pytest

from envfile import carregar

RAIZ = Path(__file__).resolve().parents[1]


def pytest_configure(config):
    for chave, valor in carregar(RAIZ / ".env").items():
        os.environ.setdefault(chave, valor)
    ambiente = os.environ.get("QA_ENV", "local")
    if ambiente not in ("local", "hml"):
        raise pytest.UsageError("QA_ENV deve ser local ou hml.")
    if ambiente == "hml" and os.environ.get("QA_ALLOW_HML") != "1":
        raise pytest.UsageError("QA_ENV=hml sem QA_ALLOW_HML=1 na sessão.")
