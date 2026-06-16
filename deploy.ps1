#Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

if (-not (Test-Path ".env")) {
    Write-Host "Creating .env from defaults — set OPENROUTER_API_KEY for AI features."
    @"
OPENROUTER_API_KEY=
POSTGRES_PASSWORD=apidebug
FRONTEND_PORT=80
PUBLIC_URL=http://localhost
LLM_MODEL=openai/gpt-4o-mini
EMBEDDING_MODEL=openai/text-embedding-3-small
"@ | Set-Content -Path ".env" -Encoding UTF8
}

Write-Host "Building and starting production stack..."
docker compose -f docker-compose.prod.yml up --build -d

$port = if ($env:FRONTEND_PORT) { $env:FRONTEND_PORT } else { "80" }
Write-Host ""
Write-Host "Production deploy complete."
Write-Host "  App:    http://localhost:$port"
Write-Host "  API:    http://localhost:$port/api/analytics"
Write-Host "  Health: http://localhost:$port/health"
