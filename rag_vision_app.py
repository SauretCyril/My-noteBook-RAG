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
from PIL import Image
import pytesseract
import requests
import base64
import io
import cv2
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch

# Configuration de la page
st.set_page_config(
    page_title="RAG Knowledge Base Manager + Vision",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Chemins des fichiers
DATA_DIR = "data"
KNOWLEDGE_BASE_FILE = os.path.join(DATA_DIR, "anthropic_docs.json")
BACKUP_FILE = os.path.join(DATA_DIR, "anthropic_docs.json.backup")
VECTOR_DB_FILE = os.path.join(DATA_DIR, "docs", "vector_db.pkl")
IMAGES_DIR = os.path.join(DATA_DIR, "images")

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

# Initialisation du modèle de vision
@st.cache_resource
def init_vision_model():
    """Initialise le modèle de description d'images BLIP"""
    try:
        processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        return processor, model
    except Exception as e:
        st.error(f"Erreur lors du chargement du modèle de vision : {e}")
        return None, None

# Fonctions de traitement d'images
def extract_text_from_image(image):
    """Extrait le texte d'une image avec OCR"""
    try:
        # Convertir en OpenCV format pour améliorer la qualité OCR
        img_array = np.array(image)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Améliorer la qualité pour l'OCR
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Extraire le texte
        text = pytesseract.image_to_string(thresh, lang='fra+eng')
        return text.strip()
    except Exception as e:
        st.error(f"Erreur OCR : {e}")
        return ""

def generate_image_description(image, processor, model):
    """Génère une description automatique de l'image"""
    try:
        if processor is None or model is None:
            return "Modèle de vision non disponible"
        
        # Préparer l'image
        inputs = processor(image, return_tensors="pt")
        
        # Générer la description
        with torch.no_grad():
            out = model.generate(**inputs, max_length=100, num_beams=5)
        
        # Décoder le résultat
        description = processor.decode(out[0], skip_special_tokens=True)
        return description
    except Exception as e:
        st.error(f"Erreur génération description : {e}")
        return "Erreur lors de la génération de la description"

def classify_image_content(image, text_content="", description=""):
    """Classifie le contenu de l'image en catégories"""
    categories = []
    
    # Classification basée sur le texte extrait
    if text_content:
        text_lower = text_content.lower()
        if any(word in text_lower for word in ['facture', 'invoice', 'total', 'prix', 'montant']):
            categories.append('Document financier')
        if any(word in text_lower for word in ['certificat', 'diplome', 'formation', 'université']):
            categories.append('Document éducatif')
        if any(word in text_lower for word in ['contrat', 'accord', 'signature', 'conditions']):
            categories.append('Document juridique')
    
    # Classification basée sur la description visuelle
    if description:
        desc_lower = description.lower()
        if any(word in desc_lower for word in ['person', 'people', 'man', 'woman', 'face']):
            categories.append('Portrait/Personne')
        if any(word in desc_lower for word in ['building', 'house', 'architecture', 'room']):
            categories.append('Architecture/Bâtiment')
        if any(word in desc_lower for word in ['nature', 'tree', 'flower', 'landscape', 'outdoor']):
            categories.append('Nature/Paysage')
        if any(word in desc_lower for word in ['car', 'vehicle', 'transport', 'road']):
            categories.append('Transport/Véhicule')
        if any(word in desc_lower for word in ['food', 'meal', 'kitchen', 'restaurant']):
            categories.append('Nourriture/Cuisine')
        if any(word in desc_lower for word in ['document', 'text', 'paper', 'book']):
            categories.append('Document/Texte')
        if any(word in desc_lower for word in ['chart', 'graph', 'diagram', 'table']):
            categories.append('Graphique/Schéma')
    
    return categories if categories else ['Non classifié']

def save_image_to_storage(image, filename):
    """Sauvegarde l'image dans le dossier de stockage"""
    try:
        os.makedirs(IMAGES_DIR, exist_ok=True)
        filepath = os.path.join(IMAGES_DIR, filename)
        image.save(filepath)
        return filepath
    except Exception as e:
        st.error(f"Erreur sauvegarde image : {e}")
        return None

# Classes étendues pour la gestion vectorielle avec images
class VectorDatabase:
    def __init__(self):
        self.documents = []
        self.images = []  # Nouvelle liste pour les images
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
            'timestamp': datetime.now().isoformat(),
            'type': 'document'
        })
        self._update_vectors()
    
    def add_image(self, image_path, text_content, description, categories, metadata):
        """Ajoute une image à la base vectorielle"""
        # Créer un texte composite pour la recherche
        search_text = f"{text_content} {description} {' '.join(categories)}"
        
        image_data = {
            'image_path': image_path,
            'text_content': text_content,
            'description': description,
            'categories': categories,
            'metadata': metadata,
            'timestamp': datetime.now().isoformat(),
            'type': 'image',
            'search_text': search_text
        }
        
        self.images.append(image_data)
        
        # Ajouter aussi au documents pour la recherche textuelle
        self.documents.append({
            'text': search_text,
            'metadata': {**metadata, 'type': 'image', 'image_path': image_path},
            'timestamp': datetime.now().isoformat(),
            'type': 'image'
        })
        
        self._update_vectors()
    
    def _update_vectors(self):
        """Met à jour les vecteurs TF-IDF"""
        if self.documents:
            texts = [doc['text'] for doc in self.documents]
            self.vectors = self.vectorizer.fit_transform(texts)
    
    def search(self, query, top_k=5, filter_type=None):
        """Recherche les documents/images les plus similaires"""
        if not self.documents or self.vectors is None:
            return []
        
        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.vectors)[0]
        
        # Obtenir les indices des documents les plus similaires
        top_indices = np.argsort(similarities)[::-1][:top_k * 2]  # Plus large pour filtrer
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0:  # Seulement les résultats pertinents
                doc = self.documents[idx]
                
                # Filtrer par type si spécifié
                if filter_type and doc.get('type') != filter_type:
                    continue
                
                results.append({
                    'document': doc,
                    'similarity': similarities[idx]
                })
                
                if len(results) >= top_k:
                    break
        
        return results
    
    def get_image_by_categories(self, categories):
        """Récupère les images par catégories"""
        results = []
        for img in self.images:
            if any(cat in img['categories'] for cat in categories):
                results.append(img)
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
                        # Vérifier si les attributs images existent
                        if not hasattr(loaded_data, 'images'):
                            loaded_data.images = []
                        return loaded_data
                    else:
                        # Si c'est un autre format, créer une nouvelle instance
                        st.warning("Format de base vectorielle incompatible. Création d'une nouvelle base.")
                        return cls()
            except Exception as e:
                st.error(f"Erreur lors du chargement de la base vectorielle : {e}")
                return cls()
        return cls()

# Fonctions utilitaires existantes (identiques)
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
    
    # Séparer les documents et images
    text_docs = [doc for doc in context_docs if doc['document'].get('type') != 'image']
    image_docs = [doc for doc in context_docs if doc['document'].get('type') == 'image']
    
    # Construire le contexte textuel
    context = "\n\n".join([doc['document']['text'] for doc in text_docs])
    
    # Construire la réponse
    response = f"""Basé sur les documents de la base de connaissances, voici ma réponse :

**Contexte textuel trouvé :**
{context[:800]}...

**Images pertinentes trouvées :** {len(image_docs)}

**Réponse :**
Je peux vous aider avec les informations trouvées dans les documents et images. Pour une réponse plus précise, vous pouvez intégrer un modèle de langage comme Mistral AI ou OpenAI.

**Sources utilisées :** {len(context_docs)} élément(s) pertinent(s) ({len(text_docs)} documents, {len(image_docs)} images)"""
    
    return response, image_docs

# Interface principale
def main():
    # Initialisation
    init_nltk()
    
    # Titre principal
    st.title("🤖 RAG Knowledge Base Manager + Vision")
    st.markdown("---")
    
    # Sidebar pour la navigation
    st.sidebar.title("📋 Menu Principal")
    page = st.sidebar.selectbox(
        "Choisissez une action :",
        [
            "🏠 Accueil", 
            "🗃️ Gestion de la Base", 
            "📄 Ajouter Documents", 
            "🖼️ Ajouter Images",
            "❓ Poser Questions",
            "🔍 Recherche d'Images"
        ]
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
    elif page == "🖼️ Ajouter Images":
        show_image_upload()
    elif page == "❓ Poser Questions":
        show_question_interface()
    elif page == "🔍 Recherche d'Images":
        show_image_search()

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
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📚 Documents JSON", len(knowledge_base))
    
    with col2:
        try:
            text_docs = [doc for doc in vector_db.documents if doc.get('type') != 'image']
            st.metric("📄 Documents Texte", len(text_docs))
        except AttributeError:
            st.metric("📄 Documents Texte", 0)
    
    with col3:
        try:
            st.metric("🖼️ Images", len(vector_db.images))
        except AttributeError:
            st.metric("🖼️ Images", 0)
    
    with col4:
        conversations = len(st.session_state.chat_history)
        st.metric("💬 Conversations", conversations)
    
    # Informations sur les fichiers
    st.markdown("### 📁 État des Fichiers")
    
    files_info = [
        ("Base JSON", KNOWLEDGE_BASE_FILE),
        ("Sauvegarde", BACKUP_FILE),
        ("Base Vectorielle", VECTOR_DB_FILE),
        ("Dossier Images", IMAGES_DIR)
    ]
    
    for name, filepath in files_info:
        if os.path.exists(filepath):
            if os.path.isdir(filepath):
                count = len(os.listdir(filepath)) if os.path.exists(filepath) else 0
                st.success(f"✅ {name}: {count} fichier(s)")
            else:
                size = os.path.getsize(filepath) / 1024  # KB
                st.success(f"✅ {name}: {size:.1f} KB")
        else:
            st.warning(f"⚠️ {name}: Non trouvé")
    
    # Instructions rapides
    st.markdown("### 🚀 Démarrage Rapide")
    st.markdown("""
    1. **Gestion de la Base** : Créez ou réinitialisez votre base vectorielle
    2. **Ajouter Documents** : Uploadez des PDF pour enrichir votre base
    3. **Ajouter Images** : Uploadez des images PNG/JPG avec classification automatique
    4. **Poser Questions** : Interrogez votre base multimodale
    5. **Recherche d'Images** : Trouvez des images par catégories ou contenu
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
    col1, col2, col3 = st.columns(3)
    
    with col1:
        try:
            text_docs = [doc for doc in vector_db.documents if doc.get('type') != 'image']
            st.info(f"📄 Documents texte : {len(text_docs)}")
        except AttributeError:
            st.error("Erreur de format de base. Recréation en cours...")
            st.session_state.vector_db = VectorDatabase()
            vector_db = st.session_state.vector_db
            st.info(f"📄 Documents texte : 0")
    
    with col2:
        try:
            st.info(f"🖼️ Images : {len(vector_db.images)}")
        except AttributeError:
            vector_db.images = []
            st.info(f"🖼️ Images : 0")
    
    with col3:
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

def show_document_upload():
    """Interface pour ajouter des documents (identique à l'original)"""
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

def show_image_upload():
    """Interface pour ajouter des images"""
    st.header("🖼️ Ajouter des Images")
    
    # Charger le modèle de vision
    processor, model = init_vision_model()
    
    # Upload d'images
    uploaded_files = st.file_uploader(
        "Choisissez vos images PNG/JPG",
        type=['png', 'jpg', 'jpeg'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            st.markdown(f"### 🖼️ Traitement de : {uploaded_file.name}")
            
            # Charger l'image
            image = Image.open(uploaded_file)
            
            # Afficher l'image
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(image, caption=uploaded_file.name, use_column_width=True)
            
            with col2:
                # Traitement de l'image
                with st.spinner("Analyse de l'image..."):
                    # OCR - Extraction de texte
                    text_content = extract_text_from_image(image)
                    
                    # Description automatique
                    description = generate_image_description(image, processor, model)
                    
                    # Classification
                    categories = classify_image_content(image, text_content, description)
                
                # Affichage des résultats
                st.markdown("**📝 Texte extrait (OCR):**")
                st.text_area("", text_content[:300] + "..." if len(text_content) > 300 else text_content, height=80)
                
                st.markdown("**🔍 Description automatique:**")
                st.write(description)
                
                st.markdown("**🏷️ Catégories détectées:**")
                for cat in categories:
                    st.badge(cat)
            
            # Options d'ajout
            st.markdown("### ⚙️ Options d'Ajout")
            col1, col2 = st.columns(2)
            
            with col1:
                custom_title = st.text_input("Titre personnalisé", value=uploaded_file.name.split('.')[0])
                custom_tags = st.text_input("Tags supplémentaires (séparés par des virgules)", "")
            
            with col2:
                custom_description = st.text_area("Description personnalisée", description, height=100)
            
            # Bouton d'ajout
            if st.button(f"➕ Ajouter {uploaded_file.name} à la base", key=f"add_img_{uploaded_file.name}"):
                with st.spinner("Ajout en cours..."):
                    # Vérification de la base vectorielle
                    vector_db = st.session_state.vector_db
                    if not isinstance(vector_db, VectorDatabase):
                        st.warning("⚠️ Recréation de la base vectorielle...")
                        st.session_state.vector_db = VectorDatabase()
                        vector_db = st.session_state.vector_db
                    
                    # Sauvegarder l'image
                    image_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}"
                    image_path = save_image_to_storage(image, image_filename)
                    
                    if image_path:
                        # Préparer les métadonnées
                        all_categories = categories.copy()
                        if custom_tags:
                            all_categories.extend([tag.strip() for tag in custom_tags.split(',')])
                        
                        metadata = {
                            'title': custom_title,
                            'source': uploaded_file.name,
                            'original_filename': uploaded_file.name,
                            'file_size': len(uploaded_file.getvalue()),
                            'image_format': image.format,
                            'image_size': image.size
                        }
                        
                        # Ajouter à la base vectorielle
                        vector_db.add_image(
                            image_path=image_path,
                            text_content=text_content,
                            description=custom_description,
                            categories=all_categories,
                            metadata=metadata
                        )
                        
                        # Ajouter à la base JSON
                        knowledge_base = load_knowledge_base()
                        img_id = f"img_{len(knowledge_base) + 1}"
                        knowledge_base[img_id] = {
                            'title': custom_title,
                            'source': uploaded_file.name,
                            'image_path': image_path,
                            'text_content': text_content,
                            'description': custom_description,
                            'categories': all_categories,
                            'metadata': metadata,
                            'timestamp': datetime.now().isoformat(),
                            'type': 'image'
                        }
                        
                        # Sauvegarde
                        if save_knowledge_base(knowledge_base):
                            vector_db.save(VECTOR_DB_FILE)
                            st.success(f"✅ Image ajoutée avec succès ! Catégories: {', '.join(all_categories)}")
                        else:
                            st.error("❌ Erreur lors de la sauvegarde")
                    else:
                        st.error("❌ Erreur lors de la sauvegarde de l'image")

def show_question_interface():
    """Interface pour poser des questions (étendue pour les images)"""
    st.header("❓ Poser des Questions")
    
    vector_db = st.session_state.vector_db
    
    # Vérification de compatibilité
    if not isinstance(vector_db, VectorDatabase):
        st.error("⚠️ Format de base vectorielle incompatible détecté. Création d'une nouvelle base...")
        st.session_state.vector_db = VectorDatabase()
        vector_db = st.session_state.vector_db
    
    if not vector_db.documents:
        st.warning("⚠️ Aucun document dans la base. Ajoutez d'abord des documents ou images.")
        return
    
    # Interface de chat
    st.markdown("### 💬 Chat avec votre Base de Connaissances")
    
    # Affichage de l'historique
    for i, (question, answer, images) in enumerate(st.session_state.chat_history):
        st.markdown(f"**👤 Question {i+1}:** {question}")
        st.markdown(f"**🤖 Réponse:** {answer}")
        
        # Afficher les images associées
        if images:
            st.markdown("**🖼️ Images associées:**")
            cols = st.columns(min(3, len(images)))
            for j, img_doc in enumerate(images):
                with cols[j % 3]:
                    img_path = img_doc['document']['metadata']['image_path']
                    if os.path.exists(img_path):
                        img = Image.open(img_path)
                        st.image(img, caption=img_doc['document']['metadata']['title'], use_column_width=True)
        
        st.markdown("---")
    
    # Nouvelle question
    col1, col2 = st.columns([3, 1])
    with col1:
        question = st.text_input("🔍 Posez votre question :", placeholder="Ex: Montre-moi les documents financiers ou les images de nature")
    
    with col2:
        search_filter = st.selectbox("Filtrer par:", ["Tout", "Documents", "Images"])
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🚀 Rechercher", type="primary"):
            if question:
                with st.spinner("Recherche en cours..."):
                    # Déterminer le filtre
                    filter_type = None
                    if search_filter == "Documents":
                        filter_type = "document"
                    elif search_filter == "Images":
                        filter_type = "image"
                    
                    # Recherche dans la base vectorielle
                    results = vector_db.search(question, top_k=5, filter_type=filter_type)
                    
                    if results:
                        # Génération de la réponse
                        response, image_docs = generate_response(question, results)
                        
                        # Ajout à l'historique
                        st.session_state.chat_history.append((question, response, image_docs))
                        
                        # Affichage de la réponse
                        st.markdown("### 🤖 Réponse")
                        st.markdown(response)
                        
                        # Affichage des images
                        if image_docs:
                            st.markdown("### 🖼️ Images Trouvées")
                            cols = st.columns(min(3, len(image_docs)))
                            for j, img_doc in enumerate(image_docs):
                                with cols[j % 3]:
                                    img_path = img_doc['document']['metadata']['image_path']
                                    if os.path.exists(img_path):
                                        img = Image.open(img_path)
                                        st.image(img, caption=img_doc['document']['metadata']['title'], use_column_width=True)
                                        st.caption(f"Similarité: {img_doc['similarity']:.3f}")
                        
                        # Affichage des sources
                        st.markdown("### 📚 Sources Utilisées")
                        for i, result in enumerate(results):
                            doc = result['document']
                            similarity = result['similarity']
                            doc_type = doc.get('type', 'document')
                            
                            with st.expander(f"Source {i+1} - {doc_type.title()} - Similarité: {similarity:.3f}"):
                                st.markdown(f"**Titre:** {doc['metadata'].get('title', 'Sans titre')}")
                                st.markdown(f"**Source:** {doc['metadata'].get('source', 'Inconnue')}")
                                if doc_type == 'image':
                                    st.markdown(f"**Catégories:** {', '.join(doc['metadata'].get('categories', []))}")
                                st.text_area("Contenu:", doc['text'], height=100)
                    else:
                        st.warning("Aucun résultat trouvé pour votre question.")
    
    with col2:
        if st.button("🗑️ Effacer Historique"):
            st.session_state.chat_history = []
            st.success("Historique effacé !")
            st.rerun()

def show_image_search():
    """Interface de recherche spécifique aux images"""
    st.header("🔍 Recherche d'Images")
    
    vector_db = st.session_state.vector_db
    
    # Vérification de compatibilité
    if not isinstance(vector_db, VectorDatabase):
        st.error("⚠️ Format de base vectorielle incompatible détecté. Création d'une nouvelle base...")
        st.session_state.vector_db = VectorDatabase()
        vector_db = st.session_state.vector_db
    
    if not hasattr(vector_db, 'images') or not vector_db.images:
        st.warning("⚠️ Aucune image dans la base. Ajoutez d'abord des images.")
        return
    
    # Statistiques des images
    st.markdown("### 📊 Statistiques des Images")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("🖼️ Total Images", len(vector_db.images))
    
    with col2:
        # Compter les catégories
        all_categories = []
        for img in vector_db.images:
            all_categories.extend(img['categories'])
        unique_categories = list(set(all_categories))
        st.metric("🏷️ Catégories", len(unique_categories))
    
    # Recherche par catégories
    st.markdown("### 🏷️ Recherche par Catégories")
    
    categories_count = {}
    for img in vector_db.images:
        for cat in img['categories']:
            categories_count[cat] = categories_count.get(cat, 0) + 1
    
    selected_categories = st.multiselect(
        "Sélectionnez les catégories:",
        options=list(categories_count.keys()),
        format_func=lambda x: f"{x} ({categories_count[x]})"
    )
    
    if selected_categories:
        matching_images = vector_db.get_image_by_categories(selected_categories)
        
        if matching_images:
            st.markdown(f"### 📸 Images Trouvées ({len(matching_images)})")
            
            # Affichage en grille
            cols = st.columns(3)
            for i, img_data in enumerate(matching_images):
                with cols[i % 3]:
                    if os.path.exists(img_data['image_path']):
                        img = Image.open(img_data['image_path'])
                        st.image(img, caption=img_data['metadata']['title'], use_column_width=True)
                        
                        # Informations détaillées
                        with st.expander(f"Détails - {img_data['metadata']['title']}"):
                            st.markdown(f"**Description:** {img_data['description']}")
                            st.markdown(f"**Catégories:** {', '.join(img_data['categories'])}")
                            st.markdown(f"**Date:** {img_data['timestamp']}")
                            if img_data['text_content']:
                                st.markdown(f"**Texte extrait:** {img_data['text_content'][:200]}...")
    
    # Recherche par texte
    st.markdown("### 🔍 Recherche par Texte")
    
    search_query = st.text_input("Recherchez dans les descriptions et textes des images:")
    
    if search_query:
        # Recherche dans les images
        results = vector_db.search(search_query, top_k=10, filter_type="image")
        
        if results:
            st.markdown(f"### 📸 Résultats ({len(results)})")
            
            # Affichage des résultats
            cols = st.columns(3)
            for i, result in enumerate(results):
                with cols[i % 3]:
                    img_path = result['document']['metadata']['image_path']
                    if os.path.exists(img_path):
                        img = Image.open(img_path)
                        st.image(img, caption=result['document']['metadata']['title'], use_column_width=True)
                        st.caption(f"Similarité: {result['similarity']:.3f}")
                        
                        # Informations détaillées
                        with st.expander(f"Détails - {result['document']['metadata']['title']}"):
                            st.markdown(f"**Description:** {result['document']['text']}")
                            st.markdown(f"**Source:** {result['document']['metadata']['source']}")
        else:
            st.info("Aucune image trouvée pour cette recherche.")

if __name__ == "__main__":
    main()
