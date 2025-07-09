@echo off
echo ==============================================
echo    Nettoyage Base Vectorielle RAG
echo ==============================================
echo.

echo [INFO] Suppression des fichiers de base vectorielle incompatibles...

if exist "data\docs\vector_db.pkl" (
    del "data\docs\vector_db.pkl"
    echo [OK] Fichier vector_db.pkl supprime
) else (
    echo [INFO] Aucun fichier vector_db.pkl trouve
)

if exist "data\anthropic_docs_v2\summary_indexed_vector_db.pkl" (
    del "data\anthropic_docs_v2\summary_indexed_vector_db.pkl"
    echo [OK] Fichier v2 supprime
) else (
    echo [INFO] Aucun fichier v2 trouve
)

if exist "data\anthropic_docs_v3\summary_indexed_vector_db.pkl" (
    del "data\anthropic_docs_v3\summary_indexed_vector_db.pkl"
    echo [OK] Fichier v3 supprime
) else (
    echo [INFO] Aucun fichier v3 trouve
)

echo.
echo [INFO] Nettoyage termine. Vous pouvez maintenant relancer l'application.
echo [INFO] Une nouvelle base vectorielle sera creee automatiquement.
echo.

pause
