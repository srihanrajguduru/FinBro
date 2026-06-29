# FinBro local backend dev (Windows PowerShell)
# Starts PostgreSQL in Docker, runs migrations, then the API with reload.

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$ServerDir = Join-Path $RepoRoot "server"
$ComposeFile = Join-Path $RepoRoot "docker-compose.yml"

function Test-DockerReady {
    $prev = $ErrorActionPreference
    $ErrorActionPreference = "SilentlyContinue"
    & docker info 1>$null 2>$null
    $ready = $LASTEXITCODE -eq 0
    $ErrorActionPreference = $prev
    return $ready
}

function Wait-PostgresHealthy {
    param([int]$TimeoutSeconds = 120)
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    Write-Host "Waiting for PostgreSQL to accept connections..."
    while ((Get-Date) -lt $deadline) {
        & docker compose -f $ComposeFile exec -T postgres pg_isready -U finbro -d finbro 1>$null 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "PostgreSQL is ready."
            return
        }
        Start-Sleep -Seconds 2
    }
    throw "PostgreSQL did not become ready within ${TimeoutSeconds}s. Check: docker compose -f `"$ComposeFile`" logs postgres"
}

if (-not (Test-Path (Join-Path $ServerDir ".env"))) {
    Copy-Item (Join-Path $ServerDir ".env.example") (Join-Path $ServerDir ".env")
    Write-Host "Created server/.env from .env.example"
}

if (-not (Test-DockerReady)) {
    Write-Host @"

Docker Desktop is not running (daemon unreachable).

Start Docker Desktop, then run this script again.

Manual steps from repo root:
  docker compose up postgres -d
  cd server
  alembic upgrade head
  uvicorn app.main:app --reload --port 8000

"@ -ForegroundColor Yellow
    exit 1
}

Push-Location $RepoRoot
try {
    Write-Host "Starting PostgreSQL (docker compose)..."
    docker compose -f $ComposeFile up postgres -d
    if ($LASTEXITCODE -ne 0) { throw "docker compose up failed" }

    Wait-PostgresHealthy

    Push-Location $ServerDir
    try {
        Write-Host "Running database migrations..."
        alembic upgrade head
        if ($LASTEXITCODE -ne 0) { throw "alembic upgrade head failed" }

        Write-Host "Starting API at http://localhost:8000 ..."
        uvicorn app.main:app --reload --port 8000
    } finally {
        Pop-Location
    }
} finally {
    Pop-Location
}
