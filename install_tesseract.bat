@echo off
echo ==============================================
echo    Installation Tesseract OCR
echo ==============================================
echo.

echo [INFO] Installation automatique de Tesseract OCR...
echo [INFO] Tesseract est necessaire pour l'OCR (extraction de texte des images)
echo.

echo [1/2] Tentative d'installation via winget...
winget install UB-Mannheim.TesseractOCR

if %errorlevel% neq 0 (
    echo [WARN] Winget non disponible ou echec d'installation
    echo [INFO] Installation manuelle requise :
    echo.
    echo 1. Allez sur : https://github.com/UB-Mannheim/tesseract/wiki
    echo 2. Telechargez la derniere version pour Windows
    echo 3. Installez avec les parametres par defaut
    echo 4. Ajoutez le chemin d'installation au PATH si necessaire
    echo    Chemin typique : C:\Program Files\Tesseract-OCR
    echo.
    echo [INFO] Ou utilisez chocolatey :
    echo choco install tesseract
    echo.
) else (
    echo [OK] Tesseract installe avec succes via winget
)

echo [2/2] Test de l'installation...
python -c "import pytesseract; print('Tesseract detecte et fonctionnel')" 2>nul || (
    echo [WARN] Tesseract non detecte par Python
    echo [INFO] Vous devrez peut-etre configurer le chemin dans le code :
    echo pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
)

echo.
echo [INFO] Installation terminee. Vous pouvez maintenant lancer l'application vision.
echo.

pause
