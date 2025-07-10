"""Configuration globale de l'application RAG."""
import os
from pathlib import Path

# Chemins de base
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = DATA_DIR / "models"

# Configuration de la base de données
KNOWLEDGE_BASE_FILE = DATA_DIR / "anthropic_docs.json"
VECTOR_DB_FILE = DATA_DIR / "docs" / "vector_db.pkl"
BACKUP_FILE = DATA_DIR / "anthropic_docs.json.backup"

# Configuration Streamlit
STREAMLIT_CONFIG = {
    "page_title": "RAG Knowledge Base Manager",
    "page_icon": "📚",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Configuration NLP
NLTK_RESOURCES = [
    'punkt', 'punkt_tab', 'stopwords', 'wordnet', 'omw-1.4'
]

# Configuration Vision
VISION_CONFIG = {
    "model_name": "Salesforce/blip-image-captioning-base",
    "max_image_size": 10 * 1024 * 1024,  # 10MB
    "supported_formats": ['.png', '.jpg', '.jpeg', '.pdf', '.txt']
}

# Configuration de traitement
PROCESSING_CONFIG = {
    "max_chunk_size": 500,
    "chunk_overlap": 50,
    "max_file_size_mb": 100
}
