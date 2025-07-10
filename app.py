#!/usr/bin/env python3
"""Point d'entrée principal de l'application RAG."""

import sys
from pathlib import Path

# Ajouter le dossier racine au path Python
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

from rag_app.main import main

if __name__ == "__main__":
    main()
