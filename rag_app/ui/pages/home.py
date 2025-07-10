"""Page d'accueil de l'application RAG."""

import streamlit as st
from typing import Dict, Any

def show() -> None:
    """Affiche la page d'accueil avec les statistiques et guides."""
    
    st.header("🏠 Tableau de Bord")
    
    # Vérification de la base vectorielle
    if 'vector_db' not in st.session_state:
        st.error("⚠️ Base vectorielle non initialisée")
        return
        
    vector_db = st.session_state.vector_db
    stats = vector_db.get_stats()
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📚 Documents", stats['total_documents'])
        
    with col2:
        st.metric("🖼️ Images", stats['total_images'])
        
    with col3:
        st.metric("🏷️ Catégories", stats['categories'])
        
    with col4:
        st.metric("📋 Projets", stats['projects'])
    
    # Détails supplémentaires
    if stats['total_documents'] > 0:
        
        # Graphique de répartition des catégories
        if stats['categories_list']:
            st.markdown("### 🏷️ Répartition par Catégories")
            _show_categories_chart(vector_db, stats['categories_list'])
            
        # Graphique de répartition des projets
        if stats['projects_list']:
            st.markdown("### 📋 Répartition par Projets")
            _show_projects_chart(vector_db, stats['projects_list'])
            
        # Activité récente
        st.markdown("### 📈 Activité Récente")
        _show_recent_activity(vector_db)
        
    else:
        # Guide de démarrage si aucun document
        _show_getting_started_guide()

def _show_categories_chart(vector_db, categories: list) -> None:
    """Affiche un graphique des catégories."""
    import pandas as pd
    
    # Compter les documents par catégorie
    category_counts = {}
    for doc in vector_db.documents:
        category = doc.get('metadata', {}).get('category', 'Non classé')
        category_counts[category] = category_counts.get(category, 0) + 1
    
    if category_counts:
        df = pd.DataFrame(
            list(category_counts.items()),
            columns=['Catégorie', 'Nombre de documents']
        )
        st.bar_chart(df.set_index('Catégorie'))

def _show_projects_chart(vector_db, projects: list) -> None:
    """Affiche un graphique des projets."""
    import pandas as pd
    
    # Compter les documents par projet
    project_counts = {}
    for doc in vector_db.documents:
        project = doc.get('metadata', {}).get('project', 'Non assigné')
        project_counts[project] = project_counts.get(project, 0) + 1
    
    if project_counts:
        df = pd.DataFrame(
            list(project_counts.items()),
            columns=['Projet', 'Nombre de documents']
        )
        st.bar_chart(df.set_index('Projet'))

def _show_recent_activity(vector_db) -> None:
    """Affiche l'activité récente."""
    
    # Trier les documents par timestamp
    recent_docs = sorted(
        vector_db.documents, 
        key=lambda x: x.get('timestamp', ''), 
        reverse=True
    )[:5]
    
    if recent_docs:
        for i, doc in enumerate(recent_docs):
            with st.expander(f"📄 Document {i+1} - {doc.get('metadata', {}).get('title', 'Sans titre')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**📁 Source:** {doc.get('metadata', {}).get('source', 'N/A')}")
                    st.markdown(f"**🏷️ Catégorie:** {doc.get('metadata', {}).get('category', 'N/A')}")
                    
                with col2:
                    st.markdown(f"**📋 Projet:** {doc.get('metadata', {}).get('project', 'N/A')}")
                    st.markdown(f"**📅 Date:** {doc.get('timestamp', 'N/A')[:10]}")
                
                # Aperçu du contenu
                text_preview = doc.get('text', '')[:200] + "..." if len(doc.get('text', '')) > 200 else doc.get('text', '')
                st.markdown(f"**📝 Aperçu:** {text_preview}")
    else:
        st.info("Aucune activité récente")

def _show_getting_started_guide() -> None:
    """Affiche le guide de démarrage pour les nouveaux utilisateurs."""
    
    st.markdown("### 🚀 Guide de Démarrage")
    
    st.markdown("""
    Bienvenue dans votre système RAG professionnel ! Pour commencer :
    
    #### 📚 Étape 1 : Ajouter des Documents
    - Utilisez **"🗃️ Gestion de la Base"** pour configurer votre base
    - Ou allez dans **"📁 Traitement par Lots"** pour traiter un dossier entier
    
    #### 🔍 Étape 2 : Explorer vos Données
    - **"🔍 Recherche Avancée"** pour rechercher dans vos documents
    - **"🖼️ Galerie d'Images"** pour visualiser les images indexées
    
    #### 💬 Étape 3 : Poser des Questions
    - Une fois vos documents ajoutés, vous pourrez les interroger
    - Le système trouvera automatiquement les informations pertinentes
    """)
    
    # Boutons d'action rapide
    st.markdown("### ⚡ Actions Rapides")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Ajouter un Document", type="primary"):
            st.session_state.page_redirect = "database"
            st.rerun()
            
    with col2:
        if st.button("📁 Traitement par Lots"):
            st.session_state.page_redirect = "batch"
            st.rerun()
            
    with col3:
        if st.button("🔍 Rechercher"):
            st.session_state.page_redirect = "search"
            st.rerun()
    
    # Informations sur la version
    st.markdown("---")
    with st.expander("ℹ️ Informations sur cette Version"):
        st.markdown("""
        **Version 2.0 - Architecture Professionnelle**
        
        ✨ **Nouveautés :**
        - Architecture modulaire et maintenable
        - Composants UI réutilisables
        - Configuration centralisée
        - Structure prête pour les tests
        
        🏗️ **Architecture :**
        - Core : Logique métier
        - Services : Services applicatifs
        - UI : Interface utilisateur modulaire
        - Utils : Utilitaires partagés
        
        📦 **Compatibilité :**
        - Les données existantes sont préservées
        - Migration automatique des anciennes bases
        """)
