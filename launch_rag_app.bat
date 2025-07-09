@echo off
echo ==============================================
echo    RAG Knowledge Base Manager
echo ==============================================
echo.

echo [1/3] Verification des dependances Python...
python -m pip install -r requirements.txt --quiet

echo [2/3] Verification des donnees NLTK...
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True)" 2>nul

echo [3/3] Lancement de l'application...
echo.
echo Interface disponible sur : http://localhost:8501
echo Appuyez sur Ctrl+C pour arreter l'application
echo.

streamlit run rag_interface_app.py --server.port 8501 --server.address localhost

pause
