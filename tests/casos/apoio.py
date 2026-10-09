"""Apoio comum dos casos: leitura dos casos, login, registro do observado e evidência mascarada.

Nada aqui decide veredito: o teste registra o observado e as divergências em relação ao esperado.
Senha, token e cookie nunca entram no registro.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import date, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
FONTE_OFICIAL = RAIZ / "docs" / "casos.json"
FONTE_RASCUNHO = RAIZ / "plano" / "casos_rascunho_ciclo1.json"
INICIAIS = json.loads((RAIZ / "qa_projeto.json").read_text(encoding="utf-8")).get("iniciais_evidencia", "XX")
RN_04_1_TITULO = "Acesso não disponível."
RN_04_1_TEXTO = ("Seu usuário não possui cadastro no sistema Diário de Classe Hospitalar. "
                 "Procure a gestão da EMTI Hospitalar Semear para solicitar o cadastro.")
CPF_SEM_CADASTRO = "903.000.005-88"
CPF_PROFESSOR = "903.000.002-35"

_MASCARA_JS = r"""
() => {
  const cpf = /\d{3}\.?\d{3}\.?\d{3}-?\d{2}/g;
  const andar = (no) => {
    if (no.nodeType === 3) { no.textContent = no.textContent.replace(cpf, '***.***.***-**'); return; }
    no.childNodes.forEach(andar);
  };
  andar(document.body);
  document.querySelectorAll('input').forEach((i) => {
    if (i.type === 'password') { i.value = ''; }
    else if (cpf.test(i.value)) { i.value = '***.***.***-**'; }
  });
}
"""


def fonte_casos() -> Path:
    return FONTE_OFICIAL if FONTE_OFICIAL.exists() else FONTE_RASCUNHO


def carregar_casos() -> dict[str, dict]:
    dados = json.loads(fonte_casos().read_text(encoding="utf-8"))
    return {caso["id"]: caso for caso in dados["casos"]}


def id_do_teste(nome: str) -> str:
    """test_ct_001_01 -> CT-001-01; test_ct_trv_01 -> CT-TRV-01."""
    partes = nome.removeprefix("test_").split("_")
    return "-".join(parte.upper() for parte in partes)


def diretorio_resultados() -> Path:
    destino = RAIZ / os.environ.get("QA_RESULTS_DIR", "results")
    (destino / "evidencias").mkdir(parents=True, exist_ok=True)
    return destino


def app_url() -> str:
    return os.environ.get("QA_APP_BASE_URL", "http://localhost:8090").rstrip("/")


def resumo_hash(valor: str | None) -> str:
    """Só para comparar cookies sem gravar o valor."""
    return hashlib.sha256((valor or "").encode()).hexdigest()[:10] if valor else "(ausente)"


def texto_limpo(texto: str | None) -> str:
    return re.sub(r"\s+", " ", texto or "").strip()


class Registro:
    def __init__(self, caso: dict):
        self.caso = caso
        self.passos: list[dict] = []
        self.divergencias: list[str] = []
        self.impedimentos: list[str] = []
        self.observacoes: list[str] = []
        self.evidencias: list[str] = []
        self.situacao_execucao = "executado"
        self.inicio = datetime.now()

    def passo(self, **valores) -> None:
        self.passos.append({chave: str(valor)[:300] for chave, valor in valores.items()})

    def conferir(self, condicao: bool, divergencia: str) -> bool:
        if not condicao:
            self.divergencias.append(divergencia)
        return condicao

    def observar(self, texto: str) -> None:
        self.observacoes.append(texto)

    def impedir(self, motivo: str, parcial: bool = False) -> None:
        self.impedimentos.append(motivo)
        self.situacao_execucao = "parcial" if parcial else "impedido"

    def evidencia(self, page, sufixo: str = "") -> str:
        nome = f"{self.caso['id']}_X_{date.today().isoformat()}_{INICIAIS}{('_' + sufixo) if sufixo else ''}.png"
        try:
            page.evaluate(_MASCARA_JS)
        except Exception:  # página sem body (ex.: redirecionamento em andamento)
            pass
        page.screenshot(path=str(diretorio_resultados() / "evidencias" / nome), full_page=True)
        self.evidencias.append(f"evidencias/{nome}")
        return nome

    def salvar(self, resultado_pytest: str, erro_tecnico: str = "") -> None:
        dados = {
            "id": self.caso["id"],
            "hu": self.caso.get("hu"),
            "epico": self.caso.get("epico"),
            "cenario": self.caso.get("cenario"),
            "prioridade": self.caso.get("prioridade"),
            "esperado": self.caso.get("esperado"),
            "fonte_casos": fonte_casos().relative_to(RAIZ).as_posix(),
            "ambiente": os.environ.get("QA_ENV", "local"),
            "base_url": app_url(),
            "versao_app": os.environ.get("QA_APP_VERSAO", "ce1aa37"),
            "executado_em": self.inicio.isoformat(timespec="seconds"),
            "situacao_execucao": self.situacao_execucao,
            "pytest": resultado_pytest,
            "passos": self.passos,
            "divergencias": self.divergencias,
            "impedimentos": self.impedimentos,
            "observacoes": self.observacoes,
            "evidencias": self.evidencias,
            "erro_tecnico": erro_tecnico[:1500],
        }
        destino = diretorio_resultados() / f"{self.caso['id']}.json"
        destino.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def finalizar(reg: Registro) -> None:
    """Sinaliza no pytest: skip quando impedido, falha quando há divergência. Não é veredito."""
    import pytest

    if reg.situacao_execucao == "impedido":
        pytest.skip("Impedimento: " + " | ".join(reg.impedimentos))
    assert not reg.divergencias, " | ".join(reg.divergencias)


def senha_admin() -> str:
    senha = os.environ.get("QA_ADMIN_SENHA")
    if not senha:
        raise RuntimeError("QA_ADMIN_SENHA ausente no .env (rode scripts/seed_local.py).")
    return senha


def abrir_login(page) -> None:
    page.goto(f"{app_url()}/welcome/index/")
    page.wait_for_selector("#login")


def entrar(page, cpf: str, senha: str) -> None:
    """Preenche o formulário de login. A senha não é registrada em lugar nenhum."""
    abrir_login(page)
    page.fill("#login", cpf)
    page.fill("#password", senha)
    with page.expect_navigation():
        page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")


def entrar_admin(page) -> None:
    entrar(page, os.environ.get("QA_ADMIN_CPF", "00000000000"), senha_admin())
    page.wait_for_url(re.compile(r"/dashboard"), timeout=10_000)


def itens_menu(page) -> list[str]:
    return [texto_limpo(t) for t in page.locator(".app-nav a.app-nav-link").all_inner_texts() if texto_limpo(t)]


def esperar_url(page, padrao: str, tempo_ms: int = 8_000) -> bool:
    try:
        page.wait_for_url(re.compile(padrao), timeout=tempo_ms)
        return True
    except Exception:
        return False


def banco():
    import pymysql

    return pymysql.connect(
        host=os.environ.get("QA_DB_HOST", "127.0.0.1"), port=int(os.environ.get("QA_DB_PORT", "3306")),
        user=os.environ["QA_DB_USER"], password=os.environ.get("QA_DB_PASSWORD", ""),
        database=os.environ.get("QA_DB_NAME", "educ_diariohospitalar_qa"), charset="utf8mb4", autocommit=True,
    )


def csrf_do_login(contexto_api) -> str:
    """Abre a tela de login num contexto de API e devolve o token CSRF do formulário (não é gravado)."""
    resposta = contexto_api.get("/welcome/index/")
    achado = re.search(r'name="dch_csrf" value="([^"]+)"', resposta.text())
    return achado.group(1) if achado else ""
