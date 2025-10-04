"""Page de traitement par lots."""

import streamlit as st
import os
from typing import Dict, Any
from pathlib import Path

from ...services.batch_service import BatchService
from ...config.settings import VECTOR_DB_FILE
from ..components.debug_panel import show_debug_panel

def show() -> None:
    """Affiche la page de traitement par lots."""
    
    st.header("📁 Traitement par Lots")
    
    # Vérification de la base vectorielle
    if 'vector_db' not in st.session_state:
        st.error("⚠️ Base vectorielle non initialisée")
        return
        
    vector_db = st.session_state.vector_db
    batch_service = BatchService(vector_db)
    
    # Vérification et avertissement en cas de base obsolète
    _check_and_warn_old_database()
    
    # Description des fonctionnalités
    _show_features_description()
    
    # Interface principale
    _show_main_interface(batch_service)
    
    # Guide d'utilisation
    _show_usage_guide()

def _check_and_warn_database_conflicts(selected_sources=None):
    """Vérifie les conflits entre la base vectorielle et les sources sélectionnées."""
    
    if 'vector_db' not in st.session_state:
        return
        
    vector_db = st.session_state.vector_db
    
    if not hasattr(vector_db, 'documents') or not vector_db.documents:
        st.info("📊 **Base vectorielle vide** - Prête pour l'indexation")
        return
    
    # Analyser les sources des documents existants
    actions_4b_count = 0
    actions_11_count = 0
    other_sources = {}
    total_docs = len(vector_db.documents)
    
    # Échantillonner les documents pour analyser les sources
    sample_size = min(100, total_docs)
    for doc in vector_db.documents[:sample_size]:
        source = doc.get('metadata', {}).get('source', '')
        if 'Actions-4b_new' in source:
            actions_4b_count += 1
        elif 'Actions-11-Projects' in source:
            actions_11_count += 1
        else:
            # Extraire le répertoire racine pour les autres sources
            if source:
                # Chercher le répertoire parent principal
                parts = source.replace('\\', '/').split('/')
                if len(parts) >= 3:
                    root_path = '/'.join(parts[:3])  # Ex: C:/Users/Documents
                    other_sources[root_path] = other_sources.get(root_path, 0) + 1
    
    # Extrapoler pour tous les documents
    ratio_4b = (actions_4b_count / sample_size) * total_docs if sample_size > 0 else 0
    ratio_11 = (actions_11_count / sample_size) * total_docs if sample_size > 0 else 0
    
    # Afficher l'état de la base
    st.markdown("### 📊 État de la base vectorielle")
    
    # Métriques principales
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📄 Total documents", f"{total_docs:,}")
    with col2:
        st.metric("📁 Actions-4b_new", f"~{ratio_4b:.0f}")
    with col3:
        st.metric("📁 Actions-11-Projects", f"~{ratio_11:.0f}")
    
    # Afficher les autres sources si présentes
    if other_sources:
        st.markdown("**🗂️ Autres sources détectées :**")
        for source_path, count in sorted(other_sources.items(), key=lambda x: x[1], reverse=True)[:5]:
            estimated_total = (count / sample_size) * total_docs if sample_size > 0 else count
            st.write(f"📁 `{source_path}` : ~{estimated_total:.0f} documents")
    
    # Analyser les conflits avec les sources sélectionnées
    if selected_sources:
        # Si c'est une seule source (ancienne interface)
        if isinstance(selected_sources, str):
            selected_sources = [selected_sources]
        
        st.markdown("### ⚠️ Analyse des conflits")
        
        conflicts_detected = False
        compatible_sources = []
        
        for source in selected_sources:
            if not os.path.exists(source):
                continue
                
            # Vérifier la compatibilité avec la base existante
            is_actions_4b = "Actions-4b_new" in source
            is_actions_11 = "Actions-11-Projects" in source
            
            if is_actions_4b and ratio_11 > ratio_4b and ratio_11 > 10:
                st.warning(f"""
                ⚠️ **Conflit détecté pour {os.path.basename(source)}**
                
                La base contient principalement des documents `Actions-11-Projects` 
                mais vous voulez traiter `Actions-4b_new`.
                """)
                conflicts_detected = True
                
            elif is_actions_11 and ratio_4b > ratio_11 and ratio_4b > 10:
                st.warning(f"""
                ⚠️ **Conflit détecté pour {os.path.basename(source)}**
                
                La base contient principalement des documents `Actions-4b_new` 
                mais vous voulez traiter `Actions-11-Projects`.
                """)
                conflicts_detected = True
                
            elif is_actions_4b and ratio_4b > ratio_11:
                compatible_sources.append(source)
            elif is_actions_11 and ratio_11 > ratio_4b:
                compatible_sources.append(source)
            else:
                # Source personnalisée - vérifier si elle existe déjà
                source_exists = False
                for existing_source in other_sources:
                    if source.replace('\\', '/').startswith(existing_source) or existing_source.startswith(source.replace('\\', '/')):
                        source_exists = True
                        compatible_sources.append(source)
                        break
                
                if not source_exists:
                    st.info(f"""
                    💡 **Nouvelle source détectée : {os.path.basename(source)}**
                    
                    Cette source sera ajoutée à la base existante.
                    """)
        
        # Afficher les sources compatibles
        if compatible_sources:
            st.success(f"""
            ✅ **Sources compatibles détectées**
            
            {len(compatible_sources)} source(s) compatible(s) avec la base existante.
            Les nouveaux documents s'ajouteront aux existants.
            """)
        
        # Recommandations selon les conflits
        if conflicts_detected:
            st.markdown("""
            **🎯 Recommandations :**
            - 🔄 **Ajouter** : Les nouveaux documents s'ajouteront aux existants (base mixte)
            - 🧹 **Nettoyer** : Vider la base avant traitement (recommandé pour éviter la confusion)
            """)
    
    # Boutons de gestion de la base
    st.markdown("### 🧹 Gestion de la base")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🧹 Nettoyer la base", help="Vide complètement la base vectorielle"):
            _clean_vector_database()
    
    with col2:
        if st.button("📊 Analyser la base", help="Affiche les détails de la base"):
            _show_database_analysis(vector_db)
    
    with col3:
        if st.button("💾 Sauvegarder", help="Force la sauvegarde de la base"):
            try:
                vector_db.save()
                st.success("✅ Base sauvegardée")
            except Exception as e:
                st.error(f"❌ Erreur sauvegarde: {e}")

def _show_database_analysis(vector_db):
    """Affiche une analyse détaillée de la base vectorielle."""
    
    st.markdown("#### 🔍 Analyse détaillée")
    
    if not hasattr(vector_db, 'documents') or not vector_db.documents:
        st.info("Base vectorielle vide")
        return
    
    # Analyse des sources
    sources = {}
    for doc in vector_db.documents:
        source = doc.get('metadata', {}).get('source', 'Inconnu')
        # Extraire le répertoire parent
        if 'Actions-4b_new' in source:
            repo = 'Actions-4b_new'
        elif 'Actions-11-Projects' in source:
            repo = 'Actions-11-Projects'
        else:
            repo = 'Autre'
        
        sources[repo] = sources.get(repo, 0) + 1
    
    # Afficher les statistiques
    for repo, count in sorted(sources.items()):
        percentage = (count / len(vector_db.documents)) * 100
        st.write(f"📁 **{repo}** : {count:,} documents ({percentage:.1f}%)")
    
    # Exemples de sources
    st.markdown("**Exemples de sources :**")
    sample_sources = set()
    for doc in vector_db.documents[:20]:
        source = doc.get('metadata', {}).get('source', '')
        if source:
            sample_sources.add(source)
    
    for source in list(sample_sources)[:5]:
        st.text(f"• {source}")
    
    if len(sample_sources) > 5:
        st.text(f"... et {len(sample_sources) - 5} autres")

def _check_and_warn_old_database():
    """Vérifie si la base vectorielle contient des données de l'ancien répertoire."""
    
    if 'vector_db' not in st.session_state:
        return
        
    vector_db = st.session_state.vector_db
    
    if not hasattr(vector_db, 'documents') or not vector_db.documents:
        return
    
    # Vérifier les sources des documents
    old_path_count = 0
    new_path_count = 0
    total_docs = len(vector_db.documents)
    
    for doc in vector_db.documents[:50]:  # Échantillon des 50 premiers
        source = doc.get('metadata', {}).get('source', '')
        if 'Actions-4b_new' in source:
            old_path_count += 1
        elif 'Actions-11-Projects' in source:
            new_path_count += 1
    
    # Si la majorité des documents viennent de l'ancien répertoire
    if old_path_count > new_path_count and old_path_count > 10:
        st.warning(f"""
        ⚠️ **ATTENTION: Base vectorielle obsolète détectée**
        
        La base vectorielle contient {total_docs} documents de l'ancien répertoire `Actions-4b_new`.
        
        **Recommandation:** Nettoyez la base avant de réindexer :
        1. Cliquez sur le bouton "🧹 Nettoyer la base" ci-dessous
        2. Puis relancez le traitement par lots avec le bon répertoire
        """)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🧹 Nettoyer la base vectorielle", type="primary"):
                _clean_vector_database()

def _clean_vector_database():
    """Nettoie complètement la base vectorielle."""
    try:
        # Réinitialiser la base vectorielle
        from ...core.vector_database import VectorDatabase
        
        # Créer une nouvelle base vide
        new_db = VectorDatabase()
        new_db.save()
        
        # Mettre à jour la session
        st.session_state.vector_db = new_db
        
        st.success("✅ Base vectorielle nettoyée avec succès !")
        st.info("🔄 Vous pouvez maintenant lancer le traitement par lots")
        
        # Forcer le rechargement de la page
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Erreur lors du nettoyage : {e}")

def _show_features_description() -> None:
    """Affiche la description des fonctionnalités."""
    
    st.markdown("""
    ### 📋 Fonctionnalités
    - **🌐 Sources multiples** : Ajoutez n'importe quels répertoires (locaux, réseau, cloud, USB)
    - **🚀 Raccourcis rapides** : Boutons pour Actions-11-Projects, Actions-4b_new, Desktop, Documents
    - **✏️ Chemins personnalisés** : Spécifiez librement vos propres emplacements
    - **🔍 Détection intelligente** : Analyse automatique des conflits entre sources
    - **📊 Prévisualisation** : Scanner et analyser chaque source individuellement
    - **Parcours récursif** : Traite tous les sous-dossiers automatiquement
    - **Fichiers d'annonce** : Utilise `._rag_.data`, `.data.json` et `"dossier"_notes.txt` pour contextualiser
    - **Mapping intelligent** : `description` → nom projet, `dossier` → numéro interne, `entreprise` → société liée, `contact/tel/mail` → informations de contact
    - **Détection CV/BA** : Identifie automatiquement les fichiers `*_CV_*.pdf` (candidatures) et `*_BA_*.pdf` (supports oraux)
    - **Niveau de maturité** : Calcule automatiquement le statut (💡 Idée → 🚀 Initié → 📤 Envoyé → 🤝 Démarche)
    - **Métadonnées enrichies** : Fusion automatique des différentes sources de métadonnées
    - **Formats supportés** : PDF, TXT, PNG, JPG, JPEG
    - **Tags automatiques** : Catégories, projets, entreprises, contacts, notes personnalisées, présentations
    - **🔍 Vision avancée** : OCR et classification d'images
    - **💾 Traitement parallèle** : Gestion simultanée de multiples sources avec agrégation des résultats
    """)
    
    # Ajouter un lien vers le guide détaillé
    st.info("""
    📖 **Nouveau !** Interface multi-sources flexible - Consultez le 
    [Guide Sources Multiples](GUIDE_SOURCES_MULTIPLES.md) pour tous les détails.
    """)

def _show_main_interface(batch_service: BatchService) -> None:
    """Affiche l'interface principale de traitement."""
    
    st.markdown("### 📂 Gestion des sources de données")
    
    # Initialiser la session pour les sources multiples
    if 'data_sources' not in st.session_state:
        st.session_state.data_sources = []
    
    # Section d'ajout de nouvelles sources
    with st.expander("➕ Ajouter une nouvelle source", expanded=True):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Raccourcis rapides
            st.markdown("**🚀 Raccourcis rapides :**")
            quick_buttons = st.columns(4)
            
            with quick_buttons[0]:
                if st.button("📁 Actions-11-Projects", help="Projets actuels"):
                    new_source = "h:\\Entreprendre\\Actions-11-Projects"
                    if new_source not in st.session_state.data_sources:
                        st.session_state.data_sources.append(new_source)
                        st.rerun()
            
            with quick_buttons[1]:
                if st.button("📁 Actions-4b_new", help="Archives"):
                    new_source = "h:\\Entreprendre\\Actions-4b_new"
                    if new_source not in st.session_state.data_sources:
                        st.session_state.data_sources.append(new_source)
                        st.rerun()
            
            with quick_buttons[2]:
                if st.button("📁 Desktop", help="Bureau utilisateur"):
                    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
                    if desktop not in st.session_state.data_sources:
                        st.session_state.data_sources.append(desktop)
                        st.rerun()
            
            with quick_buttons[3]:
                if st.button("📁 Documents", help="Dossier Documents"):
                    documents = os.path.join(os.path.expanduser("~"), "Documents")
                    if documents not in st.session_state.data_sources:
                        st.session_state.data_sources.append(documents)
                        st.rerun()
            
            st.markdown("**✏️ Ou spécifiez un chemin personnalisé :**")
            
            # Saisie manuelle
            custom_path = st.text_input(
                "Chemin personnalisé",
                placeholder="Ex: C:\\MesProjets\\Dossier1",
                help="Entrez le chemin complet vers votre répertoire"
            )
            
        with col2:
            st.markdown("**Actions**")
            
            # Bouton d'ajout du chemin personnalisé
            if st.button("➕ Ajouter", disabled=not custom_path):
                if custom_path and os.path.exists(custom_path):
                    if custom_path not in st.session_state.data_sources:
                        st.session_state.data_sources.append(custom_path)
                        st.success(f"✅ Source ajoutée")
                        st.rerun()
                    else:
                        st.warning("⚠️ Source déjà présente")
                elif custom_path:
                    st.error("❌ Chemin introuvable")
            
            # Bouton de nettoyage
            if st.button("🗑️ Tout vider"):
                st.session_state.data_sources = []
                st.success("✅ Sources vidées")
                st.rerun()
    
    # Affichage des sources configurées
    if st.session_state.data_sources:
        st.markdown("### 📋 Sources configurées")
        
        # Vérifier les conflits avec la base existante
        _check_and_warn_database_conflicts(st.session_state.data_sources)
        
        for i, source in enumerate(st.session_state.data_sources):
            col1, col2, col3, col4 = st.columns([3, 1.5, 1.5, 1])
            
            with col1:
                # Icône selon le type de source
                if "Actions-11-Projects" in source:
                    icon = "🆕"
                    label = f"{icon} {os.path.basename(source)} (Projets actuels)"
                elif "Actions-4b_new" in source:
                    icon = "📦"
                    label = f"{icon} {os.path.basename(source)} (Archives)"
                else:
                    icon = "📁"
                    label = f"{icon} {os.path.basename(source)}"
                
                # Vérifier l'existence
                if os.path.exists(source):
                    st.success(label)
                    # Compter les fichiers
                    try:
                        file_count = sum(len(files) for _, _, files in os.walk(source))
                        st.caption(f"📊 ~{file_count:,} fichiers")
                    except:
                        st.caption("📊 Analyse...")
                else:
                    st.error(f"❌ {label} (introuvable)")
            
            with col2:
                # Bouton prévisualisation avec texte
                if st.button("👁️ Prévisualiser", key=f"preview_{i}", help="Scanner et analyser cette source"):
                    st.session_state[f'preview_source_{i}'] = True
                    st.rerun()
            
            with col3:
                # Bouton traitement individuel avec texte
                if st.button("🚀 Traiter seul", key=f"process_{i}", help="Traiter cette source uniquement"):
                    # Options par défaut pour traitement individuel
                    default_options = {
                        'extensions': ['.pdf', '.txt', '.png', '.jpg', '.jpeg'],
                        'max_file_size': 100,
                        'enable_vision': False
                    }
                    _execute_single_source_processing(source, default_options, batch_service)
            
            with col4:
                # Bouton suppression
                if st.button("🗑️ Suppr.", key=f"delete_{i}", help="Supprimer cette source"):
                    st.session_state.data_sources.pop(i)
                    st.rerun()
        
        # Affichage des prévisualisations
        for i, source in enumerate(st.session_state.data_sources):
            if st.session_state.get(f'preview_source_{i}', False):
                with st.expander(f"👁️ Prévisualisation: {os.path.basename(source)}", expanded=True):
                    if st.button("❌ Fermer", key=f"close_preview_{i}"):
                        st.session_state[f'preview_source_{i}'] = False
                        st.rerun()
                    
                    _show_source_preview(source, batch_service)
        
        # Interface de traitement global
        st.markdown("### 🚀 Traitement global")
        
        # Options de traitement
        options = _show_processing_options(batch_service)
        
        # Statistiques globales
        total_sources = len([s for s in st.session_state.data_sources if os.path.exists(s)])
        st.info(f"📊 **{total_sources} source(s) valide(s)** configurée(s) pour le traitement")
        
        # Bouton de traitement global
        if st.button("▶️ Traiter toutes les sources", type="primary", disabled=total_sources == 0):
            _execute_multi_source_processing(st.session_state.data_sources, options, batch_service)
    
    else:
        st.info("📂 **Aucune source configurée** - Ajoutez des répertoires ci-dessus pour commencer")
        
        # Afficher l'état de la base même sans sources
        _check_and_warn_database_conflicts()

def _show_processing_options(batch_service: BatchService) -> Dict[str, Any]:
    """Affiche les options de traitement."""
    
    st.markdown("### ⚙️ Options de Traitement")
    
    supported = batch_service.get_supported_extensions()
    
    extensions = st.multiselect(
        "Types de fichiers à traiter",
        supported['all'],
        default=['.pdf', '.txt', '.png', '.jpg', '.jpeg'],
        help="Sélectionnez les types de fichiers à inclure dans le traitement"
    )
    
    max_file_size = st.slider(
        "Taille max par fichier (MB)",
        1, 200, 100,
        help="Fichiers plus volumineux seront ignorés"
    )
    
    # Option pour activer la vision avancée
    enable_vision = st.checkbox(
        "🔍 Activer la vision avancée pour les images",
        value=False,
        help="Génère des descriptions automatiques et classifie les images (plus lent)"
    )
    
    if enable_vision:
        st.info("⚠️ Le traitement sera plus lent mais les images seront mieux analysées")
    
    return {
        'extensions': extensions,
        'max_file_size': max_file_size,
        'enable_vision': enable_vision
    }

def _show_source_preview(source_path: str, batch_service: BatchService) -> None:
    """Affiche la prévisualisation d'une source spécifique."""
    
    if not os.path.exists(source_path):
        st.error("❌ Source introuvable")
        return
    
    if st.button("🔍 Scanner cette source", key=f"scan_{source_path}"):
        with st.spinner(f"Scan de {source_path}..."):
            from ...utils.file_utils import find_files_recursive
            
            # Extensions par défaut
            extensions = ['.pdf', '.txt', '.png', '.jpg', '.jpeg']
            
            # Scan de la source
            files_found = find_files_recursive(source_path, extensions)
            
            if files_found:
                st.success(f"📄 {len(files_found)} fichier(s) trouvé(s)")
                
                # Statistiques par type
                file_types = {'pdf': 0, 'txt': 0, 'images': 0, 'other': 0}
                projects = set()
                categories = set()
                
                for file_path, metadata in files_found:
                    ext = os.path.splitext(file_path)[1].lower()
                    if ext == '.pdf':
                        file_types['pdf'] += 1
                    elif ext == '.txt':
                        file_types['txt'] += 1
                    elif ext in ['.png', '.jpg', '.jpeg']:
                        file_types['images'] += 1
                    else:
                        file_types['other'] += 1
                    
                    # Collecter projets et catégories
                    if metadata:
                        if metadata.get('project') and metadata['project'] != 'Projet par défaut':
                            projects.add(metadata['project'])
                        if metadata.get('category') and metadata['category'] != 'Non classé':
                            categories.add(metadata['category'])
                
                # Affichage des stats de fichiers
                st.markdown("**📊 Statistiques des fichiers :**")
                cols = st.columns(4)
                with cols[0]:
                    st.metric("📄 PDF", file_types['pdf'])
                with cols[1]:
                    st.metric("📝 TXT", file_types['txt'])
                with cols[2]:
                    st.metric("🖼️ Images", file_types['images'])
                with cols[3]:
                    st.metric("📎 Autres", file_types['other'])
                
                # Affichage des projets détectés
                if projects:
                    st.markdown("**📋 Projets détectés :**")
                    st.info(f"🎯 **{len(projects)} projet(s)** identifié(s) depuis les fichiers .data.json")
                    for project in sorted(projects):
                        st.write(f"• 📂 **{project}**")
                else:
                    st.warning("⚠️ Aucun projet spécifique détecté - utilisation du projet par défaut")
                
                # Affichage des catégories détectées
                if categories:
                    st.markdown("**🏷️ Catégories détectées :**")
                    st.info(f"🔖 **{len(categories)} catégorie(s)** identifiée(s) depuis les fichiers .data.json")
                    for category in sorted(categories):
                        st.write(f"• 🏷️ **{category}**")
                else:
                    st.warning("⚠️ Aucune catégorie spécifique détectée - utilisation de 'Non classé'")
                
                # Échantillon de fichiers avec métadonnées détaillées
                st.markdown("**📋 Échantillon des fichiers avec métadonnées :**")
                for i, (file_path, metadata) in enumerate(files_found[:5]):
                    with st.expander(f"📄 {os.path.basename(file_path)}", expanded=False):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**📁 Chemin :** `{file_path}`")
                            if metadata.get('project'):
                                st.write(f"**🎯 Projet :** {metadata['project']}")
                            if metadata.get('category'):
                                st.write(f"**🏷️ Catégorie :** {metadata['category']}")
                        with col2:
                            if metadata.get('description'):
                                st.write(f"**📝 Description :** {metadata['description']}")
                            if metadata.get('author'):
                                st.write(f"**👤 Auteur :** {metadata['author']}")
                            if metadata.get('date'):
                                st.write(f"**📅 Date :** {metadata['date']}")
                            if metadata.get('tags'):
                                st.write(f"**🏷️ Tags :** {metadata['tags']}")
                
                if len(files_found) > 5:
                    st.write(f"... et {len(files_found) - 5} autres fichiers")
                    
                # Résumé des métadonnées RAG
                st.markdown("**🤖 Analyse RAG :**")
                data_json_count = sum(1 for _, metadata in files_found if metadata.get('source_format') == 'data_json')
                if data_json_count > 0:
                    st.success(f"✅ {data_json_count} fichier(s) .data.json trouvé(s) et mappé(s) vers le format RAG")
                    st.info("📊 Chaque fichier .data.json représente un projet avec ses métadonnées enrichies")
                else:
                    st.warning("⚠️ Aucun fichier .data.json trouvé - métadonnées limitées")
            else:
                st.warning("⚠️ Aucun fichier trouvé")

def _execute_single_source_processing(source_path: str, options: Dict[str, Any], batch_service: BatchService) -> None:
    """Exécute le traitement sur une seule source avec progression détaillée."""
    
    from ...utils.file_utils import find_files_recursive
    
    # Scanner les fichiers d'abord
    with st.spinner("🔍 Scan des fichiers..."):
        files_found = find_files_recursive(source_path, options['extensions'])
    
    if not files_found:
        st.warning("⚠️ Aucun fichier trouvé à traiter")
        return
    
    total_files = len(files_found)
    st.success(f"📊 **{total_files} fichier(s)** trouvé(s) à traiter")
    
    # Barres de progression
    progress_bar = st.progress(0)
    status_text = st.empty()
    file_counter = st.empty()
    
    # Fonction de callback pour mise à jour
    def update_progress(current: int, total: int, current_file: str):
        progress = current / total if total > 0 else 0
        progress_bar.progress(progress)
        status_text.text(f"📁 {os.path.basename(current_file)}")
        file_counter.text(f"📊 Progression : {current}/{total} fichiers traités")
    
    # Traitement avec callback
    with st.spinner("🔄 Traitement en cours..."):
        results = batch_service.process_directory(
            directory=source_path,
            file_extensions=options['extensions'],
            progress_callback=update_progress,
            enable_vision=options['enable_vision']
        )
    
    # Finalisation
    progress_bar.progress(1.0)
    status_text.text("✅ Traitement terminé !")
    file_counter.text(f"🎉 **Terminé** : {total_files}/{total_files} fichiers traités")
    
    # Affichage des résultats
    _show_processing_results(results, batch_service)
    

def _execute_multi_source_processing(sources: list, options: Dict[str, Any], batch_service: BatchService) -> None:
    """Exécute le traitement sur plusieurs sources."""
    
    # Filtrer les sources valides
    valid_sources = [s for s in sources if os.path.exists(s)]
    
    if not valid_sources:
        st.error("❌ Aucune source valide à traiter")
        return
    
    # Compter le nombre total de fichiers à traiter
    st.info("🔍 Comptage des fichiers à traiter...")
    total_files = 0
    files_by_source = {}
    
    for source in valid_sources:
        try:
            from ...utils.file_utils import find_files_recursive
            files_found = find_files_recursive(source, options['extensions'])
            files_by_source[source] = files_found
            total_files += len(files_found)
        except Exception as e:
            st.warning(f"⚠️ Erreur scan {os.path.basename(source)}: {e}")
            files_by_source[source] = []
    
    if total_files == 0:
        st.warning("⚠️ Aucun fichier à traiter dans les sources sélectionnées")
        return
    
    st.success(f"📊 **{total_files} fichier(s)** trouvé(s) dans {len(valid_sources)} source(s)")
    
    # Barres de progression avec colonnes ajustées
    col1, col2 = st.columns([2, 1])
    
    with col1:
        progress_bar = st.progress(0)
        status_text = st.empty()
    
    with col2:
        file_counter = st.empty()
    
    total_results = {
        'success': 0,
        'errors': 0,
        'skipped': 0,
        'images_processed': [],
        'sources_processed': []
    }
    
    # Compteur global de fichiers traités
    files_processed = 0
    
    # Fonction de callback pour mise à jour de progression
    def update_global_progress(current_in_source: int, total_in_source: int, current_file: str):
        nonlocal files_processed
        files_processed += 1
        
        # Calculer le pourcentage global
        global_progress = files_processed / total_files if total_files > 0 else 0
        progress_bar.progress(min(global_progress, 1.0))
        
        # Afficher les informations détaillées avec texte plus court
        status_text.text(f"� {os.path.basename(current_file)}")
        file_counter.metric("📊 Progression", f"{files_processed}/{total_files}", delta=f"{int(global_progress*100)}%")
    
    # Traitement source par source
    for source_idx, source in enumerate(valid_sources):
        source_name = os.path.basename(source)
        files_in_source = files_by_source[source]
        
        if not files_in_source:
            st.info(f"⏭️ Source {source_name} : Aucun fichier à traiter")
            continue
        
        st.info(f"🔄 **Source {source_idx + 1}/{len(valid_sources)}** : {source_name} ({len(files_in_source)} fichiers)")
        
        # Traitement de la source avec callback de progression
        try:
            results = batch_service.process_directory(
                directory=source,
                file_extensions=options['extensions'],
                progress_callback=update_global_progress,
                enable_vision=options['enable_vision']
            )
            
            # Agréger les résultats
            total_results['success'] += results.get('success', 0)
            total_results['errors'] += results.get('errors', 0)
            total_results['skipped'] += results.get('skipped', 0)
            total_results['images_processed'].extend(results.get('images_processed', []))
            
            total_results['sources_processed'].append({
                'source': source,
                'results': results
            })
            
            # Affichage des résultats de la source
            source_success = results.get('success', 0)
            source_errors = results.get('errors', 0)
            if source_success > 0:
                st.success(f"✅ {source_name} : {source_success} fichier(s) traité(s)")
            if source_errors > 0:
                st.error(f"❌ {source_name} : {source_errors} erreur(s)")
            
        except Exception as e:
            st.error(f"❌ Erreur traitement {source_name}: {e}")
            total_results['errors'] += len(files_in_source) if files_in_source else 1
    
    # Finalisation
    progress_bar.progress(1.0)
    status_text.text("✅ Traitement terminé !")
    file_counter.text(f"🎉 **Terminé** : {files_processed}/{total_files} fichiers traités")
    
    # Affichage des résultats globaux
    _show_multi_source_results(total_results, batch_service)

def _show_processing_results(results: Dict[str, Any], batch_service: BatchService) -> None:
    """Affiche les résultats du traitement d'une source unique."""
    
    # Statistiques générales
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("✅ Succès", results.get('success', 0))
    with col2:
        st.metric("❌ Erreurs", results.get('errors', 0))
    with col3:
        st.metric("⏭️ Ignorés", results.get('skipped', 0))
    with col4:
        st.metric("🖼️ Images", len(results.get('images_processed', [])))
    
    # Analyser les projets et catégories traités
    _show_processed_projects_and_categories(batch_service)
    
    # Afficher les images traitées si disponibles
    if results.get('images_processed'):
        st.markdown("### 🖼️ Images Traitées")
        for i, img_result in enumerate(results['images_processed'][:5]):
            with st.expander(f"📸 {os.path.basename(img_result['file'])}"):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    try:
                        from PIL import Image
                        image = Image.open(img_result['file'])
                        st.image(image, width=200)
                    except:
                        st.write("❌ Aperçu non disponible")
                
                with col2:
                    st.write(f"**Description:** {img_result.get('description', 'N/A')}")
                    st.write(f"**Catégories:** {', '.join(img_result.get('categories', []))}")
                    if img_result.get('ocr_text'):
                        st.write(f"**Texte OCR:** {img_result['ocr_text']}")
        
        if len(results['images_processed']) > 5:
            st.write(f"... et {len(results['images_processed']) - 5} autres images")
    
    # Sauvegarder la base
    if results.get('success', 0) > 0:
        batch_service.vector_db.save()
        st.success(f"✅ {results['success']} fichier(s) ajouté(s) à la base !")
    
    # Afficher les erreurs
    if results.get('errors', 0) > 0:
        with st.expander("❌ Voir les erreurs"):
            for error in results.get('errors_list', []):
                st.error(error)

def _show_multi_source_results(results: Dict[str, Any], batch_service: BatchService) -> None:
    """Affiche les résultats du traitement multi-sources."""
    
    st.markdown("### 📊 Résultats du traitement")
    
    # Statistiques globales
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("✅ Succès total", results['success'])
    with col2:
        st.metric("❌ Erreurs", results['errors'])
    with col3:
        st.metric("⏭️ Ignorés", results['skipped'])
    with col4:
        st.metric("🖼️ Images", len(results['images_processed']))
    
    # Afficher les projets et catégories traités
    _show_processed_projects_and_categories(batch_service)
    
    # Détails par source
    if results.get('sources_processed'):
        st.markdown("### 📁 Détails par source")
        
        for source_data in results['sources_processed']:
            source = source_data['source']
            source_results = source_data['results']
            source_name = os.path.basename(source)
            
            with st.expander(f"📂 {source_name}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("✅ Succès", source_results.get('success', 0))
                with col2:
                    st.metric("❌ Erreurs", source_results.get('errors', 0))
                with col3:
                    st.metric("⏭️ Ignorés", source_results.get('skipped', 0))
                
                # Afficher les erreurs de cette source si présentes
                if source_results.get('errors_list'):
                    st.markdown("**❌ Erreurs :**")
                    for error in source_results['errors_list'][:3]:
                        st.error(error)
                    if len(source_results['errors_list']) > 3:
                        st.write(f"... et {len(source_results['errors_list']) - 3} autres erreurs")
    
    # Images traitées globalement
    if results.get('images_processed'):
        st.markdown("### 🖼️ Images traitées (toutes sources)")
        
        total_images = len(results['images_processed'])
        st.info(f"📸 {total_images} image(s) traitée(s) avec analyse automatique")
        
        # Échantillon d'images
        for i, img_result in enumerate(results['images_processed'][:3]):
            with st.expander(f"📸 {os.path.basename(img_result['file'])}"):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    try:
                        from PIL import Image
                        image = Image.open(img_result['file'])
                        st.image(image, width=150)
                    except:
                        st.write("❌ Aperçu non disponible")
                
                with col2:
                    st.write(f"**Description:** {img_result.get('description', 'N/A')}")
                    st.write(f"**Catégories:** {', '.join(img_result.get('categories', []))}")
                    if img_result.get('ocr_text'):
                        st.write(f"**Texte OCR:** {img_result['ocr_text'][:100]}...")
        
        if total_images > 3:
            st.write(f"... et {total_images - 3} autres images")
    
    # Sauvegarder la base
    if results['success'] > 0:
        batch_service.vector_db.save()
        st.success(f"🎉 **{results['success']} fichier(s) au total** ajoutés à la base RAG !")
        
        # Message de confirmation sur les projets
        st.info("""
        ✅ **Traitement terminé avec succès !**
        
        Les fichiers .data.json ont été automatiquement convertis en projets RAG.
        Utilisez la page "💬 Chat RAG" pour interroger vos données par projet ou catégorie.
        """)
    
    # Résumé des erreurs
    if results['errors'] > 0:
        with st.expander(f"❌ Voir toutes les erreurs ({results['errors']})"):
            all_errors = []
            for source_data in results.get('sources_processed', []):
                all_errors.extend(source_data['results'].get('errors_list', []))
            
            for error in all_errors:
                st.error(error)

def _show_processed_projects_and_categories(batch_service: BatchService) -> None:
    """Affiche les projets et catégories actuellement dans la base vectorielle."""
    
    if not hasattr(batch_service.vector_db, 'documents') or not batch_service.vector_db.documents:
        st.info("📊 Base vectorielle vide")
        return
    
    # Analyser les documents dans la base
    projects = {}
    categories = {}
    data_json_projects = 0
    
    for doc in batch_service.vector_db.documents:
        metadata = doc.get('metadata', {})
        
        # Compter les projets .data.json
        if metadata.get('source_format') == 'data_json':
            data_json_projects += 1
        
        # Collecter projets
        project = metadata.get('project', 'Non spécifié')
        if project not in projects:
            projects[project] = {'count': 0, 'categories': set()}
        projects[project]['count'] += 1
        
        # Collecter catégories
        category = metadata.get('category', 'Non classé')
        if category not in categories:
            categories[category] = 0
        categories[category] += 1
        projects[project]['categories'].add(category)
    
    # Affichage des projets
    st.markdown("### 🎯 Projets dans la base RAG")
    
    if data_json_projects > 0:
        st.success(f"📊 **{data_json_projects} projet(s)** issus de fichiers .data.json détectés")
    
    if len(projects) > 1 or (len(projects) == 1 and 'Projet par défaut' not in projects):
        st.info(f"📂 **{len(projects)} projet(s)** identifié(s) au total")
        
        # Afficher les projets les plus importants
        sorted_projects = sorted(projects.items(), key=lambda x: x[1]['count'], reverse=True)
        
        for project, data in sorted_projects[:10]:  # Top 10
            categories_list = list(data['categories'])
            categories_str = ', '.join(categories_list[:3])
            if len(categories_list) > 3:
                categories_str += f" (+{len(categories_list)-3})"
            
            with st.expander(f"📂 **{project}** ({data['count']} documents)"):
                st.write(f"**🏷️ Catégories :** {categories_str}")
                st.write(f"**📄 Documents :** {data['count']}")
        
        if len(sorted_projects) > 10:
            st.write(f"... et {len(sorted_projects) - 10} autres projets")
    else:
        st.warning("⚠️ Aucun projet spécifique détecté - tous les documents utilisent le projet par défaut")
    
    # Affichage des catégories
    st.markdown("### 🏷️ Catégories dans la base RAG")
    
    if len(categories) > 1 or (len(categories) == 1 and 'Non classé' not in categories):
        st.info(f"🔖 **{len(categories)} catégorie(s)** identifiée(s)")
        
        # Afficher les catégories les plus fréquentes
        sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        
        cols = st.columns(min(3, len(sorted_categories)))
        for i, (category, count) in enumerate(sorted_categories[:6]):
            with cols[i % 3]:
                st.metric(f"🏷️ {category}", count)
        
        if len(sorted_categories) > 6:
            st.write(f"... et {len(sorted_categories) - 6} autres catégories")
    else:
        st.warning("⚠️ Aucune catégorie spécifique détectée - tous les documents utilisent 'Non classé'")
    
    # Information sur l'enrichissement automatique
    if data_json_projects > 0:
        st.markdown("### 🤖 Enrichissement RAG automatique")
        st.info("""
        ✅ **Chaque fichier .data.json** est automatiquement traité comme un projet
        
        🔄 **Mapping automatique :**
        - `dossier` + `description` → **Nom du projet**
        - `categorie` → **Catégorie RAG**
        - `contact` / `entreprise` → **Auteur**
        - `Date` → **Date du projet**
        - Autres champs → **Tags et métadonnées enrichies**
        """)
    else:
        st.warning("""
        ⚠️ **Aucun fichier .data.json détecté**
        
        Pour bénéficier de l'organisation par projets et catégories :
        - Ajoutez des fichiers `.data.json` dans vos sources
        - Chaque fichier représentera un projet avec ses métadonnées
        """)

def _show_usage_guide() -> None:
    """Affiche le guide d'utilisation."""
    
    with st.expander("📋 Guide d'Utilisation"):
        st.markdown("""
        ### 📂 Interface Multi-Sources
        
        Cette nouvelle interface vous permet d'ajouter **n'importe quelles sources** pour votre base RAG :
        
        #### ➕ **Ajout de Sources**
        - 🚀 **Raccourcis rapides** : Boutons pour Actions-11-Projects, Actions-4b_new, Desktop, Documents
        - ✏️ **Chemin personnalisé** : Saisissez n'importe quel répertoire (local, réseau, cloud, USB)
        - ✅ **Validation automatique** : Vérification d'existence et compatibilité
        
        #### 📋 **Gestion des Sources**
        - 👁️ **Prévisualisation** : Scanner une source pour voir les fichiers
        - 🚀 **Traitement individuel** : Traiter une seule source avec progression détaillée
        - ▶️ **Traitement global** : Traiter toutes les sources en une fois
        - 🗑️ **Suppression** : Retirer des sources de la liste
        
        #### 🔍 **Détection Intelligente**
        - ⚠️ **Analyse des conflits** : Détection automatique des incompatibilités
        - 📊 **Recommandations** : Conseils pour gérer les sources mixtes
        - 🧹 **Nettoyage guidé** : Suggestions de nettoyage de base
        
        #### 📊 **Progression Détaillée**
        - 📈 **Comptage préalable** : Nombre total de fichiers à traiter
        - 🔄 **Progression temps réel** : Fichier actuel et pourcentage global
        - 📁 **Résultats par source** : Statistiques détaillées par répertoire
        
        ### 💡 **Exemples d'Utilisation**
        
        **Projets multiples :**
        ```
        ✅ h:\\Entreprendre\\Actions-11-Projects (Actuels)
        ✅ h:\\Entreprendre\\Actions-4b_new (Archives)
        ✅ C:\\Users\\MonNom\\Desktop\\Brouillons
        ```
        
        **Équipe distribuée :**
        ```
        ✅ \\\\serveur\\projets\\equipe1
        ✅ \\\\serveur\\projets\\equipe2
        ✅ C:\\Users\\MonNom\\OneDrive\\Personnel
        ```
        
        ### ⚙️ **Options Avancées**
        - 📄 **Types de fichiers** : PDF, TXT, Images configurables
        - 📏 **Taille maximale** : Limitation par fichier
        - 🔍 **Vision avancée** : OCR et classification d'images
        - 💾 **Sauvegarde automatique** : Base mise à jour en continu
        
        ### 🎯 **Conseils**
        - 🔍 **Prévisualisez** avant de traiter pour éviter les erreurs
        - 🧹 **Nettoyez** la base en cas de conflits de sources
        - 🚀 **Traitez individuellement** pour tester une nouvelle source
        - ▶️ **Traitement global** pour l'efficacité maximale
        """)
    
    # Panneau de debug en bas de page
    show_debug_panel("batch_processing")
