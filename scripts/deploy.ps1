<#
.SYNOPSIS
    Construye y despliega SoporteTI-Agent en AWS con AWS SAM.
.EXAMPLE
    .\scripts\deploy.ps1 -StackName soporte-ti-agent-dev -Region eu-west-1
#>

param(
    [string]$StackName = "soporte-ti-agent-dev",
    [string]$Region = "us-east-1"
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

if (-not (Get-Command sam -ErrorAction SilentlyContinue)) {
    throw "No se encontro AWS SAM CLI. Instalalo antes de desplegar."
}
if (-not (Get-Command aws -ErrorAction SilentlyContinue)) {
    throw "No se encontro AWS CLI. Instalalo y configura 'aws configure' antes de desplegar."
}

Write-Host "Construyendo la funcion Lambda..." -ForegroundColor Yellow
sam build --template-file template.yaml

Write-Host "Desplegando $StackName en $Region..." -ForegroundColor Yellow
sam deploy `
    --template-file .aws-sam\build\template.yaml `
    --stack-name $StackName `
    --region $Region `
    --capabilities CAPABILITY_IAM `
    --resolve-s3 `
    --no-confirm-changeset `
    --no-fail-on-empty-changeset

Write-Host "Despliegue finalizado. URL de la API:" -ForegroundColor Green
aws cloudformation describe-stacks `
    --stack-name $StackName `
    --region $Region `
    --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" `
    --output text