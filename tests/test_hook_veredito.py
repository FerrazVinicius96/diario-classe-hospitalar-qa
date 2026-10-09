import guard

CONFIG = {
    "repo_aplicacao": "../diario-app-exemplo",
    "hosts_locais": ["localhost", "127.0.0.1", "::1"],
    "hosts_hml": ["hml.exemplo.invalid"],
    "hosts_producao": ["producao.exemplo.invalid"],
}


def avaliar(evento):
    return guard.avaliar(evento, CONFIG)


def test_bloqueia_aprovado_em_arquivo_de_saida():
    bloqueado, motivo = avaliar(
        {"tool_name": "Write", "tool_input": {"file_path": "results/ct_001.json", "content": "Aprovado"}}
    )
    assert bloqueado
    assert motivo


def test_permite_observado_sem_veredito():
    bloqueado, _ = avaliar(
        {
            "tool_name": "Write",
            "tool_input": {"file_path": "results/ct_001.json", "content": '{"observado": "tela de login", "http": 200}'},
        }
    )
    assert not bloqueado


def test_bloqueia_coluna_de_veredito_no_rascunho():
    bloqueado, _ = avaliar(
        {"tool_name": "Write", "tool_input": {"file_path": "reports/rascunho_planilha.csv", "content": "ID,Resultado\nCT-001-01,ok\n"}}
    )
    assert bloqueado


def test_bloqueia_leitura_de_env():
    bloqueado, _ = avaliar({"tool_name": "Read", "tool_input": {"file_path": r"c:\qa\.env"}})
    assert bloqueado


def test_permite_exemplo_de_env():
    bloqueado, _ = avaliar({"tool_name": "Read", "tool_input": {"file_path": ".env.example"}})
    assert not bloqueado


def test_bloqueia_docs_e_originais():
    bloqueado, _ = avaliar({"tool_name": "Edit", "tool_input": {"file_path": "docs/plano.md", "new_string": "x"}})
    assert bloqueado


def test_bloqueia_escrita_no_repositorio_da_aplicacao():
    bloqueado, _ = avaliar(
        {"tool_name": "Edit", "tool_input": {"file_path": r"c:\dev\diario-app-exemplo\config.php"}}
    )
    assert bloqueado


def test_bloqueia_git_push_na_aplicacao():
    bloqueado, _ = avaliar(
        {"tool_name": "Bash", "tool_input": {"command": "git -C ../diario-app-exemplo push"}}
    )
    assert bloqueado


def test_permite_git_status_na_aplicacao():
    bloqueado, _ = avaliar(
        {"tool_name": "Bash", "tool_input": {"command": "git -C ../diario-app-exemplo status"}}
    )
    assert not bloqueado


def test_bloqueia_hml_sem_flag(monkeypatch):
    monkeypatch.delenv("QA_ALLOW_HML", raising=False)
    monkeypatch.setenv("QA_ENV", "local")
    bloqueado, _ = avaliar({"tool_name": "Bash", "tool_input": {"command": "set QA_ENV=hml\npython -m pytest"}})
    assert bloqueado


def test_hml_so_com_flag(monkeypatch):
    monkeypatch.delenv("QA_ALLOW_HML", raising=False)
    assert avaliar({"tool_name": "Bash", "tool_input": {"command": "curl https://hml.exemplo.invalid/"}})[0]
    monkeypatch.setenv("QA_ALLOW_HML", "1")
    assert not avaliar({"tool_name": "Bash", "tool_input": {"command": "curl https://hml.exemplo.invalid/"}})[0]


def test_bloqueia_producao_mesmo_com_flag(monkeypatch):
    monkeypatch.setenv("QA_ALLOW_HML", "1")
    bloqueado, _ = avaliar({"tool_name": "Bash", "tool_input": {"command": "curl https://producao.exemplo.invalid/"}})
    assert bloqueado


def test_permite_localhost():
    bloqueado, _ = avaliar({"tool_name": "Bash", "tool_input": {"command": "curl http://127.0.0.1:8080/"}})
    assert not bloqueado


def test_bloqueia_escrita_em_pasta_somente_leitura():
    config = {**CONFIG, "pastas_somente_leitura": ["../pasta-documentos-exemplo"]}
    bloqueado, _ = guard.avaliar(
        {"tool_name": "Write", "tool_input": {"file_path": r"c:\dev\pasta-documentos-exemplo\docs\plano.md", "content": "x"}},
        config,
    )
    assert bloqueado


def test_sem_repo_definido_nao_quebra():
    bloqueado, _ = guard.avaliar({"tool_name": "Edit", "tool_input": {"file_path": "tests/casos/apoio.py"}}, {})
    assert not bloqueado
