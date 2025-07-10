"""Composant sidebar réutilisable."""

import streamlit as st
from typing import List, Dict, Any

class Sidebar:
    """Composant de navigation latérale."""
    
    @staticmethod
    def render_navigation(pages: List[Dict[str, str]]) -> str:
        """Affiche le menu de navigation."""
        st.sidebar.title("📋 Menu Principal")
        
        page_options = [page['label'] for page in pages]
        selected = st.sidebar.selectbox(
            "Choisissez une action :",
            page_options
        )
        
        # Retourner l'ID de la page sélectionnée
        for page in pages:
            if page['label'] == selected:
                return page['id']
                
        return pages[0]['id']  # Page par défaut
        
    @staticmethod 
    def render_stats(stats: Dict[str, Any]) -> None:
        """Affiche les statistiques dans la sidebar."""
        st.sidebar.markdown("### 📊 Statistiques")
        
        if stats.get('total_documents', 0) > 0:
            st.sidebar.metric(
                "📚 Documents", 
                stats['total_documents']
            )
            
        if stats.get('total_images', 0) > 0:
            st.sidebar.metric(
                "🖼️ Images",
                stats['total_images']
            )
            
        if stats.get('categories', 0) > 0:
            st.sidebar.metric(
                "🏷️ Catégories",
                stats['categories'] 
            )
            
        if stats.get('projects', 0) > 0:
            st.sidebar.metric(
                "📋 Projets",
                stats['projects']
            )
            
        # Affichage du statut de la base
        if stats.get('has_vectors', False):
            st.sidebar.success("✅ Base vectorielle active")
        else:
            st.sidebar.warning("⚠️ Base vectorielle non initialisée")
            
    @staticmethod
    def render_quick_actions() -> None:
        """Affiche les actions rapides dans la sidebar."""
        st.sidebar.markdown("### ⚡ Actions Rapides")
        
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            if st.button("💾", help="Sauvegarder"):
                if 'vector_db' in st.session_state:
                    st.session_state.vector_db.save()
                    st.sidebar.success("✅ Sauvegardé")
                    
        with col2:
            if st.button("🔄", help="Recharger"):
                if 'vector_db' in st.session_state:
                    from ..core.vector_database import VectorDatabase
                    st.session_state.vector_db = VectorDatabase.load()
                    st.sidebar.success("✅ Rechargé")
                    st.rerun()
                    
    @staticmethod
    def render_settings() -> None:
        """Affiche les paramètres utilisateur."""
        with st.sidebar.expander("⚙️ Paramètres"):
            
            # Thème
            theme = st.selectbox(
                "Thème",
                ["light", "dark"],
                index=0 if st.session_state.get('user_settings', {}).get('theme') == 'light' else 1
            )
            
            # Langue
            language = st.selectbox(
                "Langue",
                ["fr", "en"],
                index=0 if st.session_state.get('user_settings', {}).get('language') == 'fr' else 1
            )
            
            # Nombre de résultats par défaut
            max_results = st.slider(
                "Résultats max",
                1, 20, 
                st.session_state.get('user_settings', {}).get('max_results', 10)
            )
            
            # Sauvegarder les paramètres
            if 'user_settings' not in st.session_state:
                st.session_state.user_settings = {}
                
            st.session_state.user_settings.update({
                'theme': theme,
                'language': language,
                'max_results': max_results
            })
