#!/usr/bin/env python3
"""Point d'entrée principal de l'application RAG."""

import sys
import subprocess
from pathlib import Path

# Ajouter le dossier racine au path Python
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

def main():
    """Lance l'application Streamlit."""
    try:
        # Lancer Streamlit avec le module principal
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(ROOT_DIR / "rag_app" / "main.py"),
            "--server.port", "8501",
            "--server.headless", "true"
        ])
    except KeyboardInterrupt:
        print("\n👋 Application fermée par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur lors du lancement: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
