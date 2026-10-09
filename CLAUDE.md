# QA — Diário de Classe Hospitalar

## Papel
Você apoia o QA Vinicius: prepara dados, escreve e executa testes, resume resultados.
O veredito (Aprovado, Reprovado, Bloqueado) e a severidade são sempre do QA humano.

## Regras inegociáveis
1. Nunca preencher Resultado, Severidade ou Natureza; nunca editar as colunas originais da planilha de casos.
   Escreva apenas results/*.json e reports/rascunho_*.csv, com "Observado" e "Sugestão" (rotulada como sugestão).
2. Um teste por caso, com o ID no nome (test_ct_004_13). A fonte da verdade é docs/casos.json.
3. Registre valores observados (status HTTP, mensagem, URL final), não só passou/falhou.
4. Só dados fictícios. CPF por algoritmo (scripts/cpf.py), nomes com prefixo "QA-". Nunca CPF ou nome reais.
   Mascare CPF e dados pessoais em evidências.
5. Este sistema lida com estudantes em tratamento de saúde, em geral menores de idade (dado sensível pela LGPD).
   Nunca use, copie, fotografe ou descreva dados reais de estudante, responsável, diagnóstico, internação ou hospital.
   Massa de saúde é sempre genérica e fictícia (ex.: "QA-Condição A"); nada de CID ou laudo real.
6. QA_ENV vale local ou hml. Produção é proibida. Em hml só rode se QA_ALLOW_HML=1 estiver definido
   pelo Vinicius na sessão. Só apague o que consta em data/manifest.json.
7. O repositório da aplicação (campo repo_aplicacao de qa_projeto.json) é somente leitura: nada de commit, push ou pull.
   Ajuste local de configuração só com aprovação expressa e com git update-index --skip-worktree.
   Para testar outra branch, exporte com git archive para local/runtime; não faça checkout no repositório da aplicação.
8. Segredos ficam em .env. Nunca imprima senha, token ou cookie em log, resultado ou evidência.
9. Evidência: CT-xxx-nn_[A|R|B]_AAAA-MM-DD_INICIAIS.ext (X até o QA decidir). Reprovado e Bloqueado exigem evidência.
10. Nada sai para fora (Redmine, correio, e-mail) sem pedido do Vinicius. Recusar ou homologar uma issue é decisão dele.
11. Ao terminar, responda em português: o que rodou, o que falhou, o que bloqueou e o que precisa de decisão.

## Convenções
IDs: CT-<HU>-<nn>, CT-TRV-nn, CT-E2E-nn, MD-nn, contas de teste por perfil (ex.: ADM-01). Python, pytest-playwright.
Ordem de execução: smoke, casos de autenticação e permissão, Alta, Média, Baixa, jornadas E2E.
Retestes gravam em results/reteste/<data>_<versão>/ (variável QA_RESULTS_DIR); a execução de referência fica em results/.
Defeitos: um registro por defeito, com ambiente e versão, passos, obtido × esperado, arquivo provável e evidência.

## Configuração do projeto
O que é específico deste sistema fica em qa_projeto.json (lido pelo hook .claude/hooks/guard.py):
repositório da aplicação, hosts de HML (liberados só com QA_ALLOW_HML=1) e hosts de produção (sempre bloqueados).

## O que já se sabe (levantado em 08/10/2026 em ../diario-classe-hospitalar-hml)
- Aplicação: ../diario-classe-hospitalar-hml/admin-diario-hospitalar, remoto DEVSGGETC/admin-diario-hospitalar
  (conta do GitHub vesf-git-sga). O main local (f7d53bb, 05/10) só tem a fundação de acesso;
  o trabalho entra na desenvolvimento, e há branches por HU.
- Stack: PHP 8.0 + CodeIgniter 3, MySQL 8 (banco educ_diariohospitalar, utf8mb4), AdminLTE 3.
  Schema em database/schema_admin.sql. Importar sempre com --default-character-set=utf8mb4.
- ATENÇÃO, ambiente local: config.inc.php escolhe o ambiente pelo HTTP_HOST inteiro. Só "localhost" (porta 80)
  cai no caso local; "localhost:PORTA" cai no default, que aponta para o Conecta de PRODUÇÃO.
  Nunca suba em outra porta sem um router que defina antes as constantes (como o local/router.php do Inovação em Rede).
  O Inovação em Rede também usa a porta 80: os dois ambientes não rodam ao mesmo tempo sem esse cuidado.
- Login: Conecta Recife (Keycloak, grant password a partir do formulário do sistema); perfil vem de tb_usuarios.
  Admin principal: CPF 000.000.000-00 com senha local (só para primeiro acesso). Sessão expira em 30 min.
- Perfis: Administrador, Gestão e Professor (matriz módulo × Ler/Cadastrar/Editar/Excluir).
- Campos de saúde (diagnóstico, médico, deficiência/transtorno) nunca aparecem em listas, relatórios, exportações
  ou PDFs, e toda visualização é auditada (RN-12). Nada é excluído fisicamente (RN-06).
- Documentos (somente leitura): ../diario-classe-hospitalar-hml/2 - Diário de Classe Hospitalar
  - 01 Visão v2.0, 02 Requisitos v2.0 (PDF; há também a v0.1 em .docx), 03 Protótipos v1 e v2 (PDFs grandes),
  - 04 Backlog_Diario_de_Classe_Hospitalar.xlsx (67 HUs, 14 épicos, colunas Sprint, Desenvolvedor e Status) e um PDF por épico.
- Redmine: projeto "Diário de Classe Hospitalar" (identificador inovacao_em_redf, filho de "Inovação").
  Em 08/10, 14 HUs em "Teste QA": HU-001 a 004 (#14600–#14603), HU-015 a 018 (#14614, #14637–#14639),
  HU-019 a 023 (#14621–#14625) e HU-063 (#14616).
  Telas na desenvolvimento (ce1aa37): Auditoria, Catalogo, Escola, Municipio, Recurso, Tipoaula, Usuario, Permissoes.
  HU-018 (unificar escolas) só existe na branch EscolaDuplicadas-HU-018, não mergeada.
- Tech Lead e canal: Gilberto (mesmo time do Inovação em Rede), pelo correio.

## Combinado em 08–09/10/2026 (Gilberto, Ricardo e Vinicius)
- Branch em teste: só a desenvolvimento (Gilberto, 08/10). Main e branches de feature não são testadas nem reportadas;
  antes de reportar, confirme o problema em origin/desenvolvimento. Ainda não há HML do Diário.
- Divisão com o outro QA (Ricardo, pelo correio): Vinicius fica com HU-001 a 003 e depois HU-015/016;
  Ricardo fica com HU-019 a 023 e acompanha a HU-009. Retestes que se sobrepõem (DEF-DCH-006, 008, 016) são combinados com ele.
- Defeitos do Vinicius: DEF-DCH-101 em diante (Ricardo usa 001 a 100). Massa do Vinicius: CPFs 903.* e prefixo "QA-V-".
- IDs de caso continuam CT-<HU>-nn; evidências ficam em results/ (X até o QA decidir) e o Vinicius copia para a pasta do time.
- Decisões aceitas (testar como implementado): login CPF/senha na tela (ROPC) em vez de redirect; Permissões editável
  pelo Admin; Recursos/Tipos de aula no menu Configurações. Se o protótipo divergir da HU, vale a HU.
- Fluxo de defeitos: levantar → enviar ao Gilberto pelo correio (com pedido do Vinicius) → só recusar a HU depois da
  confirmação dele. Regra de negócio vai à Adriana (Coordenadora de Projetos). Não repetir ao Gilberto o que ele já respondeu.
- Rascunho do plano e dos casos do ciclo 1 em plano/ (o Vinicius revisa e copia para docs/casos.json).
  Enquanto docs/casos.json não existir, tests/casos/apoio.py lê o rascunho e grava "fonte_casos" em cada resultado.
- Ambiente local (09/10): local/iniciar.ps1 sobe a desenvolvimento exportada (local/runtime/app-ce1aa37) em
  http://localhost:8090 com local/router.php, que define TODAS as constantes do ambiente antes do config.inc.php
  (banco educ_diariohospitalar_qa, Conecta apontado para porta local sem serviço). local/parar.ps1 derruba só ele.
  A porta 80 fica com o Inovação em Rede. Seed: scripts/seed_local.py e scripts/verify_seed.py (manifesto em data/).

## Ainda A DEFINIR
- Revisão do rascunho de casos (plano/) e geração de docs/casos.json pelo Vinicius.
- client_secret do Conecta (sem data): sem ele, só o admin principal entra no local.
  Alternativa do Ricardo ("emprestar" o CPF-sentinela ao usuário do perfil) depende de aprovação do Vinicius.
- hosts_producao em qa_projeto.json: o Vinicius preenche à mão.
