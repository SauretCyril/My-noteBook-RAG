"""Application principale RAG avec architecture modulaire."""

import streamlit as st
import sys
from pathlib import Path

# Configuration de Streamlit
st.set_page_config(
    page_title="RAG Knowledge Base Manager",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import des modules internes
from .config.settings import STREAMLIT_CONFIG
from .core.vector_database import VectorDatabase
from .ui.components.sidebar import Sidebar
from .ui.pages import (
    home, database_management, batch_processing, 
    search, gallery
)

def main():
    """Point d'entrée principal de l'application."""
    
    # Titre principal
    st.title("🤖 RAG Knowledge Base Manager - Version Professionnelle")
    st.markdown("---")
    
    # Configuration des pages disponibles
    pages = [
        {"id": "home", "label": "🏠 Accueil"},
        {"id": "database", "label": "🗃️ Gestion de la Base"},
        {"id": "batch", "label": "📁 Traitement par Lots"},
        {"id": "search", "label": "🔍 Recherche Avancée"},
        {"id": "gallery", "label": "🖼️ Galerie d'Images"}
    ]
    
    # Initialisation de la session
    initialize_session()
    
    # Sidebar avec navigation et statistiques
    current_page = Sidebar.render_navigation(pages)
    
    # Affichage des statistiques dans la sidebar
    if 'vector_db' in st.session_state:
        stats = st.session_state.vector_db.get_stats()
        Sidebar.render_stats(stats)
    
    # Navigation vers les pages
    if current_page == "home":
        home.show()
    elif current_page == "database":
        database_management.show()
    elif current_page == "batch":
        batch_processing.show()
    elif current_page == "search":
        search.show()
    elif current_page == "gallery":
        gallery.show()

def initialize_session():
    """Initialise les variables de session."""
    
    # Chargement de la base vectorielle
    if 'vector_db' not in st.session_state:
        st.session_state.vector_db = VectorDatabase.load()
    
    # Initialisation de l'historique des conversations
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Initialisation des paramètres utilisateur
    if 'user_settings' not in st.session_state:
        st.session_state.user_settings = {
            'theme': 'light',
            'language': 'fr',
            'max_results': 10
        }

if __name__ == "__main__":
    main()
