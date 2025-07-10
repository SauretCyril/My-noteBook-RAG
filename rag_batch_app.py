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
from pathlib import Path
import glob
from typing import Dict, List, Tuple, Optional
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch

# Configuration de la page
st.set_page_config(
    page_title="RAG Knowledge Base Manager + Batch",
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
    import ssl
    
    # Contournement SSL si nécessaire
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context
    
    # Liste des ressources nécessaires
    resources = ['punkt', 'punkt_tab', 'stopwords', 'wordnet', 'omw-1.4']
    
    for resource in resources:
        try:
            # Vérifier si la ressource existe
            if resource == 'punkt':
                nltk.data.find('tokenizers/punkt')
            elif resource == 'punkt_tab':
                nltk.data.find('tokenizers/punkt_tab')
            elif resource == 'stopwords':
                nltk.data.find('corpora/stopwords')
            elif resource == 'wordnet':
                nltk.data.find('corpora/wordnet')
            elif resource == 'omw-1.4':
                nltk.data.find('corpora/omw-1.4')
        except LookupError:
            try:
                print(f"Téléchargement de {resource}...")
                nltk.download(resource, quiet=True)
                print(f"✅ {resource} installé")
            except Exception as e:
                print(f"❌ Erreur avec {resource}: {e}")
                # Continuer avec les autres ressources
                continue
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

# Fonctions de traitement par lots
def read_annonce_file(file_path: str) -> Dict:
    """Lit un fichier ._annonce_.data et retourne ses informations"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        # Essayer de parser comme JSON
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Si ce n'est pas du JSON, traiter comme texte structuré
            lines = content.split('\n')
            data = {}
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    data[key.strip()] = value.strip()
                else:
                    # Ajouter à une description générale
                    if 'description' not in data:
                        data['description'] = ''
                    data['description'] += line + '\n'
            return data
    except Exception as e:
        st.error(f"Erreur lecture fichier d'annonce {file_path}: {e}")
        return {}

def find_files_recursive(directory: str, extensions: List[str]) -> List[Tuple[str, Dict]]:
    """Trouve tous les fichiers avec les extensions spécifiées de manière récursive"""
    files_found = []
    
    for root, dirs, files in os.walk(directory):
        # Chercher un fichier d'annonce dans ce répertoire
        annonce_data = {}
        annonce_files = [f for f in files if f.startswith('._rag_.') and f.endswith('.data')]
        
        if annonce_files:
            annonce_path = os.path.join(root, annonce_files[0])
            annonce_data = read_annonce_file(annonce_path)
            st.info(f"📋 Fichier d'annonce trouvé : {annonce_path}")
        
        # Chercher les fichiers à traiter
        for file in files:
            file_path = os.path.join(root, file)
            file_ext = os.path.splitext(file)[1].lower()
            
            if file_ext in extensions and not file.startswith('._rag_.'):
                files_found.append((file_path, annonce_data))
    
    return files_found

def extract_text_from_file(file_path: str) -> Optional[str]:
    """Extrait le texte d'un fichier selon son extension"""
    try:
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            return extract_text_from_pdf_file(file_path)
        elif file_ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif file_ext in ['.png', '.jpg', '.jpeg']:
            return extract_text_from_image_file(file_path)
        else:
            return None
    except Exception as e:
        st.error(f"Erreur extraction {file_path}: {e}")
        return None

def extract_text_from_pdf_file(file_path: str) -> Optional[str]:
    """Extrait le texte d'un fichier PDF"""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        st.error(f"Erreur extraction PDF {file_path}: {e}")
        return None

def extract_text_from_image_file(file_path: str) -> Optional[str]:
    """Extrait le texte d'une image via OCR"""
    try:
        image = Image.open(file_path)
        # Convertir en OpenCV format pour améliorer la qualité OCR
        img_array = np.array(image)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Améliorer la qualité pour l'OCR
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Extraire le texte
        text = pytesseract.image_to_string(thresh, lang='fra+eng')
        return text.strip()
    except Exception as e:
        st.error(f"Erreur OCR {file_path}: {e}")
        return None

def generate_image_description(image_path: str, processor, model) -> str:
    """Génère une description automatique de l'image"""
    try:
        if processor is None or model is None:
            return "Modèle de vision non disponible"
        
        # Charger et préparer l'image
        image = Image.open(image_path)
        inputs = processor(image, return_tensors="pt")
        
        # Générer la description
        with torch.no_grad():
            out = model.generate(**inputs, max_length=100, num_beams=5)
        
        # Décoder le résultat
        description = processor.decode(out[0], skip_special_tokens=True)
        return description
    except Exception as e:
        st.error(f"Erreur génération description {image_path}: {e}")
        return "Erreur lors de la génération de la description"

def classify_image_content(image_path: str, text_content: str = "", description: str = "") -> List[str]:
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
        if any(word in text_lower for word in ['email', 'mail', 'message', 'correspondance']):
            categories.append('Communication')
    
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
        if any(word in desc_lower for word in ['screen', 'computer', 'software', 'interface']):
            categories.append('Interface/Écran')
    
    # Classification basée sur l'extension et le contexte
    file_ext = os.path.splitext(image_path)[1].lower()
    if file_ext in ['.png', '.jpg', '.jpeg']:
        if not categories:  # Si aucune catégorie trouvée
            categories.append('Image générale')
    
    return categories if categories else ['Non classifié']

def save_image_to_storage(image_path: str, target_filename: str) -> Optional[str]:
    """Copie l'image dans le dossier de stockage"""
    try:
        os.makedirs(IMAGES_DIR, exist_ok=True)
        target_path = os.path.join(IMAGES_DIR, target_filename)
        
        # Copier l'image
        with Image.open(image_path) as img:
            img.save(target_path)
        
        return target_path
    except Exception as e:
        st.error(f"Erreur sauvegarde image {image_path}: {e}")
        return None

def create_document_metadata(file_path: str, annonce_data: Dict) -> Dict:
    """Crée les métadonnées d'un document basées sur le fichier et l'annonce"""
    file_name = os.path.basename(file_path)
    file_dir = os.path.dirname(file_path)
    
    metadata = {
        'title': annonce_data.get('title', file_name),
        'source': file_path,
        'filename': file_name,
        'directory': file_dir,
        'file_size': os.path.getsize(file_path),
        'category': annonce_data.get('category', 'Non classé'),
        'tags': annonce_data.get('tags', '').split(',') if annonce_data.get('tags') else [],
        'description': annonce_data.get('description', ''),
        'project': annonce_data.get('project', ''),
        'date': annonce_data.get('date', ''),
        'author': annonce_data.get('author', ''),
        'type': annonce_data.get('type', 'document'),
        'priority': annonce_data.get('priority', 'normal'),
        'status': annonce_data.get('status', 'active')
    }
    
    return metadata

def process_batch_files(files_list: List[Tuple[str, Dict]], vector_db, progress_callback=None, enable_vision=False) -> Dict:
    """Traite une liste de fichiers par lots avec traitement d'images avancé"""
    results = {
        'processed': 0,
        'success': 0,
        'errors': 0,
        'skipped': 0,
        'files_processed': [],
        'images_processed': [],
        'errors_list': []
    }
    
    total_files = len(files_list)
    
    # Initialiser le modèle de vision si nécessaire
    processor, model = None, None
    if enable_vision:
        processor, model = init_vision_model()
    
    for i, (file_path, annonce_data) in enumerate(files_list):
        try:
            if progress_callback:
                progress_callback(i, total_files, file_path)
            
            file_ext = os.path.splitext(file_path)[1].lower()
            
            # Traitement spécial pour les images
            if file_ext in ['.png', '.jpg', '.jpeg']:
                # Extraire le texte via OCR
                text = extract_text_from_file(file_path)
                
                # Générer la description si le modèle est disponible
                description = ""
                if enable_vision and processor and model:
                    description = generate_image_description(file_path, processor, model)
                
                # Classifier l'image
                categories = classify_image_content(file_path, text or "", description)
                
                # Créer les métadonnées enrichies
                metadata = create_document_metadata(file_path, annonce_data)
                metadata.update({
                    'description_auto': description,
                    'categories_auto': categories,
                    'ocr_text': text or "",
                    'file_type': 'image'
                })
                
                # Sauvegarder l'image dans le stockage
                filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.path.basename(file_path)}"
                saved_path = save_image_to_storage(file_path, filename)
                if saved_path:
                    metadata['stored_path'] = saved_path
                
                # Créer un texte composite pour l'indexation
                search_text = f"{text or ''} {description} {' '.join(categories)}"
                
                # Ajouter l'image à la base vectorielle
                if hasattr(vector_db, 'add_image'):
                    vector_db.add_image(file_path, text or "", description, categories, metadata)
                else:
                    # Fallback pour les bases vectorielles sans support images
                    if search_text.strip():
                        vector_db.add_document(search_text, metadata)
                
                results['success'] += 1
                results['images_processed'].append({
                    'file': file_path,
                    'description': description,
                    'categories': categories,
                    'ocr_text': text or "",
                    'metadata': metadata
                })
            else:
                # Traitement normal pour les autres fichiers
                text = extract_text_from_file(file_path)
                
                if text and text.strip():
                    # Créer les métadonnées
                    metadata = create_document_metadata(file_path, annonce_data)
                    metadata['file_type'] = 'document'
                    
                    # Segmenter le texte
                    segments = segment_text(text, 500)
                    
                    # Ajouter chaque segment à la base
                    for j, segment in enumerate(segments):
                        segment_metadata = metadata.copy()
                        segment_metadata.update({
                            'segment': j + 1,
                            'total_segments': len(segments),
                            'segment_text': segment
                        })
                        
                        vector_db.add_document(segment, segment_metadata)
                    
                    results['success'] += 1
                    results['files_processed'].append({
                        'file': file_path,
                        'segments': len(segments),
                        'metadata': metadata
                    })
                else:
                    results['skipped'] += 1
                    results['errors_list'].append(f"Pas de texte extrait: {file_path}")
                
        except Exception as e:
            results['errors'] += 1
            results['errors_list'].append(f"Erreur {file_path}: {str(e)}")
        
        results['processed'] += 1
    
    return results

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
    
    def search(self, query, top_k=5, filter_by=None, filter_type=None):
        """Recherche les documents les plus similaires avec filtrage optionnel"""
        if not self.documents or self.vectors is None:
            return []
        
        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.vectors)[0]
        
        # Filtrer les documents si nécessaire
        if filter_by or filter_type:
            filtered_indices = []
            for idx, doc in enumerate(self.documents):
                if filter_type and doc.get('type') != filter_type:
                    continue
                if filter_by and not self._matches_filter(doc, filter_by):
                    continue
                filtered_indices.append(idx)
            
            if not filtered_indices:
                return []
            
            # Obtenir les similarités filtrées
            filtered_similarities = [(idx, similarities[idx]) for idx in filtered_indices]
            filtered_similarities.sort(key=lambda x: x[1], reverse=True)
            
            results = []
            for idx, similarity in filtered_similarities[:top_k]:
                if similarity > 0:
                    results.append({
                        'document': self.documents[idx],
                        'similarity': similarity
                    })
            
            return results
        else:
            # Recherche normale sans filtre
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                if similarities[idx] > 0:
                    results.append({
                        'document': self.documents[idx],
                        'similarity': similarities[idx]
                    })
            
            return results
    
    def get_image_by_categories(self, categories):
        """Récupère les images par catégories"""
        results = []
        for img in self.images:
            if any(cat in img['categories'] for cat in categories):
                results.append(img)
        return results
    
    def get_all_images(self):
        """Récupère toutes les images"""
        return self.images
    
    def _matches_filter(self, document, filter_by):
        """Vérifie si un document correspond aux critères de filtrage"""
        metadata = document['metadata']
        
        for key, value in filter_by.items():
            if key in metadata:
                if isinstance(value, list):
                    if metadata[key] not in value:
                        return False
                else:
                    if metadata[key] != value:
                        return False
            else:
                return False
        
        return True
    
    def get_categories(self):
        """Retourne toutes les catégories disponibles"""
        categories = set()
        for doc in self.documents:
            category = doc['metadata'].get('category', 'Non classé')
            categories.add(category)
        return sorted(list(categories))
    
    def get_projects(self):
        """Retourne tous les projets disponibles"""
        projects = set()
        for doc in self.documents:
            project = doc['metadata'].get('project', '')
            if project:
                projects.add(project)
        return sorted(list(projects))
    
    def get_stats(self):
        """Retourne les statistiques de la base"""
        total_docs = len(self.documents)
        total_images = len(self.images)
        categories = self.get_categories()
        projects = self.get_projects()
        
        return {
            'total_documents': total_docs,
            'total_images': total_images,
            'categories': len(categories),
            'projects': len(projects),
            'categories_list': categories,
            'projects_list': projects
        }
    
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
                        st.warning("Format de base vectorielle incompatible. Création d'une nouvelle base.")
                        return cls()
            except Exception as e:
                st.error(f"Erreur lors du chargement de la base vectorielle : {e}")
                return cls()
        return cls()

# Fonctions utilitaires (identiques aux précédentes)
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
        create_backup(KNOWLEDGE_BASE_FILE)
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(KNOWLEDGE_BASE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"Erreur lors de la sauvegarde : {e}")
        return False

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
    
    # Informations sur les sources
    sources_info = []
    for doc in context_docs:
        metadata = doc['document']['metadata']
        sources_info.append(f"- {metadata.get('title', 'Sans titre')} ({metadata.get('category', 'Non classé')})")
    
    response = f"""Basé sur les documents de la base de connaissances, voici ma réponse :

**Contexte trouvé :**
{context[:800]}...

**Réponse :**
Je peux vous aider avec les informations trouvées dans les documents. Pour une réponse plus précise, vous pouvez intégrer un modèle de langage comme Mistral AI ou OpenAI.

**Sources utilisées :**
{chr(10).join(sources_info)}

**Total : {len(context_docs)} document(s) pertinent(s)**"""
    
    return response

# Interface principale
def main():
    # Initialisation
    init_nltk()
    
    # Titre principal
    st.title("🤖 RAG Knowledge Base Manager + Batch Processing")
    st.markdown("---")
    
    # Sidebar pour la navigation
    st.sidebar.title("📋 Menu Principal")
    page = st.sidebar.selectbox(
        "Choisissez une action :",
        [
            "🏠 Accueil", 
            "🗃️ Gestion de la Base", 
            "📄 Ajouter Document", 
            "📁 Traitement par Lots",
            "❓ Poser Questions",
            "🔍 Recherche Avancée",
            "🖼️ Galerie d'Images"
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
    elif page == "📄 Ajouter Document":
        show_single_document_upload()
    elif page == "📁 Traitement par Lots":
        show_batch_processing()
    elif page == "❓ Poser Questions":
        show_question_interface()
    elif page == "🔍 Recherche Avancée":
        show_advanced_search()
    elif page == "🖼️ Galerie d'Images":
        show_images_gallery()

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
    
    # Statistiques principales
    stats = vector_db.get_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📚 Documents JSON", len(knowledge_base))
    
    with col2:
        st.metric("📄 Documents Vectorisés", stats['total_documents'])
    
    with col3:
        st.metric("🏷️ Catégories", stats['categories'])
    
    with col4:
        st.metric("📋 Projets", stats['projects'])
    
    # Informations détaillées
    if stats['categories'] > 0:
        st.markdown("### 🏷️ Catégories Disponibles")
        cols = st.columns(min(5, len(stats['categories_list'])))
        for i, category in enumerate(stats['categories_list']):
            with cols[i % 5]:
                st.badge(category)
    
    if stats['projects'] > 0:
        st.markdown("### 📋 Projets Disponibles")
        cols = st.columns(min(5, len(stats['projects_list'])))
        for i, project in enumerate(stats['projects_list']):
            with cols[i % 5]:
                st.badge(project)
    
    # Instructions rapides
    st.markdown("### 🚀 Démarrage Rapide")
    st.markdown("""
    1. **Gestion de la Base** : Créez ou réinitialisez votre base vectorielle
    2. **Traitement par Lots** : Ajoutez tout un répertoire de documents
    3. **Ajouter Document** : Uploadez des fichiers individuels
    4. **Poser Questions** : Interrogez votre base de connaissances
    5. **Recherche Avancée** : Filtrez par catégorie, projet, etc.
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
    
    # Statistiques détaillées
    stats = vector_db.get_stats()
    
    st.markdown("### 📊 Statistiques Détaillées")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"📄 Documents : {stats['total_documents']}")
    
    with col2:
        st.info(f"🏷️ Catégories : {stats['categories']}")
    
    with col3:
        if vector_db.vectors is not None:
            st.info(f"🔢 Dimensions : {vector_db.vectors.shape}")
        else:
            st.info("🔢 Pas de vecteurs")
    
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

def show_single_document_upload():
    """Interface pour ajouter un document unique"""
    st.header("📄 Ajouter un Document")
    
    uploaded_file = st.file_uploader(
        "Choisissez un fichier",
        type=['pdf', 'txt', 'png', 'jpg', 'jpeg']
    )
    
    if uploaded_file:
        st.markdown(f"### 📎 Traitement de : {uploaded_file.name}")
        
        # Extraction du texte
        with st.spinner("Extraction du texte..."):
            if uploaded_file.type == "application/pdf":
                text = extract_text_from_pdf(uploaded_file)
            elif uploaded_file.type == "text/plain":
                text = str(uploaded_file.read(), "utf-8")
            elif uploaded_file.type.startswith("image/"):
                image = Image.open(uploaded_file)
                text = extract_text_from_image(image)
            else:
                text = None
        
        if text and text.strip():
            st.success(f"✅ Texte extrait : {len(text)} caractères")
            
            # Métadonnées personnalisées
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Titre", value=uploaded_file.name)
                category = st.text_input("Catégorie", value="Non classé")
                project = st.text_input("Projet", value="")
            
            with col2:
                author = st.text_input("Auteur", value="")
                tags = st.text_input("Tags (séparés par des virgules)", value="")
                description = st.text_area("Description", value="")
            
            # Ajout à la base
            if st.button("➕ Ajouter à la base"):
                with st.spinner("Ajout en cours..."):
                    vector_db = st.session_state.vector_db
                    
                    metadata = {
                        'title': title,
                        'source': uploaded_file.name,
                        'category': category,
                        'project': project,
                        'author': author,
                        'tags': tags.split(',') if tags else [],
                        'description': description,
                        'type': 'upload'
                    }
                    
                    segments = segment_text(text, 500)
                    
                    for i, segment in enumerate(segments):
                        segment_metadata = metadata.copy()
                        segment_metadata.update({
                            'segment': i + 1,
                            'total_segments': len(segments)
                        })
                        vector_db.add_document(segment, segment_metadata)
                    
                    # Sauvegarder
                    vector_db.save(VECTOR_DB_FILE)
                    st.success(f"✅ Document ajouté avec succès ! ({len(segments)} segments)")
        else:
            st.error("❌ Impossible d'extraire le texte")

def show_batch_processing():
    """Interface pour le traitement par lots"""
    st.header("📁 Traitement par Lots")
    
    st.markdown("""
    ### 📋 Fonctionnalités
    - **Parcours récursif** : Traite tous les sous-dossiers
    - **Fichiers d'annonce** : Utilise `._annonce_.data` pour contextualiser
    - **Formats supportés** : PDF, TXT, PNG, JPG, JPEG
    - **Métadonnées enrichies** : Catégories, projets, tags automatiques
    - **🔍 Vision avancée** : Descriptions automatiques et classification d'images
    """)
    
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
            st.markdown("### ⚙️ Options de Traitement")
            extensions = st.multiselect(
                "Types de fichiers à traiter",
                ['.pdf', '.txt', '.png', '.jpg', '.jpeg'],
                default=['.pdf', '.txt']
            )
            
            max_file_size = st.slider(
                "Taille max par fichier (MB)",
                1, 100, 10
            )
            
            # Option pour activer la vision avancée
            enable_vision = st.checkbox(
                "🔍 Activer la vision avancée pour les images",
                value=False,
                help="Génère des descriptions automatiques et classifie les images (plus lent)"
            )
            
            if enable_vision:
                st.info("⚠️ Le traitement sera plus lent mais les images seront mieux analysées")
        
        with col2:
            st.markdown("### 📊 Prévisualisation")
            if st.button("🔍 Scanner le répertoire"):
                with st.spinner("Scan en cours..."):
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
                        st.session_state.enable_vision = enable_vision
                    else:
                        st.warning("⚠️ Aucun fichier trouvé")
        
        # Traitement par lots
        if 'files_to_process' in st.session_state:
            st.markdown("### 🚀 Traitement par Lots")
            
            # Afficher les options choisies
            if st.session_state.get('enable_vision', False):
                st.info("🔍 Vision avancée activée - Les images seront analysées en profondeur")
            
            if st.button("▶️ Lancer le traitement", type="primary"):
                files_list = st.session_state.files_to_process
                enable_vision = st.session_state.get('enable_vision', False)
                
                # Barre de progression
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                def update_progress(current, total, current_file):
                    progress = current / total
                    progress_bar.progress(progress)
                    status_text.text(f"Traitement : {current}/{total} - {os.path.basename(current_file)}")
                
                # Traitement
                vector_db = st.session_state.vector_db
                with st.spinner("Traitement en cours..."):
                    results = process_batch_files(files_list, vector_db, update_progress, enable_vision)
                
                # Affichage des résultats
                progress_bar.progress(1.0)
                status_text.text("Traitement terminé !")
                
                # Statistiques générales
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("✅ Succès", results['success'])
                with col2:
                    st.metric("❌ Erreurs", results['errors'])
                with col3:
                    st.metric("⏭️ Ignorés", results['skipped'])
                with col4:
                    st.metric("🖼️ Images", len(results.get('images_processed', [])))
                
                # Afficher les images traitées si disponibles
                if results.get('images_processed'):
                    st.markdown("### 🖼️ Images Traitées")
                    
                    for img_result in results['images_processed'][:5]:  # Afficher les 5 premières
                        with st.expander(f"📸 {os.path.basename(img_result['file'])}"):
                            col1, col2 = st.columns([1, 2])
                            
                            with col1:
                                try:
                                    image = Image.open(img_result['file'])
                                    st.image(image, width=200)
                                except:
                                    st.write("❌ Aperçu non disponible")
                            
                            with col2:
                                st.write(f"**Description:** {img_result.get('description', 'N/A')}")
                                st.write(f"**Catégories:** {', '.join(img_result.get('categories', []))}")
                                if img_result.get('ocr_text'):
                                    st.write(f"**Texte OCR:** {img_result['ocr_text'][:100]}...")
                    
                    if len(results['images_processed']) > 5:
                        st.write(f"... et {len(results['images_processed']) - 5} autres images")
                
                # Sauvegarder la base
                if results['success'] > 0:
                    vector_db.save(VECTOR_DB_FILE)
                    st.success(f"✅ {results['success']} fichier(s) ajouté(s) à la base !")
                
                # Afficher les erreurs
                if results['errors'] > 0:
                    with st.expander("❌ Voir les erreurs"):
                        for error in results['errors_list']:
                            st.error(error)
                
                # Nettoyer la session
                if 'files_to_process' in st.session_state:
                    del st.session_state.files_to_process
                if 'enable_vision' in st.session_state:
                    del st.session_state.enable_vision
    
    else:
        st.info("📂 Sélectionnez un répertoire valide pour commencer")
    
    # Exemple de fichier d'annonce
    st.markdown("### 📋 Format du Fichier d'Annonce")
    st.markdown("""
    Créez un fichier `._annonce_.data` dans vos dossiers avec ce format :
    
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
    
    Ou format texte simple :
    ```
    title: Projet X - Documentation
    category: Projet  
    project: Projet X
    author: Nom de l'auteur
    description: Description du contenu du dossier
    tags: documentation,projet,important
    ```
    """)

def show_question_interface():
    """Interface pour poser des questions"""
    st.header("❓ Poser des Questions")
    
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
    question = st.text_input("🔍 Posez votre question :", placeholder="Ex: Quels sont les documents du projet X ?")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🚀 Rechercher", type="primary"):
            if question:
                with st.spinner("Recherche en cours..."):
                    results = vector_db.search(question, top_k=5)
                    
                    if results:
                        response = generate_response(question, results)
                        st.session_state.chat_history.append((question, response))
                        
                        st.markdown("### 🤖 Réponse")
                        st.markdown(response)
                        
                        # Affichage des sources
                        st.markdown("### 📚 Sources Utilisées")
                        for i, result in enumerate(results):
                            doc = result['document']
                            metadata = doc['metadata']
                            similarity = result['similarity']
                            
                            with st.expander(f"Source {i+1} - {metadata.get('title', 'Sans titre')} - Similarité: {similarity:.3f}"):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.markdown(f"**Catégorie:** {metadata.get('category', 'N/A')}")
                                    st.markdown(f"**Projet:** {metadata.get('project', 'N/A')}")
                                    st.markdown(f"**Auteur:** {metadata.get('author', 'N/A')}")
                                
                                with col2:
                                    st.markdown(f"**Source:** {metadata.get('source', 'N/A')}")
                                    st.markdown(f"**Segment:** {metadata.get('segment', 'N/A')}/{metadata.get('total_segments', 'N/A')}")
                                
                                st.text_area("Contenu:", doc['text'], height=100)
                    else:
                        st.warning("Aucun résultat trouvé pour votre question.")
    
    with col2:
        if st.button("🗑️ Effacer Historique"):
            st.session_state.chat_history = []
            st.success("Historique effacé !")
            st.rerun()

def show_advanced_search():
    """Interface de recherche avancée"""
    st.header("🔍 Recherche Avancée")
    
    vector_db = st.session_state.vector_db
    
    if not vector_db.documents:
        st.warning("⚠️ Aucun document dans la base.")
        return
    
    # Options de filtrage
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔍 Recherche Textuelle")
        search_query = st.text_input("Rechercher dans le contenu:")
        
        st.markdown("### 🏷️ Filtres")
        categories = vector_db.get_categories()
        selected_categories = st.multiselect("Catégories:", categories)
        
        projects = vector_db.get_projects()
        selected_projects = st.multiselect("Projets:", projects)
    
    with col2:
        st.markdown("### ⚙️ Options")
        max_results = st.slider("Nombre de résultats", 1, 20, 10)
        min_similarity = st.slider("Similarité minimale", 0.0, 1.0, 0.1)
    
    # Recherche
    if st.button("🔍 Rechercher"):
        if search_query:
            # Construire les filtres
            filters = {}
            if selected_categories:
                filters['category'] = selected_categories
            if selected_projects:
                filters['project'] = selected_projects
            
            # Effectuer la recherche
            results = vector_db.search(search_query, top_k=max_results, filter_by=filters if filters else None)
            
            # Filtrer par similarité
            filtered_results = [r for r in results if r['similarity'] >= min_similarity]
            
            if filtered_results:
                st.markdown(f"### 📊 Résultats ({len(filtered_results)})")
                
                for i, result in enumerate(filtered_results):
                    doc = result['document']
                    metadata = doc['metadata']
                    similarity = result['similarity']
                    
                    with st.expander(f"Résultat {i+1} - {metadata.get('title', 'Sans titre')} - Score: {similarity:.3f}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**📁 Source:** {metadata.get('source', 'N/A')}")
                            st.markdown(f"**🏷️ Catégorie:** {metadata.get('category', 'N/A')}")
                            st.markdown(f"**📋 Projet:** {metadata.get('project', 'N/A')}")
                        
                        with col2:
                            st.markdown(f"**👤 Auteur:** {metadata.get('author', 'N/A')}")
                            st.markdown(f"**📄 Segment:** {metadata.get('segment', 'N/A')}/{metadata.get('total_segments', 'N/A')}")
                            st.markdown(f"**📅 Date:** {metadata.get('date', 'N/A')}")
                        
                        if metadata.get('description'):
                            st.markdown(f"**📝 Description:** {metadata['description']}")
                        
                        st.text_area("Contenu:", doc['text'], height=100, key=f"content_{i}")
            else:
                st.info("Aucun résultat trouvé avec ces critères.")

def show_images_gallery():
    """Interface pour visualiser les images indexées"""
    st.header("🖼️ Galerie d'Images")
    
    vector_db = st.session_state.vector_db
    
    if not hasattr(vector_db, 'images') or not vector_db.images:
        st.warning("⚠️ Aucune image dans la base. Ajoutez d'abord des images avec la vision avancée activée.")
        return
    
    st.markdown(f"### 📊 {len(vector_db.images)} image(s) indexée(s)")
    
    # Filtres
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Filtre par catégorie
        all_categories = set()
        for img in vector_db.images:
            all_categories.update(img.get('categories', []))
        
        selected_categories = st.multiselect(
            "Filtrer par catégorie:",
            sorted(list(all_categories)),
            default=[]
        )
    
    with col2:
        # Filtre par projet
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
    
    with col3:
        # Options d'affichage
        images_per_row = st.select_slider(
            "Images par ligne:",
            options=[2, 3, 4, 5],
            value=3
        )
        
        show_details = st.checkbox("Afficher les détails", value=True)
    
    # Recherche textuelle dans les images
    search_query = st.text_input(
        "🔍 Rechercher dans les descriptions et texte OCR:",
        placeholder="Ex: document, personne, nature..."
    )
    
    # Filtrer les images
    filtered_images = vector_db.images
    
    if selected_categories:
        filtered_images = [img for img in filtered_images 
                          if any(cat in img.get('categories', []) for cat in selected_categories)]
    
    if selected_projects:
        filtered_images = [img for img in filtered_images 
                          if img.get('metadata', {}).get('project', '') in selected_projects]
    
    if search_query:
        search_lower = search_query.lower()
        filtered_images = [img for img in filtered_images 
                          if search_lower in img.get('description', '').lower() or 
                             search_lower in img.get('text_content', '').lower() or
                             any(search_lower in cat.lower() for cat in img.get('categories', []))]
    
    if not filtered_images:
        st.info("Aucune image ne correspond aux critères de recherche.")
        return
    
    st.markdown(f"### 🖼️ {len(filtered_images)} image(s) trouvée(s)")
    
    # Affichage en grille
    num_images = len(filtered_images)
    num_rows = (num_images + images_per_row - 1) // images_per_row
    
    for row in range(num_rows):
        cols = st.columns(images_per_row)
        
        for col_idx in range(images_per_row):
            img_idx = row * images_per_row + col_idx
            
            if img_idx < num_images:
                img_data = filtered_images[img_idx]
                
                with cols[col_idx]:
                    try:
                        # Afficher l'image
                        if os.path.exists(img_data['image_path']):
                            image = Image.open(img_data['image_path'])
                            st.image(image, use_column_width=True)
                        else:
                            st.write("❌ Image non trouvée")
                        
                        # Afficher les détails si demandé
                        if show_details:
                            st.markdown(f"**📁** {os.path.basename(img_data['image_path'])}")
                            
                            # Description
                            if img_data.get('description'):
                                st.markdown(f"**🔍** {img_data['description'][:80]}...")
                            
                            # Catégories
                            if img_data.get('categories'):
                                categories_str = ', '.join(img_data['categories'][:3])
                                if len(img_data['categories']) > 3:
                                    categories_str += f" +{len(img_data['categories']) - 3}"
                                st.markdown(f"**🏷️** {categories_str}")
                            
                            # Texte OCR (si disponible)
                            if img_data.get('text_content'):
                                st.markdown(f"**📝** {img_data['text_content'][:50]}...")
                            
                            # Métadonnées
                            metadata = img_data.get('metadata', {})
                            if metadata.get('project'):
                                st.markdown(f"**📂** {metadata['project']}")
                        
                        # Bouton pour voir les détails complets
                        if st.button(f"🔍 Détails", key=f"details_{img_idx}"):
                            st.session_state.selected_image = img_data
                    
                    except Exception as e:
                        st.error(f"Erreur affichage image: {e}")
    
    # Affichage des détails de l'image sélectionnée
    if 'selected_image' in st.session_state:
        img_data = st.session_state.selected_image
        
        st.markdown("---")
        st.markdown("### 📋 Détails de l'Image")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            try:
                if os.path.exists(img_data['image_path']):
                    image = Image.open(img_data['image_path'])
                    st.image(image, width=300)
                else:
                    st.write("❌ Image non trouvée")
            except:
                st.write("❌ Erreur affichage")
        
        with col2:
            st.markdown(f"**📁 Fichier:** {img_data['image_path']}")
            st.markdown(f"**🔍 Description:** {img_data.get('description', 'N/A')}")
            st.markdown(f"**🏷️ Catégories:** {', '.join(img_data.get('categories', []))}")
            
            if img_data.get('text_content'):
                st.markdown("**📝 Texte OCR:**")
                st.text_area("", img_data['text_content'], height=100)
            
            metadata = img_data.get('metadata', {})
            if metadata:
                st.markdown("**📋 Métadonnées:**")
                for key, value in metadata.items():
                    if key not in ['stored_path', 'segment_text'] and value:
                        st.markdown(f"- **{key}:** {value}")
    if search_query:
        search_lower = search_query.lower()
        filtered_images = [img for img in filtered_images 
                          if search_lower in img.get('description', '').lower() or 
                             search_lower in img.get('text_content', '').lower() or
                             any(search_lower in cat.lower() for cat in img.get('categories', []))]
    
    if not filtered_images:
        st.info("Aucune image ne correspond aux critères de recherche.")
        return
    
    st.markdown(f"### 🖼️ {len(filtered_images)} image(s) trouvée(s)")
    
    # Affichage en grille
    num_images = len(filtered_images)
    num_rows = (num_images + images_per_row - 1) // images_per_row
    
    for row in range(num_rows):
        cols = st.columns(images_per_row)
        
        for col_idx in range(images_per_row):
            img_idx = row * images_per_row + col_idx
            
            if img_idx < num_images:
                img_data = filtered_images[img_idx]
                
                with cols[col_idx]:
                    try:
                        # Afficher l'image
                        if os.path.exists(img_data['image_path']):
                            image = Image.open(img_data['image_path'])
                            st.image(image, use_column_width=True)
                        else:
                            st.write("❌ Image non trouvée")
                        
                        # Afficher les détails si demandé
                        if show_details:
                            st.markdown(f"**📁** {os.path.basename(img_data['image_path'])}")
                            
                            # Description
                            if img_data.get('description'):
                                st.markdown(f"**🔍** {img_data['description'][:80]}...")
                            
                            # Catégories
                            if img_data.get('categories'):
                                categories_str = ', '.join(img_data['categories'][:3])
                                if len(img_data['categories']) > 3:
                                    categories_str += f" +{len(img_data['categories']) - 3}"
                                st.markdown(f"**🏷️** {categories_str}")
                            
                            # Texte OCR (si disponible)
                            if img_data.get('text_content'):
                                st.markdown(f"**📝** {img_data['text_content'][:50]}...")
                            
                            # Métadonnées
                            metadata = img_data.get('metadata', {})
                            if metadata.get('project'):
                                st.markdown(f"**📂** {metadata['project']}")
                        
                        # Bouton pour voir les détails complets
                        if st.button(f"🔍 Détails", key=f"details_{img_idx}"):
                            st.session_state.selected_image = img_data
                    
                    except Exception as e:
                        st.error(f"Erreur affichage image: {e}")
    
    # Affichage des détails de l'image sélectionnée
    if 'selected_image' in st.session_state:
        img_data = st.session_state.selected_image
        
        st.markdown("---")
        st.markdown("### 📋 Détails de l'Image")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            try:
                if os.path.exists(img_data['image_path']):
                    image = Image.open(img_data['image_path'])
                    st.image(image, width=300)
                else:
                    st.write("❌ Image non trouvée")
            except:
                st.write("❌ Erreur affichage")
        
        with col2:
            st.markdown(f"**📁 Fichier:** {img_data['image_path']}")
            st.markdown(f"**🔍 Description:** {img_data.get('description', 'N/A')}")
            st.markdown(f"**🏷️ Catégories:** {', '.join(img_data.get('categories', []))}")
            
            if img_data.get('text_content'):
                st.markdown("**📝 Texte OCR:**")
                st.text_area("", img_data['text_content'], height=100)
            
            metadata = img_data.get('metadata', {})
            if metadata:
                st.markdown("**📋 Métadonnées:**")
                for key, value in metadata.items():
                    if key not in ['stored_path', 'segment_text'] and value:
                        st.markdown(f"- **{key}:** {value}")
        
        if st.button("❌ Fermer les détails"):
            del st.session_state.selected_image
            st.rerun()

def extract_text_from_pdf(pdf_file):
    """Extrait le texte d'un fichier PDF uploadé"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"Erreur lors de l'extraction du PDF : {e}")
        return None

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

if __name__ == "__main__":
    main()
