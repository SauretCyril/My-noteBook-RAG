@echo off
echo 🔧 Installation des ressources NLTK...
echo.

REM Activer l'environnement virtuel s'il existe
if exist ".venv\Scripts\activate.bat" (
    echo 📦 Activation de l'environnement virtuel...
    call .venv\Scripts\activate.bat
)

echo 📥 Téléchargement des ressources NLTK nécessaires...
python -c "import nltk; import ssl; ssl._create_default_https_context = ssl._create_unverified_context; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('omw-1.4'); print('✅ Installation terminée !')"

echo.
echo 🧪 Test de vérification...
python -c "from nltk.tokenize import sent_tokenize; print('✅ NLTK fonctionne correctement !')"

echo.
echo 🎉 Configuration NLTK terminée !
pause
