# Script para criar a estrutura de pastas
$folders = @(
    "pesquisa_satisfacao",
    "pesquisa_satisfacao\static",
    "pesquisa_satisfacao\static\css",
    "pesquisa_satisfacao\static\js",
    "pesquisa_satisfacao\templates"
)

foreach ($folder in $folders) {
    New-Item -ItemType Directory -Path $folder -Force
}

# Criar arquivos
New-Item -ItemType File -Path "pesquisa_satisfacao\app.py" -Force
New-Item -ItemType File -Path "pesquisa_satisfacao\pesquisa.ps1" -Force
New-Item -ItemType File -Path "pesquisa_satisfacao\static\css\styles.css" -Force
New-Item -ItemType File -Path "pesquisa_satisfacao\static\js\script.js" -Force
New-Item -ItemType File -Path "pesquisa_satisfacao\templates\formulario.html" -Force
New-Item -ItemType File -Path "pesquisa_satisfacao\templates\success.html" -Force