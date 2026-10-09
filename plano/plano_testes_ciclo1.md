# Plano de testes — Ciclo 1 (rascunho para revisão)

Diário de Classe Hospitalar · QA Vinicius · rascunho de 09/10/2026

## 1. Escopo
- **Branch:** só a `desenvolvimento`. A versão de referência é a `ce1aa37` (PR #10, de 08/10). A branch main e as de feature ficam de fora até o merge (decisão do Gilberto em 08/10).
- **HUs do Vinicius:** HU-001, HU-002 e HU-003 (Épico E1). Depois vêm Escolas de Origem (HU-015 e HU-016).
- **HUs do Ricardo:** HU-019 a HU-023 e o acompanhamento da HU-009.
- **Fora do ciclo:** HU-004 (não está na lista "Teste QA" do Gilberto), telas pedagógicas e branches não mergeadas.

## 2. Fontes
- Épico E1 Autenticação e Acesso, de 02/10.
- Requisitos v2.0: seção 2 (matriz de permissões), seção 3.1 (RF-01 a RF-04 e RN-04.1), RNF-02 e RNF-03.
- Código da `desenvolvimento`, lido sem alterar.
- Decisões aceitas, que divergem da HU e são testadas como estão implementadas:
  - login com CPF e senha na tela (ROPC);
  - tela Permissões editável pelo Admin;
  - Recursos e Tipos de aula no menu Configurações.

## 3. Ambiente
- Ambiente local, servido só em `http://localhost` na porta 80, com export da `desenvolvimento` via `git archive` para `local/runtime`.
- Banco `educ_diariohospitalar`, sempre importado com `--default-character-set=utf8mb4`.
- Não há HML do Diário por enquanto.
- O Inovação em Rede também usa a porta 80, então os dois não sobem juntos.

## 4. Massa (fictícia, CPFs de prefixo 903, nomes com prefixo QA-V-)
| ID | Perfil | CPF | Situação |
|---|---|---|---|
| MD-01 | Administrador (CPF-sentinela da aplicação) | 000.000.000-00 | ativo |
| MD-02 | Gestão | 903.000.001-54 | ativo |
| MD-03 | Professor | 903.000.002-35 | ativo |
| MD-04 | Professor | 903.000.003-16 | inativo |
| MD-05 | Administrador secundário | 903.000.004-05 | ativo |
| MD-06 | sem cadastro | 903.000.005-88 | — |

## 5. Casos (31), na ordem de execução
| Grupo | Casos | Executáveis hoje |
|---|---|---|
| Smoke | CT-TRV-01 | sim |
| Autenticação (HU-001) | CT-001-01 a 14 | 10 (07, 09 e 14 são manuais; 07 e 09 dependem do Conecta) |
| Permissão (HU-002) | CT-002-01 a 10 | 01 e a primeira parte do 10; os outros dependem do login de Gestão e de Professor |
| Bloqueio sem cadastro (HU-003) | CT-003-01 a 06 | 01 e 06 (o 06 precisa da sua aprovação) |

O detalhe de cada caso (passos, esperado, dependência) está em `casos_rascunho_ciclo1.json`. Depois da revisão, você copia esse arquivo para `docs/casos.json`, porque o agente não escreve em `docs/`.

## 6. Impedimentos e dependências
1. **Client_secret do Conecta** (sem data): impede o login de Gestão e de Professor e quase toda a HU-003.
2. **Alternativa para a HU-002:** emprestar o CPF-sentinela ao usuário QA-V- do perfil e devolvê-lo depois, como faz o Ricardo. Isso altera `tb_usuarios` no banco local, por isso **depende da sua aprovação** e de registro no `data/manifest.json`.
3. Telas pedagógicas (CT-002-08): só depois do merge das branches.

## 7. Pontos levantados na leitura do código (não são veredito)
- **Recursos e Tipos de aula para Gestão e Professor:** a seção 2 prevê "Leitura", mas a matriz padrão (`permissoesPadrao`) não dá acesso. Ver CT-002-02 e 03.
- **Usuários pela Gestão:** a seção 2 diz "só Professor", mas a matriz dá acesso total. O assunto já está no DEF-DCH-023 do Ricardo e deve ser conferido no merge.
- **Conecta fora do ar:** a falha aparece como "Credenciais inválidas" (Welcome.php:55). Ver CT-001-14.
- **CPF completo na auditoria:** o CPF vai sem máscara para `tb_log.log_adicionais` (Welcome_model.php:54). Ver CT-003-05.
- **Admin principal inativo:** recebe "Credenciais inválidas" em vez do texto do RN-04.1. Ver CT-003-06.

## 8. Sobreposição com o Ricardo
O CT-001-11 cobre o DEF-DCH-016, o CT-001-12 cobre o DEF-DCH-006 e o CT-002-09 cobre o DEF-DCH-008, que são retestes do Ricardo. Os resultados devem ser combinados com ele antes de qualquer registro, para não duplicar.

## 9. Registro
- O observado vai para `results/` e as evidências seguem o padrão `CT-xxx-nn_X_AAAA-MM-DD_VF.ext`.
- Defeitos usam IDs a partir de DEF-DCH-101.
- Veredito, severidade e natureza são decisão do Vinicius.
