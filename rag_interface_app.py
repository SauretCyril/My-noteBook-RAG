import streamlit as st
import json
import os
from datetime import datetime
import PyPDF2
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

# Configuration de la page
st.set_page_config(
    page_title="RAG Knowledge Base Manager",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Chemins des fichiers
DATA_DIR = "data"
KNOWLEDGE_BASE_FILE = os.path.join(DATA_DIR, "anthropic_docs.json")
BACKUP_FILE = os.path.join(DATA_DIR, "anthropic_docs.json.backup")
VECTOR_DB_FILE = os.path.join(DATA_DIR, "docs", "vector_db.pkl")

# Initialisation de NLTK
@st.cache_resource
def init_nltk():
    """Initialise les ressources NLTK nécessaires"""
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
    return True

# Classes pour la gestion vectorielle
class VectorDatabase:
    def __init__(self):
        self.documents = []
        self.vectors = None
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2)
        )
    
    def add_document(self, text, metadata):
        """Ajoute un document à la base vectorielle"""
        self.documents.append({
            'text': text,
            'metadata': metadata,
            'timestamp': datetime.now().isoformat()
        })
        self._update_vectors()
    
    def _update_vectors(self):
        """Met à jour les vecteurs TF-IDF"""
        if self.documents:
            texts = [doc['text'] for doc in self.documents]
            self.vectors = self.vectorizer.fit_transform(texts)
    
    def search(self, query, top_k=5):
        """Recherche les documents les plus similaires"""
        if not self.documents or self.vectors is None:
            return []
        
        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.vectors)[0]
        
        # Obtenir les indices des documents les plus similaires
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0:  # Seulement les résultats pertinents
                results.append({
                    'document': self.documents[idx],
                    'similarity': similarities[idx]
                })
        
        return results
    
    def save(self, filepath):
        """Sauvegarde la base vectorielle"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)
    
    @classmethod
    def load(cls, filepath):
        """Charge la base vectorielle"""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'rb') as f:
                    loaded_data = pickle.load(f)
                    # Vérifier si c'est une instance de VectorDatabase
                    if isinstance(loaded_data, cls):
                        return loaded_data
                    else:
                        # Si c'est un autre format, créer une nouvelle instance
                        st.warning("Format de base vectorielle incompatible. Création d'une nouvelle base.")
                        return cls()
            except Exception as e:
                st.error(f"Erreur lors du chargement de la base vectorielle : {e}")
                return cls()
        return cls()

# Fonctions utilitaires
def create_backup(source_file):
    """Crée une sauvegarde du fichier source"""
    if os.path.exists(source_file):
        with open(source_file, 'r', encoding='utf-8') as src:
            with open(BACKUP_FILE, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
        return True
    return False

def load_knowledge_base():
    """Charge la base de connaissances JSON"""
    if os.path.exists(KNOWLEDGE_BASE_FILE):
        try:
            with open(KNOWLEDGE_BASE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Erreur lors du chargement de la base : {e}")
            return {}
    return {}

def save_knowledge_base(data):
    """Sauvegarde la base de connaissances JSON"""
    try:
        # Créer une sauvegarde
        create_backup(KNOWLEDGE_BASE_FILE)
        
        # Créer le dossier si nécessaire
        os.makedirs(DATA_DIR, exist_ok=True)
        
        # Sauvegarder les nouvelles données
        with open(KNOWLEDGE_BASE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"Erreur lors de la sauvegarde : {e}")
        return False

def extract_text_from_pdf(pdf_file):
    """Extrait le texte d'un fichier PDF"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"Erreur lors de l'extraction du PDF : {e}")
        return None

def segment_text(text, max_length=500):
    """Segmente le texte en chunks plus petits"""
    sentences = sent_tokenize(text)
    segments = []
    current_segment = ""
    
    for sentence in sentences:
        if len(current_segment) + len(sentence) <= max_length:
            current_segment += sentence + " "
        else:
            if current_segment:
                segments.append(current_segment.strip())
            current_segment = sentence + " "
    
    if current_segment:
        segments.append(current_segment.strip())
    
    return segments

def generate_response(query, context_docs):
    """Génère une réponse basée sur les documents trouvés"""
    if not context_docs:
        return "Je n'ai pas trouvé d'informations pertinentes pour répondre à votre question."
    
    # Construire le contexte
    context = "\n\n".join([doc['document']['text'] for doc in context_docs])
    
    # Simulation d'une réponse (à remplacer par un vrai modèle)
    response = f"""Basé sur les documents de la base de connaissances, voici ma réponse :

**Contexte trouvé :**
{context[:800]}...

**Réponse :**
Je peux vous aider avec les informations trouvées dans les documents. Pour une réponse plus précise, vous pouvez intégrer un modèle de langage comme Mistral AI ou OpenAI.

**Sources utilisées :** {len(context_docs)} document(s) pertinent(s)"""
    
    return response

# Interface principale
def main():
    # Initialisation
    init_nltk()
    
    # Titre principal
    st.title("🤖 RAG Knowledge Base Manager")
    st.markdown("---")
    
    # Sidebar pour la navigation
    st.sidebar.title("📋 Menu Principal")
    page = st.sidebar.selectbox(
        "Choisissez une action :",
        ["🏠 Accueil", "🗃️ Gestion de la Base", "📄 Ajouter Documents", "❓ Poser Questions"]
    )
    
    # Chargement de la base vectorielle
    if 'vector_db' not in st.session_state:
        st.session_state.vector_db = VectorDatabase.load(VECTOR_DB_FILE)
    
    # Initialisation de l'historique des conversations
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Navigation entre les pages
    if page == "🏠 Accueil":
        show_home_page()
    elif page == "🗃️ Gestion de la Base":
        show_database_management()
    elif page == "📄 Ajouter Documents":
        show_document_upload()
    elif page == "❓ Poser Questions":
        show_question_interface()

def show_home_page():
    """Page d'accueil avec les statistiques"""
    st.header("🏠 Tableau de Bord")
    
    # Statistiques de la base
    knowledge_base = load_knowledge_base()
    vector_db = st.session_state.vector_db
    
    # Vérification de compatibilité
    if not isinstance(vector_db, VectorDatabase):
        st.warning("⚠️ Format de base vectorielle incompatible détecté. Recréation automatique...")
        st.session_state.vector_db = VectorDatabase()
        vector_db = st.session_state.vector_db
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📚 Documents JSON", len(knowledge_base))
    
    with col2:
        try:
            st.metric("🔍 Documents Vectorisés", len(vector_db.documents))
        except AttributeError:
            st.metric("🔍 Documents Vectorisés", 0)
    
    with col3:
        conversations = len(st.session_state.chat_history)
        st.metric("💬 Conversations", conversations)
    
    # Informations sur les fichiers
    st.markdown("### 📁 État des Fichiers")
    
    files_info = [
        ("Base JSON", KNOWLEDGE_BASE_FILE),
        ("Sauvegarde", BACKUP_FILE),
        ("Base Vectorielle", VECTOR_DB_FILE)
    ]
    
    for name, filepath in files_info:
        if os.path.exists(filepath):
            size = os.path.getsize(filepath) / 1024  # KB
            st.success(f"✅ {name}: {size:.1f} KB")
        else:
            st.warning(f"⚠️ {name}: Non trouvé")
    
    # Instructions rapides
    st.markdown("### 🚀 Démarrage Rapide")
    st.markdown("""
    1. **Gestion de la Base** : Créez ou réinitialisez votre base vectorielle
    2. **Ajouter Documents** : Uploadez des PDF pour enrichir votre base
    3. **Poser Questions** : Interrogez votre base de connaissances
    """)

def show_database_management():
    """Interface de gestion de la base vectorielle"""
    st.header("🗃️ Gestion de la Base Vectorielle")
    
    vector_db = st.session_state.vector_db
    
    # Vérification de compatibilité
    if not isinstance(vector_db, VectorDatabase):
        st.error("⚠️ Format de base vectorielle incompatible détecté. Création d'une nouvelle base...")
        st.session_state.vector_db = VectorDatabase()
        vector_db = st.session_state.vector_db
    
    # Informations sur la base actuelle
    st.markdown("### 📊 Statistiques Actuelles")
    col1, col2 = st.columns(2)
    
    with col1:
        try:
            st.info(f"📄 Documents stockés : {len(vector_db.documents)}")
        except AttributeError:
            st.error("Erreur de format de base. Recréation en cours...")
            st.session_state.vector_db = VectorDatabase()
            vector_db = st.session_state.vector_db
            st.info(f"📄 Documents stockés : {len(vector_db.documents)}")
    
    with col2:
        if vector_db.vectors is not None:
            st.info(f"🔢 Dimensions vectorielles : {vector_db.vectors.shape}")
        else:
            st.info("🔢 Pas de vecteurs générés")
    
    # Actions de gestion
    st.markdown("### ⚙️ Actions de Gestion")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🆕 Créer Nouvelle Base", type="primary"):
            st.session_state.vector_db = VectorDatabase()
            st.success("✅ Nouvelle base vectorielle créée !")
            st.rerun()
    
    with col2:
        if st.button("💾 Sauvegarder Base"):
            st.session_state.vector_db.save(VECTOR_DB_FILE)
            st.success("✅ Base sauvegardée avec succès !")
    
    with col3:
        if st.button("🔄 Recharger Base"):
            st.session_state.vector_db = VectorDatabase.load(VECTOR_DB_FILE)
            st.success("✅ Base rechargée !")
            st.rerun()
    
    # Affichage des documents
    if vector_db.documents:
        st.markdown("### 📚 Documents dans la Base")
        for i, doc in enumerate(vector_db.documents):
            with st.expander(f"Document {i+1} - {doc['metadata'].get('title', 'Sans titre')}"):
                st.markdown(f"**Source:** {doc['metadata'].get('source', 'Inconnue')}")
                st.markdown(f"**Date:** {doc['timestamp']}")
                st.text_area("Contenu:", doc['text'][:500] + "..." if len(doc['text']) > 500 else doc['text'], height=100)

def show_document_upload():
    """Interface pour ajouter des documents"""
    st.header("📄 Ajouter des Documents")
    
    # Upload de fichiers
    uploaded_files = st.file_uploader(
        "Choisissez vos fichiers PDF",
        type=['pdf'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            st.markdown(f"### 📎 Traitement de : {uploaded_file.name}")
            
            # Extraction du texte
            with st.spinner("Extraction du texte..."):
                text = extract_text_from_pdf(uploaded_file)
            
            if text:
                st.success(f"✅ Texte extrait : {len(text)} caractères")
                
                # Prévisualisation
                with st.expander("👀 Prévisualisation du texte"):
                    st.text_area("Contenu extrait:", text[:1000] + "..." if len(text) > 1000 else text, height=200)
                
                # Options de segmentation
                col1, col2 = st.columns(2)
                with col1:
                    max_segment_length = st.slider("Taille max des segments", 200, 1000, 500)
                with col2:
                    title = st.text_input("Titre du document", value=uploaded_file.name)
                
                # Bouton d'ajout
                if st.button(f"➕ Ajouter {uploaded_file.name} à la base", key=f"add_{uploaded_file.name}"):
                    with st.spinner("Ajout en cours..."):
                        # Vérification de la base vectorielle
                        vector_db = st.session_state.vector_db
                        if not isinstance(vector_db, VectorDatabase):
                            st.warning("⚠️ Recréation de la base vectorielle...")
                            st.session_state.vector_db = VectorDatabase()
                            vector_db = st.session_state.vector_db
                        
                        # Segmentation
                        segments = segment_text(text, max_segment_length)
                        
                        # Ajout à la base vectorielle
                        vector_db = st.session_state.vector_db
                        for i, segment in enumerate(segments):
                            metadata = {
                                'title': title,
                                'source': uploaded_file.name,
                                'segment': i + 1,
                                'total_segments': len(segments)
                            }
                            vector_db.add_document(segment, metadata)
                        
                        # Ajout à la base JSON
                        knowledge_base = load_knowledge_base()
                        doc_id = f"doc_{len(knowledge_base) + 1}"
                        knowledge_base[doc_id] = {
                            'title': title,
                            'source': uploaded_file.name,
                            'content': text,
                            'segments': segments,
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        # Sauvegarde
                        if save_knowledge_base(knowledge_base):
                            vector_db.save(VECTOR_DB_FILE)
                            st.success(f"✅ Document ajouté avec succès ! ({len(segments)} segments créés)")
                        else:
                            st.error("❌ Erreur lors de la sauvegarde")
            else:
                st.error("❌ Impossible d'extraire le texte du PDF")

def show_question_interface():
    """Interface pour poser des questions"""
    st.header("❓ Poser des Questions")
    
    vector_db = st.session_state.vector_db
    
    # Vérification de compatibilité
    if not isinstance(vector_db, VectorDatabase):
        st.error("⚠️ Format de base vectorielle incompatible détecté. Création d'une nouvelle base...")
        st.session_state.vector_db = VectorDatabase()
        vector_db = st.session_state.vector_db
    
    if not vector_db.documents:
        st.warning("⚠️ Aucun document dans la base. Ajoutez d'abord des documents.")
        return
    
    # Interface de chat
    st.markdown("### 💬 Chat avec votre Base de Connaissances")
    
    # Affichage de l'historique
    for i, (question, answer) in enumerate(st.session_state.chat_history):
        st.markdown(f"**👤 Question {i+1}:** {question}")
        st.markdown(f"**🤖 Réponse:** {answer}")
        st.markdown("---")
    
    # Nouvelle question
    question = st.text_input("🔍 Posez votre question :", placeholder="Ex: Quelles sont les compétences mentionnées dans les CV ?")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🚀 Rechercher", type="primary"):
            if question:
                with st.spinner("Recherche en cours..."):
                    # Recherche dans la base vectorielle
                    results = vector_db.search(question, top_k=5)
                    
                    if results:
                        # Génération de la réponse
                        response = generate_response(question, results)
                        
                        # Ajout à l'historique
                        st.session_state.chat_history.append((question, response))
                        
                        # Affichage de la réponse
                        st.markdown("### 🤖 Réponse")
                        st.markdown(response)
                        
                        # Affichage des sources
                        st.markdown("### 📚 Sources Utilisées")
                        for i, result in enumerate(results):
                            doc = result['document']
                            similarity = result['similarity']
                            with st.expander(f"Source {i+1} - Similarité: {similarity:.3f}"):
                                st.markdown(f"**Titre:** {doc['metadata'].get('title', 'Sans titre')}")
                                st.markdown(f"**Source:** {doc['metadata'].get('source', 'Inconnue')}")
                                st.text_area("Contenu:", doc['text'], height=100)
                    else:
                        st.warning("Aucun résultat trouvé pour votre question.")
    
    with col2:
        if st.button("🗑️ Effacer Historique"):
            st.session_state.chat_history = []
            st.success("Historique effacé !")
            st.rerun()
    
    # Paramètres de recherche
    with st.expander("⚙️ Paramètres de Recherche"):
        top_k = st.slider("Nombre de résultats", 1, 10, 5)
        min_similarity = st.slider("Similarité minimale", 0.0, 1.0, 0.1)

if __name__ == "__main__":
    main()
