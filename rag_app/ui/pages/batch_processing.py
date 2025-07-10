"""Page de traitement par lots."""

import streamlit as st
import os
from typing import Dict, Any
from pathlib import Path

from ...services.batch_service import BatchService
from ...config.settings import VECTOR_DB_FILE

def show() -> None:
    """Affiche la page de traitement par lots."""
    
    st.header("📁 Traitement par Lots")
    
    # Vérification de la base vectorielle
    if 'vector_db' not in st.session_state:
        st.error("⚠️ Base vectorielle non initialisée")
        return
        
    vector_db = st.session_state.vector_db
    batch_service = BatchService(vector_db)
    
    # Description des fonctionnalités
    _show_features_description()
    
    # Interface principale
    _show_main_interface(batch_service)
    
    # Guide d'utilisation
    _show_usage_guide()

def _show_features_description() -> None:
    """Affiche la description des fonctionnalités."""
    
    st.markdown("""
    ### 📋 Fonctionnalités
    - **Parcours récursif** : Traite tous les sous-dossiers automatiquement
    - **Fichiers d'annonce** : Utilise `._rag_.data` pour contextualiser
    - **Formats supportés** : PDF, TXT, PNG, JPG, JPEG
    - **Métadonnées enrichies** : Catégories, projets, tags automatiques
    - **🔍 Vision avancée** : OCR et classification d'images
    """)

def _show_main_interface(batch_service: BatchService) -> None:
    """Affiche l'interface principale de traitement."""
    
    # Sélection du répertoire
    directory_path = st.text_input(
        "📂 Chemin du répertoire à traiter",
        value="",
        placeholder="Ex: C:\\MesDocuments\\Projets"
    )
    
    if directory_path and os.path.exists(directory_path):
        st.success(f"✅ Répertoire trouvé : {directory_path}")
        
        # Options de traitement
        col1, col2 = st.columns(2)
        
        with col1:
            options = _show_processing_options(batch_service)
            
        with col2:
            _show_directory_preview(directory_path, options['extensions'], batch_service)
        
        # Traitement par lots
        if 'files_to_process' in st.session_state:
            _show_batch_execution(directory_path, options, batch_service)
            
    elif directory_path:
        st.error("❌ Répertoire non trouvé ou inaccessible")

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

def _show_directory_preview(directory_path: str, extensions: list, batch_service: BatchService) -> None:
    """Affiche la prévisualisation du répertoire."""
    
    st.markdown("### 📊 Prévisualisation")
    
    if st.button("🔍 Scanner le répertoire"):
        with st.spinner("Scan en cours..."):
            from ...utils.file_utils import find_files_recursive
            files_found = find_files_recursive(directory_path, extensions)
            
            if files_found:
                st.info(f"📄 {len(files_found)} fichier(s) trouvé(s)")
                
                # Compter les types de fichiers
                file_types = {'pdf': 0, 'txt': 0, 'images': 0}
                for file_path, _ in files_found:
                    ext = os.path.splitext(file_path)[1].lower()
                    if ext == '.pdf':
                        file_types['pdf'] += 1
                    elif ext == '.txt':
                        file_types['txt'] += 1
                    elif ext in ['.png', '.jpg', '.jpeg']:
                        file_types['images'] += 1
                
                # Afficher les statistiques
                st.markdown("**Répartition des fichiers :**")
                if file_types['pdf'] > 0:
                    st.write(f"📄 PDF : {file_types['pdf']}")
                if file_types['txt'] > 0:
                    st.write(f"📝 TXT : {file_types['txt']}")
                if file_types['images'] > 0:
                    st.write(f"🖼️ Images : {file_types['images']}")
                
                # Afficher un échantillon
                st.markdown("**Échantillon des fichiers :**")
                for i, (file_path, annonce_data) in enumerate(files_found[:5]):
                    st.write(f"{i+1}. {os.path.basename(file_path)}")
                    if annonce_data:
                        st.write(f"   📋 Contexte: {annonce_data.get('title', 'N/A')}")
                
                if len(files_found) > 5:
                    st.write(f"... et {len(files_found) - 5} autres fichiers")
                
                # Stocker les résultats pour le traitement
                st.session_state.files_to_process = files_found
            else:
                st.warning("⚠️ Aucun fichier trouvé avec les critères sélectionnés")

def _show_batch_execution(directory_path: str, options: Dict[str, Any], batch_service: BatchService) -> None:
    """Affiche l'interface d'exécution du traitement par lots."""
    
    st.markdown("### 🚀 Traitement par Lots")
    
    files_list = st.session_state.files_to_process
    
    # Afficher les options choisies
    if options['enable_vision']:
        st.info("🔍 Vision avancée activée - Les images seront analysées en profondeur")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"📁 **Répertoire:** {directory_path}")
        st.write(f"📄 **Fichiers à traiter:** {len(files_list)}")
        
    with col2:
        st.write(f"📋 **Extensions:** {', '.join(options['extensions'])}")
        st.write(f"📏 **Taille max:** {options['max_file_size']} MB")
    
    # Bouton de lancement
    if st.button("▶️ Lancer le traitement", type="primary"):
        _execute_batch_processing(files_list, options, batch_service)

def _execute_batch_processing(files_list: list, options: Dict[str, Any], batch_service: BatchService) -> None:
    """Exécute le traitement par lots."""
    
    # Barre de progression
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    def update_progress(current: int, total: int, current_file: str):
        progress = current / total
        progress_bar.progress(progress)
        status_text.text(f"Traitement : {current}/{total} - {os.path.basename(current_file)}")
    
    # Traitement
    with st.spinner("Traitement en cours..."):
        directory_path = os.path.dirname(files_list[0][0]) if files_list else ""
        results = batch_service.process_directory(
            directory=directory_path,
            file_extensions=options['extensions'],
            progress_callback=update_progress,
            enable_vision=options['enable_vision']
        )
    
    # Affichage des résultats
    progress_bar.progress(1.0)
    status_text.text("Traitement terminé !")
    
    _show_processing_results(results, batch_service)

def _show_processing_results(results: Dict[str, Any], batch_service: BatchService) -> None:
    """Affiche les résultats du traitement."""
    
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
    
    # Nettoyer la session
    if 'files_to_process' in st.session_state:
        del st.session_state.files_to_process

def _show_usage_guide() -> None:
    """Affiche le guide d'utilisation."""
    
    with st.expander("📋 Guide d'Utilisation"):
        st.markdown("""
        ### 📋 Format du Fichier d'Annonce
        
        Créez un fichier `._rag_.data` dans vos dossiers avec ce format :
        
        **Format JSON :**
        ```json
        {
            "title": "Projet X - Documentation",
            "category": "Projet",
            "project": "Projet X",
            "author": "Nom de l'auteur",
            "description": "Description du contenu du dossier",
            "tags": "documentation,projet,important",
            "date": "2024-01-15",
            "type": "documentation",
            "priority": "high",
            "status": "active"
        }
        ```
        
        **Format texte simple :**
        ```
        title: Projet X - Documentation
        category: Projet  
        project: Projet X
        author: Nom de l'auteur
        description: Description du contenu du dossier
        tags: documentation,projet,important
        ```
        
        ### 💡 Conseils d'Utilisation
        
        - **Organisation** : Placez un fichier `._rag_.data` dans chaque dossier thématique
        - **Nommage** : Utilisez des noms de catégories et projets cohérents
        - **Taille** : Évitez les fichiers trop volumineux (>100MB)
        - **Vision** : Activez la vision avancée uniquement pour les images importantes
        """)
        
        # Exemple de fichier d'annonce
        if st.button("📝 Créer un exemple de fichier d'annonce"):
            example_content = '''{
    "title": "Documentation Exemple",
    "category": "Exemple",
    "project": "Projet Test",
    "author": "Utilisateur Test",
    "description": "Exemple de fichier de métadonnées pour le traitement par lots",
    "tags": "exemple,test,documentation",
    "date": "2024-07-10",
    "type": "documentation",
    "priority": "normal",
    "status": "active"
}'''
            st.code(example_content, language='json')
            st.info("💾 Copiez ce contenu dans un fichier `._rag_.data` dans votre dossier de documents.")
