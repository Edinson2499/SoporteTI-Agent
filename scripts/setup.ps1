<#
.SYNOPSIS
    Prepara el entorno local de SoporteTI-Agent en cualquier equipo Windows.
.DESCRIPTION
    Crea el entorno virtual, instala dependencias, genera el .env local
    (si no existe) y ejecuta las pruebas para validar la instalacion.
.EXAMPLE
    .\scripts\setup.ps1
#>

param(
    [switch]$SkipTests
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

Write-Host "== SoporteTI-Agent: configuracion de entorno ==" -ForegroundColor Cyan

# 1. Verificar Python disponible
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    throw "No se encontro 'python' en el PATH. Instala Python 3.11+ antes de continuar."
}
Write-Host "Python detectado: $($python.Source)" -ForegroundColor DarkGray

# 2. Crear entorno virtual si no existe
if (-not (Test-Path ".venv")) {
    Write-Host "Creando entorno virtual (.venv)..." -ForegroundColor Yellow
    python -m venv .venv
} else {
    Write-Host "Entorno virtual (.venv) ya existe, se reutiliza." -ForegroundColor DarkGray
}

# 3. Activar entorno virtual
Write-Host "Activando entorno virtual..." -ForegroundColor Yellow
. .\.venv\Scripts\Activate.ps1

# 4. Instalar dependencias
Write-Host "Instalando dependencias desde requirements.txt..." -ForegroundColor Yellow
python -m pip install --upgrade pip
pip install -r requirements.txt

# 5. Crear .env local a partir del ejemplo si no existe
if (-not (Test-Path ".env") -and (Test-Path ".env.example")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Se genero .env a partir de .env.example. Revisa y completa los valores." -ForegroundColor Yellow
} else {
    Write-Host ".env ya existe o no hay .env.example, no se sobrescribe." -ForegroundColor DarkGray
}

# 6. Ejecutar pruebas para validar la instalacion
if (-not $SkipTests) {
    Write-Host "Ejecutando pruebas (pytest)..." -ForegroundColor Yellow
    python -m pytest tests/ -v
} else {
    Write-Host "Pruebas omitidas (-SkipTests)." -ForegroundColor DarkGray
}

Write-Host "`n== Entorno listo ==" -ForegroundColor Green
Write-Host "Para iniciar la API ejecuta: .\scripts\start.ps1" -ForegroundColor Green
