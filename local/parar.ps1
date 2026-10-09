# Para só o servidor do Diário local de QA (processos php -S na porta indicada). Não toca no Inovação em Rede.
# Uso: powershell -File local\parar.ps1 [-Porta 8090]
param([int]$Porta = 8090)
$alvos = Get-CimInstance Win32_Process -Filter "Name='php.exe'" | Where-Object { $_.CommandLine -match ":$Porta\b" -and $_.CommandLine -match 'diario-classe-hospitalar-qa' }
$alvos | ForEach-Object { Stop-Process -Id $_.ProcessId -Force; Write-Host "Parado PID $($_.ProcessId)" }
if (-not $alvos) { Write-Host "Nenhum servidor do Diário na porta $Porta." }
