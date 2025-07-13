"""Page de visualisation des projets et catégories."""

import streamlit as st
from typing import Dict, List, Set
import os

from ...services.batch_service import BatchService
from ..components.debug_panel import show_debug_panel

def show() -> None:
    """Affiche la page de projets et catégories."""
    
    st.header("📂 Projets et Catégories RAG")
    
    # Vérification de la base vectorielle
    if 'vector_db' not in st.session_state:
        st.error("⚠️ Base vectorielle non initialisée")
        st.info("Retournez à l'accueil pour initialiser la base de données.")
        return
        
    vector_db = st.session_state.vector_db
    batch_service = BatchService(vector_db)
    
    # Description de la page
    st.markdown("""
    Cette page vous permet de visualiser l'organisation de votre base RAG par **projets** et **catégories**.
    
    🎯 **Projets** : Issus des fichiers `.data.json` (un fichier = un projet)
    🏷️ **Catégories** : Classifications automatiques et manuelles des documents
    """)
    
    # Analyser la base
    projects_data, categories_data, stats = _analyze_database(vector_db)
    
    # Affichage des statistiques générales
    _show_general_stats(stats)
    
    # Interface à onglets
    tab1, tab2, tab3 = st.tabs(["📂 Projets", "🏷️ Catégories", "📊 Analyse"])
    
    with tab1:
        _show_projects_view(projects_data, vector_db)
    
    with tab2:
        _show_categories_view(categories_data, vector_db)
    
    with tab3:
        _show_analysis_view(projects_data, categories_data, stats, vector_db)
    
    # Panneau de debug
    show_debug_panel("projects_categories")

def _analyze_database(vector_db) -> tuple:
    """Analyse la base vectorielle pour extraire projets et catégories."""
    
    if not hasattr(vector_db, 'documents') or not vector_db.documents:
        return {}, {}, {'total_docs': 0, 'data_json_projects': 0, 'unique_projects': 0, 'unique_categories': 0}
    
    projects = {}
    categories = {}
    stats = {
        'total_docs': len(vector_db.documents),
        'data_json_projects': 0,
        'unique_projects': 0,
        'unique_categories': 0,
        'docs_with_projects': 0,
        'docs_with_categories': 0
    }
    
    # Analyser chaque document
    for doc in vector_db.documents:
        metadata = doc.get('metadata', {})
        
        # Statistiques .data.json
        if metadata.get('source_format') == 'data_json':
            stats['data_json_projects'] += 1
        
        # Analyser les projets
        project = metadata.get('project', 'Non spécifié')
        if project and project != 'Projet par défaut':
            stats['docs_with_projects'] += 1
            
        if project not in projects:
            projects[project] = {
                'count': 0,
                'categories': set(),
                'sources': set(),
                'authors': set(),
                'dates': set(),
                'data_json_count': 0,
                'documents': []
            }
        
        projects[project]['count'] += 1
        projects[project]['sources'].add(metadata.get('source', '').split('\\')[-2] if '\\' in metadata.get('source', '') else 'Racine')
        projects[project]['authors'].add(metadata.get('author', 'Inconnu'))
        projects[project]['dates'].add(metadata.get('date', ''))
        projects[project]['documents'].append(doc)
        
        if metadata.get('source_format') == 'data_json':
            projects[project]['data_json_count'] += 1
        
        # Analyser les catégories
        category = metadata.get('category', 'Non classé')
        if category and category != 'Non classé':
            stats['docs_with_categories'] += 1
            
        if category not in categories:
            categories[category] = {
                'count': 0,
                'projects': set(),
                'authors': set(),
                'file_types': set(),
                'documents': []
            }
        
        categories[category]['count'] += 1
        categories[category]['projects'].add(project)
        categories[category]['authors'].add(metadata.get('author', 'Inconnu'))
        categories[category]['documents'].append(doc)
        
        projects[project]['categories'].add(category)
        
        # Type de fichier
        source = metadata.get('source', '')
        if source:
            ext = os.path.splitext(source)[1].lower()
            categories[category]['file_types'].add(ext if ext else 'autre')
    
    stats['unique_projects'] = len([p for p in projects.keys() if p != 'Projet par défaut'])
    stats['unique_categories'] = len([c for c in categories.keys() if c != 'Non classé'])
    
    return projects, categories, stats

def _show_general_stats(stats: Dict) -> None:
    """Affiche les statistiques générales."""
    
    st.markdown("### 📊 Vue d'ensemble")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📄 Documents totaux", f"{stats['total_docs']:,}")
    
    with col2:
        st.metric(
            "🎯 Projets identifiés", 
            stats['unique_projects'],
            help="Projets avec nom spécifique (hors 'Projet par défaut')"
        )
    
    with col3:
        st.metric(
            "🏷️ Catégories actives", 
            stats['unique_categories'],
            help="Catégories définies (hors 'Non classé')"
        )
    
    with col4:
        st.metric(
            "📊 Projets .data.json", 
            stats['data_json_projects'],
            help="Documents issus de fichiers .data.json"
        )
    
    # Barres de progression
    if stats['total_docs'] > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            project_coverage = stats['docs_with_projects'] / stats['total_docs']
            st.metric(
                "📂 Couverture projets",
                f"{project_coverage:.1%}",
                help="Pourcentage de documents avec projet spécifique"
            )
            st.progress(project_coverage)
        
        with col2:
            category_coverage = stats['docs_with_categories'] / stats['total_docs']
            st.metric(
                "🏷️ Couverture catégories",
                f"{category_coverage:.1%}",
                help="Pourcentage de documents avec catégorie spécifique"
            )
            st.progress(category_coverage)

def _show_projects_view(projects_data: Dict, vector_db) -> None:
    """Affiche la vue des projets."""
    
    if not projects_data:
        st.info("📭 Aucun projet détecté dans la base")
        return
    
    # Filtrer les projets par défaut
    real_projects = {k: v for k, v in projects_data.items() if k != 'Projet par défaut'}
    
    if real_projects:
        st.markdown(f"### 📂 {len(real_projects)} Projet(s) Identifié(s)")
        
        # Tri des projets
        sort_by = st.selectbox(
            "Trier par :",
            ["Nombre de documents", "Nom du projet", "Nombre .data.json"],
            key="sort_projects"
        )
        
        if sort_by == "Nombre de documents":
            sorted_projects = sorted(real_projects.items(), key=lambda x: x[1]['count'], reverse=True)
        elif sort_by == "Nombre .data.json":
            sorted_projects = sorted(real_projects.items(), key=lambda x: x[1]['data_json_count'], reverse=True)
        else:
            sorted_projects = sorted(real_projects.items(), key=lambda x: x[0])
        
        # Affichage des projets
        for project_name, project_data in sorted_projects:
            with st.expander(f"📂 **{project_name}** ({project_data['count']} documents)", expanded=False):
                
                # Métriques du projet
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📄 Documents", project_data['count'])
                with col2:
                    st.metric("📊 .data.json", project_data['data_json_count'])
                with col3:
                    st.metric("🏷️ Catégories", len(project_data['categories']))
                with col4:
                    st.metric("👤 Auteurs", len(project_data['authors']))
                
                # Détails du projet
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**🏷️ Catégories :**")
                    for category in sorted(project_data['categories']):
                        st.write(f"• {category}")
                    
                    st.markdown("**👤 Auteurs :**")
                    for author in sorted(project_data['authors']) if project_data['authors'] != {'Inconnu'} else []:
                        st.write(f"• {author}")
                
                with col2:
                    st.markdown("**📁 Sources :**")
                    for source in sorted(project_data['sources']):
                        st.write(f"• {source}")
                    
                    st.markdown("**📅 Dates :**")
                    dates = [d for d in sorted(project_data['dates']) if d]
                    for date in dates[:5]:  # Limiter à 5 dates
                        st.write(f"• {date}")
                
                # Bouton pour voir les documents
                if st.button(f"📋 Voir les documents de '{project_name}'", key=f"docs_{project_name}"):
                    _show_project_documents(project_name, project_data['documents'])
    
    # Projets par défaut
    if 'Projet par défaut' in projects_data:
        default_count = projects_data['Projet par défaut']['count']
        st.warning(f"⚠️ **{default_count} document(s)** utilise(nt) le projet par défaut")
        st.info("💡 Ajoutez des fichiers .data.json pour organiser ces documents en projets spécifiques")

def _show_categories_view(categories_data: Dict, vector_db) -> None:
    """Affiche la vue des catégories."""
    
    if not categories_data:
        st.info("📭 Aucune catégorie détectée dans la base")
        return
    
    # Filtrer les catégories par défaut
    real_categories = {k: v for k, v in categories_data.items() if k != 'Non classé'}
    
    if real_categories:
        st.markdown(f"### 🏷️ {len(real_categories)} Catégorie(s) Identifiée(s)")
        
        # Affichage en grille
        cols = st.columns(3)
        
        sorted_categories = sorted(real_categories.items(), key=lambda x: x[1]['count'], reverse=True)
        
        for i, (category_name, category_data) in enumerate(sorted_categories):
            with cols[i % 3]:
                with st.container():
                    st.markdown(f"**🏷️ {category_name}**")
                    st.metric("📄 Documents", category_data['count'])
                    st.metric("📂 Projets", len(category_data['projects']))
                    
                    # Types de fichiers
                    file_types = list(category_data['file_types'])
                    if file_types:
                        st.write(f"**📎 Types :** {', '.join(file_types[:3])}")
                    
                    if st.button(f"🔍 Détails", key=f"cat_{category_name}"):
                        _show_category_details(category_name, category_data)
    
    # Catégories par défaut
    if 'Non classé' in categories_data:
        default_count = categories_data['Non classé']['count']
        st.warning(f"⚠️ **{default_count} document(s)** sans catégorie spécifique")
        st.info("💡 Enrichissez vos fichiers .data.json avec le champ 'categorie' pour une meilleure organisation")

def _show_analysis_view(projects_data: Dict, categories_data: Dict, stats: Dict, vector_db) -> None:
    """Affiche l'analyse avancée."""
    
    st.markdown("### 🔍 Analyse Avancée")
    
    # Recommandations
    st.markdown("#### 💡 Recommandations")
    
    recommendations = []
    
    if stats['data_json_projects'] == 0:
        recommendations.append("📊 **Ajoutez des fichiers .data.json** pour structurer vos données en projets")
    
    if stats['unique_projects'] < stats['total_docs'] / 10:
        recommendations.append("🎯 **Augmentez le nombre de projets** pour une meilleure organisation")
    
    if stats['unique_categories'] < 5:
        recommendations.append("🏷️ **Enrichissez les catégories** pour faciliter la recherche")
    
    coverage_project = stats['docs_with_projects'] / stats['total_docs'] if stats['total_docs'] > 0 else 0
    if coverage_project < 0.8:
        recommendations.append(f"📂 **Couverture projets ({coverage_project:.1%})** - Visez 80%+ pour une meilleure structure")
    
    if recommendations:
        for rec in recommendations:
            st.warning(rec)
    else:
        st.success("✅ **Excellente organisation !** Votre base RAG est bien structurée.")
    
    # Matrice projets x catégories
    if projects_data and categories_data:
        st.markdown("#### 📊 Matrice Projets × Catégories")
        
        # Construire la matrice
        real_projects = [p for p in projects_data.keys() if p != 'Projet par défaut']
        real_categories = [c for c in categories_data.keys() if c != 'Non classé']
        
        if real_projects and real_categories:
            matrix_data = []
            
            for project in real_projects[:10]:  # Limiter à 10 projets
                row = {'Projet': project}
                for category in real_categories[:5]:  # Limiter à 5 catégories
                    # Compter les documents de ce projet dans cette catégorie
                    count = len([doc for doc in projects_data[project]['documents'] 
                               if doc.get('metadata', {}).get('category') == category])
                    row[category] = count
                matrix_data.append(row)
            
            if matrix_data:
                st.dataframe(matrix_data, use_container_width=True)
        
        # Top associations
        st.markdown("#### 🔗 Top Associations")
        
        associations = []
        for project_name, project_data in projects_data.items():
            if project_name != 'Projet par défaut':
                for category in project_data['categories']:
                    if category != 'Non classé':
                        # Compter les documents de cette association
                        count = len([doc for doc in project_data['documents'] 
                                   if doc.get('metadata', {}).get('category') == category])
                        associations.append((project_name, category, count))
        
        # Trier par nombre de documents
        associations.sort(key=lambda x: x[2], reverse=True)
        
        if associations:
            st.markdown("**🏆 Associations les plus fréquentes :**")
            for i, (project, category, count) in enumerate(associations[:10]):
                st.write(f"{i+1}. **{project}** × **{category}** : {count} documents")

def _show_project_documents(project_name: str, documents: List) -> None:
    """Affiche les documents d'un projet spécifique."""
    
    st.markdown(f"#### 📋 Documents du projet '{project_name}'")
    
    for i, doc in enumerate(documents[:10]):  # Limiter à 10 documents
        metadata = doc.get('metadata', {})
        
        with st.expander(f"📄 Document {i+1}: {os.path.basename(metadata.get('source', 'N/A'))}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**🏷️ Catégorie :** {metadata.get('category', 'N/A')}")
                st.write(f"**👤 Auteur :** {metadata.get('author', 'N/A')}")
                st.write(f"**📅 Date :** {metadata.get('date', 'N/A')}")
            
            with col2:
                st.write(f"**📁 Source :** {metadata.get('source', 'N/A')}")
                st.write(f"**🏷️ Tags :** {metadata.get('tags', 'N/A')}")
                st.write(f"**📊 Format :** {metadata.get('source_format', 'standard')}")
            
            if metadata.get('description'):
                st.write(f"**📝 Description :** {metadata['description'][:200]}...")
    
    if len(documents) > 10:
        st.write(f"... et {len(documents) - 10} autres documents")

def _show_category_details(category_name: str, category_data: Dict) -> None:
    """Affiche les détails d'une catégorie."""
    
    st.markdown(f"#### 🏷️ Détails de la catégorie '{category_name}'")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📂 Projets associés :**")
        for project in sorted(category_data['projects']):
            st.write(f"• {project}")
    
    with col2:
        st.markdown("**📎 Types de fichiers :**")
        for file_type in sorted(category_data['file_types']):
            st.write(f"• {file_type}")
        
        st.markdown("**👤 Auteurs :**")
        authors = [a for a in sorted(category_data['authors']) if a != 'Inconnu']
        for author in authors[:5]:
            st.write(f"• {author}")
