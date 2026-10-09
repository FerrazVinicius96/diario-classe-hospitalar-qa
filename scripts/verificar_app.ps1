# Verifica se o repositório da aplicação tem atualização no remoto. Somente leitura.
# Faz apenas "git fetch" (não altera arquivos). Nunca faz pull, merge, commit ou push.
# O caminho vem de repo_aplicacao em qa_projeto.json.
# Uso: powershell -File scripts\verificar_app.ps1
$ErrorActionPreference = 'Continue'
$raiz = Split-Path -Parent $PSScriptRoot
$config = Get-Content (Join-Path $raiz 'qa_projeto.json') -Raw -Encoding utf8 | ConvertFrom-Json
if (-not $config.repo_aplicacao) {
    Write-Host 'repo_aplicacao ainda não definido em qa_projeto.json.'
    exit 2
}
$app = (Resolve-Path (Join-Path $raiz $config.repo_aplicacao) -ErrorAction SilentlyContinue).Path
if (-not $app -or -not (Test-Path (Join-Path $app '.git'))) {
    Write-Host "A pasta $($config.repo_aplicacao) ainda não é um clone git. Peça ao Vinicius para clonar."
    exit 2
}

# O GCM tem mais de uma conta do GitHub; a que acessa a DEVSGGETC é vesf-git-sga.
# A conta vai só neste comando (não grava nada na configuração do repositório).
$usuario = if ($env:QA_GITHUB_USER) { $env:QA_GITHUB_USER } else { 'vesf-git-sga' }
git -c "credential.username=$usuario" -C $app fetch --prune --quiet origin
if ($LASTEXITCODE -ne 0) { Write-Host 'Falha no git fetch (VPN, rede ou credencial).'; exit 3 }

$sujeira = git -C $app status --porcelain
if ($sujeira) {
    Write-Host 'ATENÇÃO: a pasta da aplicação tem arquivos alterados ou novos (não commitar; investigar a origem):'
    $sujeira | ForEach-Object { Write-Host "  $_" }
} else {
    Write-Host 'Pasta da aplicação limpa (git status vazio).'
}

$branch = git -C $app rev-parse --abbrev-ref HEAD
$upstream = git -C $app rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>$null
Write-Host "Branch local: $branch"
Write-Host "Versão local: $(git -C $app log -1 --format='%h %ad %s' --date=format:'%Y-%m-%d %H:%M')"
Write-Host 'Branches remotos:'
git -C $app branch -r --format='  %(refname:short)  %(committerdate:short)  %(objectname:short)  %(subject)'

if (-not $upstream) { exit 0 }
$atras = [int]((git -C $app rev-list --left-right --count "HEAD...$upstream") -split '\s+')[1]
Write-Host "Remoto ($upstream): $atras commit(s) à frente da versão local."
if ($atras -eq 0) { Write-Host 'Sem atualização.'; exit 0 }
git -C $app log --format='  %h %ad %an: %s' --date=short "HEAD..$upstream"
Write-Host "`nPara atualizar, o Vinicius roda: git -C `"$app`" pull --ff-only"
exit 1
