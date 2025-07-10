@echo off
echo ==============================================
echo    RAG Knowledge Base Manager v2.0
echo    Architecture Professionnelle
echo ==============================================
echo.

echo [INFO] Nouvelle version avec architecture modulaire
echo [INFO] Base vectorielle compatible avec les anciennes donnees
echo [INFO] Interface utilisateur refactorisee
echo.

echo [1/3] Verification des dependances Python...
python -m pip install -r requirements/base.txt --quiet

echo [2/3] Verification des donnees NLTK...
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True)" 2>nul

echo [3/3] Lancement de l'application v2.0...
echo.
echo Interface disponible sur : http://localhost:8503
echo.
echo === NOUVELLES FONCTIONNALITES v2.0 ===
echo [✓] Architecture modulaire et maintenable
echo [✓] Configuration centralisee
echo [✓] Composants UI reutilisables
echo [✓] Structure prete pour les tests
echo [✓] Point d'entree unique
echo.
echo === FONCTIONNALITES PRINCIPALES ===
echo [🏠] Accueil = Tableau de bord et statistiques
echo [🗃️] Gestion Base = Administration de la base vectorielle
echo [📁] Traitement Lots = Fonctionnalite heritage (en migration)
echo [🔍] Recherche = Interface de recherche avancee
echo [🖼️] Galerie = Visualisation des images indexees
echo.
echo Appuyez sur Ctrl+C pour arreter l'application
echo.

streamlit run app.py --server.port 8503 --server.address localhost

pause
