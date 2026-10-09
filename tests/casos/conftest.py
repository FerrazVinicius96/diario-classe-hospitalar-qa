import pytest

from apoio import Registro, app_url, carregar_casos, id_do_teste

CASOS = carregar_casos()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    resultado = yield
    relatorio = resultado.get_result()
    if relatorio.when == "call" or (relatorio.when == "setup" and relatorio.failed):
        item.relatorio_caso = relatorio


@pytest.fixture
def registro(request):
    caso_id = id_do_teste(request.node.originalname)
    if caso_id not in CASOS:
        pytest.fail(f"{caso_id} não consta da fonte de casos.")
    reg = Registro(CASOS[caso_id])
    yield reg
    relatorio = getattr(request.node, "relatorio_caso", None)
    estado = relatorio.outcome if relatorio else "error"
    erro = ""
    if relatorio is not None and relatorio.failed and not reg.divergencias:
        erro = str(relatorio.longrepr)
    reg.salvar(estado, erro)


@pytest.fixture
def api(playwright):
    """Contexto HTTP sem redirecionamento automático e sem cookies do navegador."""
    contexto = playwright.request.new_context(base_url=app_url())
    yield contexto
    contexto.dispose()


@pytest.fixture
def browser_context_args(browser_context_args):
    return {**browser_context_args, "locale": "pt-BR", "viewport": {"width": 1366, "height": 768}}


def pytest_collection_modifyitems(items):
    ordem = {"CT-TRV": 0, "CT-001": 1, "CT-002": 2, "CT-003": 3}
    prioridade = {"Alta": 0, "Média": 1, "Baixa": 2}

    def chave(item):
        caso = CASOS.get(id_do_teste(getattr(item, "originalname", item.name)), {})
        return (ordem.get(caso.get("id", "")[:6], 9), prioridade.get(caso.get("prioridade"), 9), item.name)

    items.sort(key=chave)
