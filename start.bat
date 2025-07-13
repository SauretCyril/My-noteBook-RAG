@echo off
chcp 65001 >nul
title RAG Knowledge Assistant - Startup
color 0A

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                RAG KNOWLEDGE ASSISTANT                       ║
echo ║                    Lancement simplifie                       ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo [1/4] Verification de l'environnement Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python n'est pas installe ou non accessible.
    echo 💡 Installez Python depuis https://python.org
    pause
    exit /b 1
)
echo ✅ Python detecte

echo.
echo [2/4] Installation des dependances...
python -m pip install -r requirements.txt --quiet --disable-pip-version-check
if %errorlevel% neq 0 (
    echo ❌ Erreur lors de l'installation des dependances
    echo 💡 Verifiez votre connexion internet et requirements.txt
    pause
    exit /b 1
)
echo ✅ Dependances installees

echo.
echo [3/4] Preparation de l'application...
:: Nettoyage du cache Python
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul

:: Verification de la structure
if not exist "rag_app" (
    echo ❌ Structure d'application manquante
    echo 💡 Verifiez que le dossier rag_app/ existe
    pause
    exit /b 1
)
echo ✅ Structure validee

echo.
echo [4/4] Demarrage de l'application RAG...
echo.
echo 🚀 Ouverture de l'interface web...
echo 📱 URL locale: http://localhost:8501
echo 🌐 URL reseau: http://192.168.1.75:8501
echo.
echo ⚠️  Pour arreter l'application: Ctrl+C
echo.

:: Lancement de l'application
python app.py

echo.
echo 👋 Application fermee. Merci d'avoir utilise RAG Assistant !
pause
