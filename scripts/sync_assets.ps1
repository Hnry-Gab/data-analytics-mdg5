# Script de Sincronização Olist Dashboard (Para rodar no Windows)
$IP = "3.14.7.74"
$KEY = "C:\Users\Mauri\AWS\G5.pem"
$REMOTE_PATH = "/home/ubuntu/data-analytics-mdg5/"

Write-Host ">>> Iniciando sincronização de arquivos pesados para $IP..." -ForegroundColor Cyan

# Sincronizar MCP
scp -i $KEY -r olist_mcp ubuntu@${IP}:${REMOTE_PATH}

# Sincronizar Datasets
scp -i $KEY -r dataset ubuntu@${IP}:${REMOTE_PATH}

# Sincronizar Modelos
scp -i $KEY -r models ubuntu@${IP}:${REMOTE_PATH}

Write-Host ">>> Sincronização concluída! ✅" -ForegroundColor Green
pause
