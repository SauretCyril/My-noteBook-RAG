"""Page de galerie d'images."""

import streamlit as st
import os
from PIL import Image
from typing import List, Dict, Any

def show() -> None:
    """Affiche la galerie d'images avec filtres et recherche."""
    
    st.header("🖼️ Galerie d'Images")
    
    if 'vector_db' not in st.session_state:
        st.error("⚠️ Base vectorielle non initialisée")
        return
        
    vector_db = st.session_state.vector_db
    
    # Vérifier s'il y a des images
    if not hasattr(vector_db, 'images') or not vector_db.images:
        _show_empty_gallery()
        return
    
    # Interface de filtrage
    _show_filters(vector_db)
    
    # Affichage des images filtrées
    _show_image_grid(vector_db)
    
    # Détails de l'image sélectionnée
    _show_image_details()

def _show_empty_gallery() -> None:
    """Affiche l'état vide de la galerie."""
    
    st.info("📭 Aucune image dans la galerie")
    
    st.markdown("""
    ### 🚀 Pour ajouter des images :
    
    1. **📁 Traitement par Lots** : Activez la vision avancée lors du traitement
    2. **🔄 Application Héritée** : Utilisez `rag_batch_app.py` pour traiter des images
    3. **📸 Upload Direct** : Interface d'upload à venir dans la v2.1
    """)
    
    # Lien vers le traitement par lots
    if st.button("📁 Aller au Traitement par Lots", type="primary"):
        st.session_state.page_redirect = "batch"
        st.rerun()

def _show_filters(vector_db) -> None:
    """Affiche les filtres de recherche."""
    
    st.markdown("### 🔍 Filtres et Recherche")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Filtrage par catégories
        all_categories = set()
        for img in vector_db.images:
            categories = img.get('categories', [])
            all_categories.update(categories)
        
        selected_categories = st.multiselect(
            "Filtrer par catégorie:",
            sorted(list(all_categories)),
            default=[]
        )
        
        # Stocker dans session state pour utilisation dans le filtrage
        st.session_state.filter_categories = selected_categories
    
    with col2:
        # Filtrage par projets
        all_projects = set()
        for img in vector_db.images:
            project = img.get('metadata', {}).get('project', '')
            if project:
                all_projects.add(project)
        
        selected_projects = st.multiselect(
            "Filtrer par projet:",
            sorted(list(all_projects)),
            default=[]
        )
        
        st.session_state.filter_projects = selected_projects
    
    with col3:
        # Options d'affichage
        images_per_row = st.select_slider(
            "Images par ligne:",
            options=[2, 3, 4, 5],
            value=3
        )
        
        show_details = st.checkbox("Afficher les détails", value=True)
        
        st.session_state.images_per_row = images_per_row
        st.session_state.show_details = show_details
    
    # Recherche textuelle
    search_query = st.text_input(
        "🔍 Rechercher dans les descriptions et texte OCR:",
        placeholder="Ex: document, personne, nature..."
    )
    
    st.session_state.search_query = search_query

def _show_image_grid(vector_db) -> None:
    """Affiche la grille d'images filtrées."""
    
    # Récupérer les filtres depuis session state
    selected_categories = st.session_state.get('filter_categories', [])
    selected_projects = st.session_state.get('filter_projects', [])
    search_query = st.session_state.get('search_query', '')
    images_per_row = st.session_state.get('images_per_row', 3)
    show_details = st.session_state.get('show_details', True)
    
    # Filtrer les images
    filtered_images = vector_db.images.copy()
    
    if selected_categories:
        filtered_images = [
            img for img in filtered_images 
            if any(cat in img.get('categories', []) for cat in selected_categories)
        ]
    
    if selected_projects:
        filtered_images = [
            img for img in filtered_images 
            if img.get('metadata', {}).get('project', '') in selected_projects
        ]
    
    if search_query:
        search_lower = search_query.lower()
        filtered_images = [
            img for img in filtered_images 
            if search_lower in img.get('description', '').lower() or 
               search_lower in img.get('text_content', '').lower() or
               any(search_lower in cat.lower() for cat in img.get('categories', []))
        ]
    
    if not filtered_images:
        st.info("🔍 Aucune image ne correspond aux critères de recherche.")
        return
    
    st.markdown(f"### 🖼️ {len(filtered_images)} image(s) trouvée(s)")
    
    # Pagination pour de grandes collections
    page_size = images_per_row * 6  # 6 lignes par page
    total_pages = (len(filtered_images) + page_size - 1) // page_size
    
    if total_pages > 1:
        page = st.selectbox(
            "Page",
            range(1, total_pages + 1),
            format_func=lambda x: f"Page {x}/{total_pages}"
        )
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_images = filtered_images[start_idx:end_idx]
    else:
        page_images = filtered_images
    
    # Affichage en grille
    num_images = len(page_images)
    num_rows = (num_images + images_per_row - 1) // images_per_row
    
    for row in range(num_rows):
        cols = st.columns(images_per_row)
        
        for col_idx in range(images_per_row):
            img_idx = row * images_per_row + col_idx
            
            if img_idx < num_images:
                img_data = page_images[img_idx]
                global_idx = (st.session_state.get('current_page', 1) - 1) * page_size + img_idx
                
                with cols[col_idx]:
                    _render_image_card(img_data, global_idx, show_details)

def _render_image_card(img_data: Dict[str, Any], img_idx: int, show_details: bool) -> None:
    """Affiche une carte d'image individuelle."""
    
    try:
        # Afficher l'image
        if os.path.exists(img_data['image_path']):
            image = Image.open(img_data['image_path'])
            st.image(image, use_container_width=True)
        else:
            st.error("❌ Image non trouvée")
            st.write(f"Chemin: {img_data['image_path']}")
        
        # Afficher les détails si demandé
        if show_details:
            st.markdown(f"**📁** {os.path.basename(img_data['image_path'])}")
            
            # Description
            if img_data.get('description'):
                description = img_data['description']
                if len(description) > 80:
                    st.markdown(f"**🔍** {description[:77]}...")
                else:
                    st.markdown(f"**🔍** {description}")
            
            # Catégories
            if img_data.get('categories'):
                categories = img_data['categories']
                if len(categories) <= 3:
                    categories_str = ', '.join(categories)
                else:
                    categories_str = ', '.join(categories[:3]) + f" +{len(categories) - 3}"
                st.markdown(f"**🏷️** {categories_str}")
            
            # Texte OCR (si disponible)
            if img_data.get('text_content'):
                text_content = img_data['text_content']
                if len(text_content) > 50:
                    st.markdown(f"**📝** {text_content[:47]}...")
                else:
                    st.markdown(f"**📝** {text_content}")
            
            # Métadonnées importantes
            metadata = img_data.get('metadata', {})
            if metadata.get('project'):
                st.markdown(f"**📂** {metadata['project']}")
        
        # Bouton pour voir les détails complets
        if st.button(f"🔍 Détails", key=f"details_{img_idx}"):
            st.session_state.selected_image = img_data
            st.rerun()
    
    except Exception as e:
        st.error(f"❌ Erreur affichage image: {str(e)}")

def _show_image_details() -> None:
    """Affiche les détails de l'image sélectionnée."""
    
    if 'selected_image' not in st.session_state:
        return
    
    img_data = st.session_state.selected_image
    
    st.markdown("---")
    st.markdown("### 📋 Détails de l'Image")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        try:
            if os.path.exists(img_data['image_path']):
                image = Image.open(img_data['image_path'])
                st.image(image, width=300)
                
                # Informations techniques de l'image
                st.markdown("**📊 Informations Techniques:**")
                st.markdown(f"• **Taille:** {image.size[0]} x {image.size[1]} pixels")
                st.markdown(f"• **Mode:** {image.mode}")
                
                # Taille du fichier
                file_size = os.path.getsize(img_data['image_path'])
                if file_size < 1024 * 1024:
                    size_str = f"{file_size / 1024:.1f} KB"
                else:
                    size_str = f"{file_size / (1024 * 1024):.1f} MB"
                st.markdown(f"• **Taille fichier:** {size_str}")
            else:
                st.error("❌ Image non trouvée")
                st.write(f"Chemin: {img_data['image_path']}")
        except Exception as e:
            st.error(f"❌ Erreur affichage: {str(e)}")
    
    with col2:
        st.markdown(f"**📁 Fichier:** {os.path.basename(img_data['image_path'])}")
        st.markdown(f"**📂 Chemin:** {img_data['image_path']}")
        
        # Description complète
        if img_data.get('description'):
            st.markdown("**🔍 Description:**")
            st.text_area("", img_data['description'], height=80, key="description_detail")
        
        # Catégories
        if img_data.get('categories'):
            st.markdown(f"**🏷️ Catégories:** {', '.join(img_data['categories'])}")
        
        # Texte OCR complet
        if img_data.get('text_content'):
            st.markdown("**📝 Texte OCR:**")
            st.text_area("", img_data['text_content'], height=120, key="ocr_detail")
        
        # Métadonnées complètes
        metadata = img_data.get('metadata', {})
        if metadata:
            st.markdown("**📋 Métadonnées:**")
            for key, value in metadata.items():
                if key not in ['stored_path', 'segment_text'] and value:
                    st.markdown(f"• **{key}:** {value}")
        
        # Timestamp
        if img_data.get('timestamp'):
            st.markdown(f"**📅 Ajouté le:** {img_data['timestamp'][:19].replace('T', ' ')}")
    
    # Actions
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("❌ Fermer les détails"):
            if 'selected_image' in st.session_state:
                del st.session_state.selected_image
            st.rerun()
    
    with col2:
        if st.button("📋 Copier le chemin"):
            # Simulation de copie (dans une vraie app, vous utiliseriez le clipboard)
            st.success(f"Chemin copié: {img_data['image_path']}")
    
    with col3:
        if st.button("🔍 Rechercher similaires"):
            # Rechercher des images avec des catégories similaires
            categories = img_data.get('categories', [])
            if categories:
                st.session_state.filter_categories = categories[:2]  # Prendre les 2 premières catégories
                del st.session_state.selected_image
                st.rerun()
            else:
                st.info("Aucune catégorie pour rechercher des images similaires")
