#!/usr/bin/env python3
"""Script de configuration automatique du projet RAG."""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python():
    """Vérifie la version de Python."""
    print("🐍 Vérification de Python...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} détecté")
        print("⚠️  Python 3.8+ requis")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def install_requirements():
    """Installe les dépendances."""
    print("\n📦 Installation des dépendances...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True, capture_output=True, text=True)
        print("✅ Dépendances installées")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur installation: {e}")
        return False

def setup_nltk():
    """Configure NLTK."""
    print("\n📚 Configuration de NLTK...")
    
    try:
        import nltk
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        print("✅ NLTK configuré")
        return True
    except Exception as e:
        print(f"❌ Erreur NLTK: {e}")
        return False

def create_env_file():
    """Crée le fichier .env si inexistant."""
    print("\n⚙️  Configuration de l'environnement...")
    
    env_file = Path(".env")
    if not env_file.exists():
        env_content = """# Configuration RAG Assistant
# Clé API Mistral (optionnelle)
MISTRAL_API_KEY=your_mistral_api_key_here

# Configuration de la base vectorielle
VECTOR_DB_PATH=vector_db
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Configuration Streamlit
STREAMLIT_PORT=8501
STREAMLIT_HOST=localhost

# Configuration des logs
LOG_LEVEL=INFO
LOG_FILE=logs/rag_app.log
"""
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("✅ Fichier .env créé")
        print("💡 Éditez .env pour configurer votre clé API Mistral")
    else:
        print("ℹ️  Fichier .env existe déjà")
    
    return True

def create_directories():
    """Crée les répertoires nécessaires."""
    print("\n📁 Création des répertoires...")
    
    directories = [
        "data/processed",
        "data/raw", 
        "logs",
        "vector_db",
        "docs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ {directory}")
    
    return True

def create_gitignore():
    """Crée ou met à jour .gitignore."""
    print("\n🚫 Configuration de .gitignore...")
    
    gitignore_content = """# RAG Assistant - Fichiers à ignorer

# Base vectorielle et données
vector_db/
data/processed/
*.pkl
*.index

# Logs
logs/
*.log

# Configuration privée
.env
*.key

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Streamlit
.streamlit/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Archive (optionnel)
archive/
"""
    
    with open(".gitignore", 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    
    print("✅ .gitignore configuré")
    return True

def test_installation():
    """Teste l'installation."""
    print("\n🧪 Test de l'installation...")
    
    try:
        # Test des imports principaux
        import streamlit
        import nltk
        import pandas
        import numpy
        
        print("✅ Tous les modules importés avec succès")
        
        # Test de l'application
        if Path("app.py").exists():
            print("✅ Point d'entrée app.py trouvé")
        else:
            print("⚠️  Fichier app.py manquant")
            return False
            
        if Path("rag_app").exists():
            print("✅ Module rag_app trouvé")
        else:
            print("⚠️  Dossier rag_app manquant")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False

def main():
    """Fonction principale de configuration."""
    
    print("🚀 CONFIGURATION AUTOMATIQUE RAG ASSISTANT")
    print("="*50)
    
    steps = [
        ("Python", check_python),
        ("Dépendances", install_requirements),
        ("NLTK", setup_nltk),
        ("Environnement", create_env_file),
        ("Répertoires", create_directories),
        ("Git", create_gitignore),
        ("Test", test_installation)
    ]
    
    success_count = 0
    for step_name, step_func in steps:
        if step_func():
            success_count += 1
        else:
            print(f"\n❌ Échec de l'étape: {step_name}")
            break
    
    print(f"\n🎯 CONFIGURATION TERMINÉE")
    print(f"✅ {success_count}/{len(steps)} étapes réussies")
    
    if success_count == len(steps):
        print("\n🎉 Configuration complète réussie !")
        print("🚀 Vous pouvez maintenant lancer: start.bat")
        print("📚 Ou exécuter: python app.py")
    else:
        print("\n⚠️  Configuration incomplète")
        print("🔧 Vérifiez les erreurs ci-dessus")
    
    return success_count == len(steps)

if __name__ == "__main__":
    main()
