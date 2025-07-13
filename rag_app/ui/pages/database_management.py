"""Page de gestion de la base de données."""

import streamlit as st
import pandas as pd
from typing import Dict, Any

def show() -> None:
    """Affiche la page de gestion de la base de données."""
    
    st.header("🗃️ Gestion de la Base Vectorielle")
    
    if 'vector_db' not in st.session_state:
        st.error("⚠️ Base vectorielle non initialisée")
        return
        
    vector_db = st.session_state.vector_db
    stats = vector_db.get_stats()
    
    # Statistiques détaillées
    _show_detailed_stats(stats)
    
    # Actions de gestion
    _show_management_actions(vector_db)
    
    # Liste des documents
    if vector_db.documents:
        _show_documents_list(vector_db)
    else:
        _show_empty_state()

def _show_detailed_stats(stats: Dict[str, Any]) -> None:
    """Affiche les statistiques détaillées."""
    
    st.markdown("### 📊 Statistiques Détaillées")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"📄 Documents : {stats['total_documents']}")
        st.info(f"🖼️ Images : {stats['total_images']}")
        
    with col2:
        st.info(f"🏷️ Catégories : {stats['categories']}")
        st.info(f"📋 Projets : {stats['projects']}")
        
    with col3:
        st.info(f"📝 Caractères : {stats['total_characters']:,}")
        status = "✅ Active" if stats['has_vectors'] else "❌ Non initialisée"
        st.info(f"🔢 Base vectorielle : {status}")

def _show_management_actions(vector_db) -> None:
    """Affiche les actions de gestion."""
    
    st.markdown("### ⚙️ Actions de Gestion")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🆕 Nouvelle Base", type="primary"):
            if st.session_state.get('confirm_new_db', False):
                from ...core.vector_database import VectorDatabase
                st.session_state.vector_db = VectorDatabase()
                st.session_state.confirm_new_db = False
                st.success("✅ Nouvelle base créée !")
                st.rerun()
            else:
                st.session_state.confirm_new_db = True
                st.warning("⚠️ Cliquez à nouveau pour confirmer")
                
    with col2:
        if st.button("💾 Sauvegarder"):
            vector_db.save()
            st.success("✅ Base sauvegardée !")
            
    with col3:
        if st.button("🔄 Recharger"):
            from ...core.vector_database import VectorDatabase
            st.session_state.vector_db = VectorDatabase.load()
            st.success("✅ Base rechargée !")
            st.rerun()
            
    with col4:
        if st.button("🗑️ Vider Base"):
            if st.session_state.get('confirm_clear', False):
                vector_db.clear()
                st.session_state.confirm_clear = False
                st.success("✅ Base vidée !")
                st.rerun()
            else:
                st.session_state.confirm_clear = True
                st.warning("⚠️ Cliquez à nouveau pour confirmer")

def _show_documents_list(vector_db) -> None:
    """Affiche la liste des documents."""
    
    st.markdown("### 📚 Documents dans la Base")
    
    # Filtres
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_category = st.selectbox(
            "Filtrer par catégorie",
            ["Toutes"] + vector_db.get_categories(),
            key="filter_category"
        )
        
    with col2:
        filter_project = st.selectbox(
            "Filtrer par projet",
            ["Tous"] + vector_db.get_projects(),
            key="filter_project"
        )
        
    with col3:
        search_term = st.text_input("Rechercher dans le titre/contenu", key="search_term")
    
    # Filtrer les documents
    filtered_docs = vector_db.documents.copy()
    
    if filter_category != "Toutes":
        filtered_docs = [
            doc for doc in filtered_docs 
            if doc.get('metadata', {}).get('category') == filter_category
        ]
        
    if filter_project != "Tous":
        filtered_docs = [
            doc for doc in filtered_docs
            if doc.get('metadata', {}).get('project') == filter_project
        ]
        
    if search_term:
        search_lower = search_term.lower()
        filtered_docs = [
            doc for doc in filtered_docs
            if search_lower in doc.get('text', '').lower() or
               search_lower in doc.get('metadata', {}).get('title', '').lower()
        ]
    
    st.write(f"📄 Affichage de {len(filtered_docs)} document(s)")
    
    # Affichage paginé
    page_size = 10
    total_pages = (len(filtered_docs) + page_size - 1) // page_size
    
    if total_pages > 1:
        page = st.selectbox(
            "Page",
            range(1, total_pages + 1),
            format_func=lambda x: f"Page {x}/{total_pages}",
            key="page_selector"
        )
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        filtered_docs = filtered_docs[start_idx:end_idx]
    
    # Afficher les documents
    for i, doc in enumerate(filtered_docs):
        with st.expander(f"📄 Document {i+1} - {doc.get('metadata', {}).get('title', 'Sans titre')}"):
            
            # Métadonnées
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**📁 Source:** {doc.get('metadata', {}).get('source', 'N/A')}")
                st.markdown(f"**🏷️ Catégorie:** {doc.get('metadata', {}).get('category', 'N/A')}")
                st.markdown(f"**👤 Auteur:** {doc.get('metadata', {}).get('author', 'N/A')}")
                
            with col2:
                st.markdown(f"**📋 Projet:** {doc.get('metadata', {}).get('project', 'N/A')}")
                st.markdown(f"**📅 Date:** {doc.get('timestamp', 'N/A')[:10]}")
                st.markdown(f"**📝 Taille:** {len(doc.get('text', ''))} caractères")
            
            # Contenu
            text = doc.get('text', '')
            if len(text) > 500:
                st.text_area("Contenu (aperçu):", text[:500] + "...", height=100, key=f"preview_{i}")
                if st.button(f"Voir le contenu complet {i}", key=f"full_content_{i}"):
                    st.text_area("Contenu complet:", text, height=300, key=f"full_{i}")
            else:
                st.text_area("Contenu:", text, height=100, key=f"content_{i}")
            
            # Actions sur le document
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"🗑️ Supprimer", key=f"delete_{i}"):
                    if st.session_state.get(f'confirm_delete_{i}', False):
                        # Trouver l'index réel dans la base
                        real_index = vector_db.documents.index(doc)
                        vector_db.remove_document(real_index)
                        st.success("Document supprimé !")
                        st.rerun()
                    else:
                        st.session_state[f'confirm_delete_{i}'] = True
                        st.warning("Cliquez à nouveau pour confirmer")

def _show_empty_state() -> None:
    """Affiche l'état vide de la base."""
    
    st.info("📭 Aucun document dans la base")
    
    st.markdown("""
    ### 🚀 Pour commencer, vous pouvez :
    
    1. **📄 Ajouter des documents individuels** via l'upload
    2. **📁 Traiter un dossier complet** avec le traitement par lots
    3. **🔄 Recharger** une base existante
    """)
    
    # Boutons d'action
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📁 Traitement par Lots", type="primary"):
            st.session_state.page_redirect = "batch"
            st.rerun()
            
    with col2:
        if st.button("📄 Upload de Documents"):
            # TODO: Ajouter une interface d'upload direct
            st.info("Interface d'upload à implémenter")
