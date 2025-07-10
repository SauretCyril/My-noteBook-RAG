@echo off
echo ==============================================
echo    RAG Batch Processing - Traitement Recursif
echo ==============================================
echo.

echo [INFO] Application specialisee pour le traitement par lots
echo [INFO] Traite les repertoires entiers de facon recursive
echo [INFO] Supporte les fichiers ._annonce_.data pour la contextualisation
echo.

echo [1/3] Verification des dependances Python...
python -m pip install -r requirements.txt --quiet

echo [2/3] Verification des donnees NLTK...
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True)" 2>nul

echo [3/3] Lancement de l'application Batch...
echo.
echo Interface disponible sur : http://localhost:8502
echo.
echo === FONCTIONNALITES PRINCIPALES ===
echo [✓] Traitement recursif de repertoires entiers
echo [✓] Support des fichiers ._annonce_.data
echo [✓] Types supportes: PDF, TXT, PNG, JPG, JPEG
echo [✓] Metadonnees automatiques (categories, projets, auteurs)
echo [✓] Recherche avancee avec filtres
echo [✓] Barre de progression temps reel
echo [✓] Rapport detaille des resultats
echo.
echo === MENU PRINCIPAL ===
echo [📁] Traitement par Lots = FONCTION PRINCIPALE
echo [🔍] Recherche Avancee = Filtrage par categories/projets
echo [❓] Poser Questions = Chat intelligent
echo [🏠] Accueil = Statistiques et tableau de bord
echo.
echo Appuyez sur Ctrl+C pour arreter l'application
echo.

streamlit run rag_batch_app.py --server.port 8502 --server.address localhost

pause
