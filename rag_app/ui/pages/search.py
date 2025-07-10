"""Page de recherche avancée."""

import streamlit as st
from typing import List, Dict, Any

def show() -> None:
    """Affiche la page de recherche avancée."""
    
    st.header("🔍 Recherche Avancée")
    
    if 'vector_db' not in st.session_state:
        st.error("⚠️ Base vectorielle non initialisée")
        return
        
    vector_db = st.session_state.vector_db
    
    if not vector_db.documents:
        _show_empty_search()
        return
    
    # Interface de recherche
    _show_search_interface(vector_db)
    
    # Affichage des résultats
    _show_search_results()

def _show_empty_search() -> None:
    """Affiche l'état vide de la recherche."""
    
    st.warning("⚠️ Aucun document dans la base.")
    
    st.markdown("""
    ### 🚀 Pour commencer :
    
    1. **📁 Traitement par Lots** : Ajoutez des documents via le traitement par lots
    2. **🗃️ Gestion Base** : Créez ou rechargez une base existante
    3. **📄 Upload Direct** : Interface d'upload à venir dans la v2.1
    """)
    
    if st.button("📁 Aller au Traitement par Lots", type="primary"):
        st.session_state.page_redirect = "batch"
        st.rerun()

def _show_search_interface(vector_db) -> None:
    """Affiche l'interface de recherche."""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔍 Recherche Textuelle")
        search_query = st.text_input(
            "Rechercher dans le contenu:",
            placeholder="Ex: projet, développement, analyse..."
        )
        st.session_state.search_query = search_query
        
        st.markdown("### 🏷️ Filtres")
        
        # Filtrage par catégories
        categories = vector_db.get_categories()
        selected_categories = st.multiselect(
            "Catégories:", 
            categories,
            default=st.session_state.get('selected_categories', [])
        )
        st.session_state.selected_categories = selected_categories
        
        # Filtrage par projets
        projects = vector_db.get_projects()
        selected_projects = st.multiselect(
            "Projets:", 
            projects,
            default=st.session_state.get('selected_projects', [])
        )
        st.session_state.selected_projects = selected_projects
        
        # Type de contenu
        content_types = _get_content_types(vector_db)
        selected_types = st.multiselect(
            "Type de contenu:",
            content_types,
            default=st.session_state.get('selected_types', [])
        )
        st.session_state.selected_types = selected_types
    
    with col2:
        st.markdown("### ⚙️ Options de Recherche")
        
        max_results = st.slider(
            "Nombre de résultats", 
            1, 50, 
            st.session_state.get('max_results', 10)
        )
        st.session_state.max_results = max_results
        
        min_similarity = st.slider(
            "Similarité minimale", 
            0.0, 1.0, 
            st.session_state.get('min_similarity', 0.1),
            step=0.05
        )
        st.session_state.min_similarity = min_similarity
        
        # Options d'affichage
        st.markdown("### 📊 Affichage")
        
        show_snippets = st.checkbox(
            "Afficher les extraits", 
            value=st.session_state.get('show_snippets', True)
        )
        st.session_state.show_snippets = show_snippets
        
        sort_by = st.selectbox(
            "Trier par:",
            ["Similarité", "Date", "Taille", "Source"],
            index=0
        )
        st.session_state.sort_by = sort_by
    
    # Boutons de recherche
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_button = st.button("🔍 Rechercher", type="primary")
    
    with col2:
        if st.button("🔄 Réinitialiser"):
            _reset_search_state()
            st.rerun()
    
    with col3:
        if st.button("💾 Sauvegarder recherche"):
            _save_search_query()
    
    # Lancer la recherche
    if search_button and search_query:
        _perform_search(vector_db)

def _get_content_types(vector_db) -> List[str]:
    """Récupère les types de contenu disponibles."""
    types = set()
    for doc in vector_db.documents:
        doc_type = doc.get('type', 'document')
        types.add(doc_type)
        
        # Ajouter aussi les types basés sur les métadonnées
        metadata = doc.get('metadata', {})
        if metadata.get('type'):
            types.add(metadata['type'])
    
    return sorted(list(types))

def _perform_search(vector_db) -> None:
    """Effectue la recherche avec les paramètres actuels."""
    
    search_query = st.session_state.get('search_query', '')
    selected_categories = st.session_state.get('selected_categories', [])
    selected_projects = st.session_state.get('selected_projects', [])
    selected_types = st.session_state.get('selected_types', [])
    max_results = st.session_state.get('max_results', 10)
    min_similarity = st.session_state.get('min_similarity', 0.1)
    
    # Construire les filtres
    filters = {}
    if selected_categories:
        filters['category'] = selected_categories
    if selected_projects:
        filters['project'] = selected_projects
    if selected_types:
        filters['type'] = selected_types
    
    # Effectuer la recherche
    with st.spinner("Recherche en cours..."):
        try:
            results = vector_db.search(
                search_query, 
                top_k=max_results, 
                filter_by=filters if filters else None
            )
            
            # Filtrer par similarité
            filtered_results = [r for r in results if r['similarity'] >= min_similarity]
            
            # Trier les résultats
            sort_by = st.session_state.get('sort_by', 'Similarité')
            filtered_results = _sort_results(filtered_results, sort_by)
            
            # Stocker les résultats
            st.session_state.search_results = filtered_results
            st.session_state.has_searched = True
            
        except Exception as e:
            st.error(f"Erreur lors de la recherche: {str(e)}")
            st.session_state.search_results = []

def _sort_results(results: List[Dict], sort_by: str) -> List[Dict]:
    """Trie les résultats selon le critère choisi."""
    
    if sort_by == "Similarité":
        return sorted(results, key=lambda x: x['similarity'], reverse=True)
    elif sort_by == "Date":
        return sorted(results, key=lambda x: x['document'].get('timestamp', ''), reverse=True)
    elif sort_by == "Taille":
        return sorted(results, key=lambda x: len(x['document'].get('text', '')), reverse=True)
    elif sort_by == "Source":
        return sorted(results, key=lambda x: x['document'].get('metadata', {}).get('source', ''))
    
    return results

def _show_search_results() -> None:
    """Affiche les résultats de recherche."""
    
    if not st.session_state.get('has_searched', False):
        return
    
    results = st.session_state.get('search_results', [])
    
    if not results:
        st.info("🔍 Aucun résultat trouvé avec ces critères.")
        return
    
    st.markdown(f"### 📊 Résultats ({len(results)})")
    
    show_snippets = st.session_state.get('show_snippets', True)
    
    # Pagination
    page_size = 5
    total_pages = (len(results) + page_size - 1) // page_size
    
    if total_pages > 1:
        page = st.selectbox(
            "Page des résultats:",
            range(1, total_pages + 1),
            format_func=lambda x: f"Page {x}/{total_pages}"
        )
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_results = results[start_idx:end_idx]
    else:
        page_results = results
    
    # Afficher les résultats
    for i, result in enumerate(page_results):
        doc = result['document']
        metadata = doc.get('metadata', {})
        similarity = result['similarity']
        
        with st.expander(
            f"📄 Résultat {i+1} - {metadata.get('title', metadata.get('source', 'Sans titre'))} - Score: {similarity:.3f}",
            expanded=i == 0
        ):
            _render_search_result(doc, metadata, similarity, show_snippets)

def _render_search_result(doc: Dict, metadata: Dict, similarity: float, show_snippets: bool) -> None:
    """Affiche un résultat de recherche individuel."""
    
    # Métadonnées en colonnes
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**📁 Source:** {metadata.get('source', 'N/A')}")
        st.markdown(f"**🏷️ Catégorie:** {metadata.get('category', 'N/A')}")
        st.markdown(f"**📋 Projet:** {metadata.get('project', 'N/A')}")
        st.markdown(f"**📊 Similarité:** {similarity:.3f}")
    
    with col2:
        st.markdown(f"**👤 Auteur:** {metadata.get('author', 'N/A')}")
        st.markdown(f"**📅 Date:** {doc.get('timestamp', 'N/A')[:10]}")
        st.markdown(f"**📝 Taille:** {len(doc.get('text', ''))} caractères")
        st.markdown(f"**🔗 Type:** {doc.get('type', 'document')}")
    
    # Description si disponible
    if metadata.get('description'):
        st.markdown(f"**📝 Description:** {metadata['description']}")
    
    # Extrait de contenu
    if show_snippets:
        text = doc.get('text', '')
        if text:
            # Essayer de trouver un extrait pertinent autour de la recherche
            search_query = st.session_state.get('search_query', '')
            snippet = _get_text_snippet(text, search_query)
            
            st.markdown("**📄 Extrait:**")
            st.text_area("", snippet, height=100, key=f"snippet_{id(doc)}")
    
    # Actions
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(f"📄 Voir le texte complet", key=f"full_text_{id(doc)}"):
            st.session_state[f"show_full_{id(doc)}"] = True
    
    with col2:
        if st.button(f"🔍 Rechercher similaires", key=f"similar_{id(doc)}"):
            # Lancer une recherche avec des termes extraits de ce document
            _search_similar_documents(doc)
    
    with col3:
        if st.button(f"📋 Copier contenu", key=f"copy_{id(doc)}"):
            st.success("Contenu copié dans le presse-papier (simulation)")
    
    # Affichage du texte complet si demandé
    if st.session_state.get(f"show_full_{id(doc)}", False):
        st.markdown("**📄 Texte complet:**")
        st.text_area("", doc.get('text', ''), height=300, key=f"full_{id(doc)}")
        
        if st.button(f"❌ Masquer", key=f"hide_{id(doc)}"):
            st.session_state[f"show_full_{id(doc)}"] = False
            st.rerun()

def _get_text_snippet(text: str, search_query: str, snippet_length: int = 300) -> str:
    """Extrait un snippet pertinent du texte."""
    
    if not search_query:
        return text[:snippet_length] + "..." if len(text) > snippet_length else text
    
    # Chercher la première occurrence de la requête
    query_lower = search_query.lower()
    text_lower = text.lower()
    
    start_pos = text_lower.find(query_lower)
    
    if start_pos == -1:
        # Requête non trouvée, retourner le début
        return text[:snippet_length] + "..." if len(text) > snippet_length else text
    
    # Centrer l'extrait autour de la position trouvée
    snippet_start = max(0, start_pos - snippet_length // 2)
    snippet_end = min(len(text), snippet_start + snippet_length)
    
    snippet = text[snippet_start:snippet_end]
    
    # Ajouter des ellipses si nécessaire
    if snippet_start > 0:
        snippet = "..." + snippet
    if snippet_end < len(text):
        snippet = snippet + "..."
    
    return snippet

def _search_similar_documents(doc: Dict) -> None:
    """Lance une recherche de documents similaires."""
    
    # Extraire des mots-clés du document
    text = doc.get('text', '')
    words = text.split()[:10]  # Prendre les 10 premiers mots comme requête
    similar_query = ' '.join(words)
    
    st.session_state.search_query = similar_query
    st.session_state.has_searched = False  # Forcer une nouvelle recherche
    st.rerun()

def _reset_search_state() -> None:
    """Remet à zéro l'état de recherche."""
    
    keys_to_reset = [
        'search_query', 'selected_categories', 'selected_projects', 
        'selected_types', 'search_results', 'has_searched'
    ]
    
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]

def _save_search_query() -> None:
    """Sauvegarde la requête de recherche actuelle."""
    
    search_params = {
        'query': st.session_state.get('search_query', ''),
        'categories': st.session_state.get('selected_categories', []),
        'projects': st.session_state.get('selected_projects', []),
        'types': st.session_state.get('selected_types', []),
        'max_results': st.session_state.get('max_results', 10),
        'min_similarity': st.session_state.get('min_similarity', 0.1)
    }
    
    # Sauvegarder dans session state (dans une vraie app, on sauvegarderait en base)
    if 'saved_searches' not in st.session_state:
        st.session_state.saved_searches = []
    
    st.session_state.saved_searches.append(search_params)
    st.success("🔖 Recherche sauvegardée !")
