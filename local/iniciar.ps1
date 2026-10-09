# Sobe o Diário local de QA em http://localhost:8090 (servidor embutido do PHP + local/router.php).
# A porta 80 fica livre para o Inovação em Rede. Lê a conexão do banco do .env sem imprimir valores.
# Uso: powershell -File local\iniciar.ps1 [-Porta 8090] [-App local\runtime\app-ce1aa37]
param([int]$Porta = 8090, [string]$App = '')
$ErrorActionPreference = 'Stop'
$raiz = Split-Path -Parent $PSScriptRoot
$php = (Get-Command php -ErrorAction SilentlyContinue).Source
if (-not $php) { $php = Get-ChildItem "$env:LOCALAPPDATA\Microsoft\WinGet\Packages\PHP.PHP.8.1*\php.exe" | Select-Object -First 1 -ExpandProperty FullName }
if (-not $php) { Write-Host 'php.exe não encontrado.'; exit 2 }

foreach ($linha in Get-Content (Join-Path $raiz '.env') -Encoding utf8) {
    if ($linha -match '^\s*(QA_DB_\w+|QA_URL_CONECTA)\s*=\s*(.*)$') { Set-Item "env:$($Matches[1])" $Matches[2].Trim() }
}
if (-not $App) { $App = Join-Path $raiz 'local\runtime\app-ce1aa37' }
$env:QA_APP_DOCROOT = (Resolve-Path $App).Path

if (Get-NetTCPConnection -LocalPort $Porta -State Listen -ErrorAction SilentlyContinue) { Write-Host "Porta $Porta já em uso."; exit 3 }

$rt = Join-Path $raiz 'local\runtime'
New-Item -ItemType Directory -Force "$rt\sessions", "$rt\logs" | Out-Null
$ext = Join-Path (Split-Path $php) 'ext'
foreach ($endereco in "127.0.0.1:$Porta", "[::1]:$Porta") {
    Start-Process -FilePath $php -WindowStyle Hidden -ArgumentList @(
        '-c', "`"$raiz\local\php.ini`"", '-d', "extension_dir=`"$ext`"",
        '-d', "session.save_path=`"$rt\sessions`"", '-d', "error_log=`"$rt\logs\php.log`"",
        '-S', $endereco, '-t', "`"$env:QA_APP_DOCROOT`"", "`"$raiz\local\router.php`"")
}
Write-Host "Diário local em http://localhost:$Porta (log em local\runtime\logs\php.log)."
