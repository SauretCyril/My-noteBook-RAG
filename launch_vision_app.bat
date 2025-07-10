@echo off
echo ==============================================
echo    RAG Knowledge Base Manager + Vision
echo ==============================================
echo.

echo [INFO] Installation de Tesseract OCR necessaire pour l'analyse d'images
echo [INFO] Telecharger depuis: https://github.com/UB-Mannheim/tesseract/wiki
echo [INFO] Ou installer via: winget install UB-Mannheim.TesseractOCR
echo.

echo [1/4] Verification des dependances Python pour la vision...
python -m pip install -r requirements_vision.txt --quiet

echo [2/4] Verification des donnees NLTK...
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True)" 2>nul

echo [3/4] Verification de Tesseract OCR...
python -c "import pytesseract; print('Tesseract OK')" 2>nul || echo [WARN] Tesseract non detecte - OCR limite

echo [4/4] Lancement de l'application Vision + Batch...
echo.
echo Interface disponible sur : http://localhost:8501
echo Fonctionnalites:
echo - Upload et analyse d'images PNG/JPG
echo - OCR automatique (extraction de texte)
echo - Description automatique du contenu
echo - Classification par categories
echo - Recherche multimodale
echo - TRAITEMENT PAR LOTS RECURSIF
echo - Support des fichiers ._annonce_.data
echo - Recherche avancee par categories/projets
echo.
echo Appuyez sur Ctrl+C pour arreter l'application
echo.

streamlit run rag_batch_app.py --server.port 8501 --server.address localhost

pause
