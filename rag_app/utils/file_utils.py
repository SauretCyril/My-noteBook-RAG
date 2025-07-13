"""Utilitaires pour la manipulation de fichiers."""

import os
import json
import PyPDF2
import pytesseract
import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
from PIL import Image
import streamlit as st

# Système de logging centralisé pour éviter la pollution de l'interface
class DebugLogger:
    """Logger centralisé pour collecter les messages de debug sans polluer l'interface"""
    
    def __init__(self):
        if 'debug_logs' not in st.session_state:
            st.session_state.debug_logs = []
    
    def log(self, level: str, message: str, component: str = "system"):
        """Ajoute un message au log de debug"""
        if 'debug_logs' not in st.session_state:
            st.session_state.debug_logs = []
        
        import datetime
        log_entry = {
            'timestamp': datetime.datetime.now().strftime("%H:%M:%S"),
            'level': level,
            'component': component,
            'message': message
        }
        st.session_state.debug_logs.append(log_entry)
        
        # Limiter à 100 entrées pour éviter l'accumulation
        if len(st.session_state.debug_logs) > 100:
            st.session_state.debug_logs = st.session_state.debug_logs[-100:]
    
    def info(self, message: str, component: str = "file_utils"):
        self.log("INFO", message, component)
    
    def warning(self, message: str, component: str = "file_utils"):
        self.log("WARNING", message, component)
    
    def error(self, message: str, component: str = "file_utils"):
        self.log("ERROR", message, component)
    
    def success(self, message: str, component: str = "file_utils"):
        self.log("SUCCESS", message, component)

# Instance globale du logger
debug_logger = DebugLogger()

# Configuration automatique de Tesseract pour Windows
def configure_tesseract():
    """Configure automatiquement le chemin vers Tesseract OCR."""
    if os.name == 'nt':  # Windows
        possible_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"C:\tesseract\tesseract.exe",
            r"C:\tools\tesseract\tesseract.exe"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                return path
        
        # Si aucun trouvé, essayer d'ajouter au PATH temporairement
        tesseract_dir = r"C:\Program Files\Tesseract-OCR"
        if os.path.exists(tesseract_dir) and tesseract_dir not in os.environ.get('PATH', ''):
            os.environ['PATH'] += os.pathsep + tesseract_dir
            
    return None

# Configurer Tesseract au chargement du module
configure_tesseract()

def read_annonce_file(file_path: str) -> Dict:
    """Lit un fichier ._rag_.data et retourne ses informations."""
    try:
        # Détecter l'encodage pour les fichiers d'annonce aussi
        encoding = detect_file_encoding(file_path)
        
        with open(file_path, 'r', encoding=encoding) as f:
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
        debug_logger.error(f"Erreur lecture fichier d'annonce {file_path}: {e}")
        return {}

def read_data_json_file(file_path: str) -> Dict:
    """Lit un fichier .data.json et convertit au format RAG."""
    try:
        # Vérifier que le fichier n'est pas vide
        if os.path.getsize(file_path) == 0:
            debug_logger.warning(f"Fichier .data.json vide ignoré : {os.path.basename(file_path)}")
            return {}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                debug_logger.warning(f"Fichier .data.json sans contenu ignoré : {os.path.basename(file_path)}")
                return {}
            data_json = json.loads(content)
        
        # Mapper les champs .data.json vers le format RAG standard
        # Construire le nom de projet : dossier + "_" + description
        dossier = data_json.get('dossier', 'Projet')
        description = data_json.get('description', 'Sans description')
        project_name = f"{dossier}_{description}"
        
        rag_data = {
            'title': data_json.get('description', ''),
            'category': data_json.get('categorie', 'Non classé'),
            'project': project_name,
            'author': data_json.get('contact', data_json.get('entreprise', 'Inconnu')),
            'date': data_json.get('Date', data_json.get('Date_rep', '')),
            'description': _build_description_from_data_json(data_json),
            'tags': _build_tags_from_data_json(data_json),
            'priority': _map_priority_from_etat(data_json.get('etat', 'Todo')),
            'status': _map_status_from_etat(data_json.get('etat', 'Todo')),
            'source_format': 'data_json',  # Identifier la source
            'original_data': data_json  # Conserver les données originales
        }
        
        return rag_data
        
    except Exception as e:
        debug_logger.error(f"Erreur lecture fichier .data.json {file_path}: {e}")
        return {}

def _build_description_from_data_json(data_json: Dict) -> str:
    """Construit une description enrichie à partir des données .data.json."""
    parts = []
    
    # Description principale
    if data_json.get('description'):
        parts.append(data_json['description'])
    
    # Commentaire
    if data_json.get('Commentaire'):
        parts.append(f"Commentaire: {data_json['Commentaire']}")
    
    # Lieu et origine
    if data_json.get('Lieu') and data_json['Lieu'] != 'N/A':
        parts.append(f"Lieu: {data_json['Lieu']}")
    
    if data_json.get('Origine'):
        parts.append(f"Origine: {data_json['Origine']}")
    
    # Action à mener
    if data_json.get('action'):
        parts.append(f"Action: {data_json['action']}")
    
    # Prochaine étape
    if data_json.get('todo') and data_json['todo'] != '?':
        parts.append(f"Todo: {data_json['todo']}")
    
    # URL principale
    if data_json.get('url'):
        parts.append(f"URL: {data_json['url']}")
    
    # Informations de contact
    contact_parts = []
    if data_json.get('contact'):
        contact_parts.append(data_json['contact'])
    if data_json.get('tel'):
        contact_parts.append(f"Tel: {data_json['tel']}")
    if data_json.get('mail'):
        contact_parts.append(f"Email: {data_json['mail']}")
    
    if contact_parts:
        parts.append(f"Contact: {' | '.join(contact_parts)}")
    
    return ' | '.join(parts)

def _build_tags_from_data_json(data_json: Dict) -> str:
    """Construit des tags à partir des données .data.json."""
    tags = []
    
    # Tags basés sur les fichiers disponibles
    if data_json.get('BA') == 'O':
        tags.append('BA')
    if data_json.get('CV') == 'O':
        tags.append('CV')
    if data_json.get('GptSum') == 'O':
        tags.append('GPT-Summary')
    if data_json.get('isJo') == 'O':
        tags.append('Annonce')
    if data_json.get('Notes'):
        tags.append('Notes')
    
    # Tags basés sur les métadonnées
    if data_json.get('categorie'):
        tags.append(data_json['categorie'])
    if data_json.get('entreprise'):
        tags.append(data_json['entreprise'])
    if data_json.get('etat'):
        tags.append(data_json['etat'])
    if data_json.get('contact'):
        tags.append(data_json['contact'])
    
    # URL YouTube si disponible
    if data_json.get('lnk_Youtub_value'):
        tags.append('video')
    
    return ','.join(tags)

def _map_priority_from_etat(etat: str) -> str:
    """Mappe l'état vers une priorité."""
    etat_lower = etat.lower()
    if etat_lower in ['urgent', 'critique']:
        return 'high'
    elif etat_lower in ['done', 'fini']:
        return 'low'
    else:
        return 'normal'

def _map_status_from_etat(etat: str) -> str:
    """Mappe l'état vers un statut."""
    etat_lower = etat.lower()
    if etat_lower in ['done', 'fini', 'terminé']:
        return 'completed'
    elif etat_lower in ['todo', 'à faire']:
        return 'active'
    elif etat_lower in ['en cours', 'wip']:
        return 'in_progress'
    else:
        return 'active'

def find_files_recursive(directory: str, extensions: List[str]) -> List[Tuple[str, Dict]]:
    """Trouve tous les fichiers avec les extensions spécifiées de manière récursive."""
    import glob
    files_found = []
    
    for root, dirs, files in os.walk(directory):
        # AJOUT: Forcer la détection des fichiers cachés .data.json
        hidden_data_json = os.path.join(root, '.data.json')
        if os.path.exists(hidden_data_json) and '.data.json' not in files:
            files.append('.data.json')
            debug_logger.info(f"🔍 Fichier caché .data.json détecté et ajouté : {hidden_data_json}")
        
        # Chercher les fichiers de métadonnées dans ce répertoire
        rag_data = {}
        data_json_data = {}
        notes_data = {}
        
        # 1. Chercher d'abord les fichiers ._rag_.data (priorité haute)
        annonce_files = [f for f in files if f.startswith('._rag_.') and f.endswith('.data')]
        
        if annonce_files:
            annonce_path = os.path.join(root, annonce_files[0])
            rag_data = read_annonce_file(annonce_path)
            debug_logger.info(f"📋 Fichier ._rag_.data trouvé : {annonce_path}")
        
        # 2. Chercher les fichiers .data.json (y compris les fichiers cachés commençant par un point)
        data_json_files = [f for f in files if f.endswith('.data.json') or f == '.data.json']
        
        if data_json_files:
            data_json_path = os.path.join(root, data_json_files[0])
            data_json_data = read_data_json_file(data_json_path)
            debug_logger.info(f"📊 Fichier .data.json trouvé : {data_json_path}")
        
        # 3. Chercher les fichiers _notes.txt (dossier_notes.txt)
        notes_files = [f for f in files if f.endswith('_notes.txt')]
        
        if notes_files:
            notes_path = os.path.join(root, notes_files[0])
            notes_data = read_notes_file(notes_path)
            debug_logger.info(f"📝 Fichier notes trouvé : {notes_path}")
        
        # 4. Détecter les fichiers de présentation (CV et BA)
        cv_files = detect_cv_files(files)
        ba_files = detect_ba_files(files)
        
        if cv_files:
            debug_logger.info(f"📄 Fichier(s) CV de candidature trouvé(s) : {', '.join(cv_files)}")
        if ba_files:
            debug_logger.info(f"🎤 Fichier(s) BA de support oral trouvé(s) : {', '.join(ba_files)}")
        
        # Fusionner toutes les métadonnées
        base_metadata = merge_metadata_sources(rag_data, data_json_data, notes_data)
        annonce_data = enrich_metadata_with_presentation_files(base_metadata, cv_files, ba_files)
        
        # Chercher les fichiers à traiter
        for file in files:
            file_path = os.path.join(root, file)
            file_ext = os.path.splitext(file)[1].lower()
            
            # Inclure les fichiers selon les extensions + les .data.json comme projets
            should_include = False
            metadata_to_use = annonce_data  # Métadonnées par défaut
            
            # Fichiers normaux selon les extensions
            if (file_ext in extensions and 
                not file.startswith('._rag_.') and 
                not file.endswith('_notes.txt')):
                should_include = True
            
            # Fichiers .data.json comme projets (avec leurs propres métadonnées, y compris fichiers cachés)
            elif file.endswith('.data.json') or file == '.data.json':
                should_include = True
                # Pour les .data.json, utiliser leurs propres métadonnées
                own_metadata = read_data_json_file(file_path)
                if own_metadata:
                    metadata_to_use = own_metadata
                debug_logger.info(f"📊 Fichier .data.json inclus comme projet : {file_path}")
            
            if should_include:
                files_found.append((file_path, metadata_to_use))
    
    return files_found

def detect_file_encoding(file_path: str) -> str:
    """Détecte l'encodage d'un fichier texte."""
    # Liste des encodages à tester par ordre de priorité
    encodings = ['utf-8', 'utf-8-sig', 'cp1252', 'iso-8859-1', 'latin1']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                # Lire un échantillon pour valider l'encodage
                f.read(1024)
            return encoding
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    # Si aucun encodage ne fonctionne, utiliser latin1 qui accepte tous les bytes
    return 'latin1'

def extract_text_from_file(file_path: str) -> Optional[str]:
    """Extrait le texte d'un fichier selon son extension."""
    try:
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            return extract_text_from_pdf_file(file_path)
        elif file_ext == '.txt':
            return extract_text_from_txt_file(file_path)
        elif file_ext in ['.png', '.jpg', '.jpeg']:
            return extract_text_from_image_file(file_path)
        elif file_path.endswith('.data.json') or file_path.endswith('/.data.json'):
            return extract_text_from_data_json(file_path)
        else:
            return None
    except Exception as e:
        if 'st' in globals():
            st.error(f"Erreur extraction {file_path}: {e}")
        print(f"Erreur extraction {file_path}: {e}")
        return None

def extract_text_from_txt_file(file_path: str) -> Optional[str]:
    """Extrait le texte d'un fichier TXT avec détection automatique d'encodage."""
    try:
        # Détecter l'encodage automatiquement
        encoding = detect_file_encoding(file_path)
        
        with open(file_path, 'r', encoding=encoding) as f:
            content = f.read()
        
        # Log de l'encodage détecté si c'est dans Streamlit
        #if 'st' in globals() and encoding != 'utf-8':
            #st.info(f"📝 Fichier {os.path.basename(file_path)} lu avec encodage {encoding}")
        #elif encoding != 'utf-8':
            #print(f"Fichier {file_path} lu avec encodage {encoding}")
            
        return content
        
    except Exception as e:
        # Tentative de fallback avec errors='replace' pour éviter les crashes
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            if 'st' in globals():
                st.warning(f"⚠️ Caractères non-UTF8 remplacés dans {os.path.basename(file_path)}")
            else:
                print(f"Avertissement: Caractères non-UTF8 remplacés dans {file_path}")
                
            return content
            
        except Exception as e2:
            if 'st' in globals():
                st.error(f"Erreur lecture fichier TXT {file_path}: {e2}")
            print(f"Erreur lecture fichier TXT {file_path}: {e2}")
            return None

def extract_text_from_pdf_file(file_path: str) -> Optional[str]:
    """Extrait le texte d'un fichier PDF."""
    try:
        # Vérifier que le fichier n'est pas vide
        if os.path.getsize(file_path) == 0:
            debug_logger.warning(f"Fichier PDF vide ignoré : {os.path.basename(file_path)}")
            return None
        
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
    except (PyPDF2.errors.PdfReadError, PyPDF2.errors.PdfStreamError) as e:
        debug_logger.warning(f"Fichier PDF corrompu ou illisible ignoré {os.path.basename(file_path)}: {str(e)}")
        return None
    except Exception as e:
        debug_logger.error(f"Erreur extraction PDF {file_path}: {e}")
        return None

def extract_text_from_image_file(file_path: str) -> Optional[str]:
    """Extrait le texte d'une image via OCR."""
    try:
        # Vérifier que Tesseract est configuré
        if not hasattr(pytesseract.pytesseract, 'tesseract_cmd') or not pytesseract.pytesseract.tesseract_cmd:
            configure_tesseract()
        
        image = Image.open(file_path)
        # Convertir en OpenCV format pour améliorer la qualité OCR
        img_array = np.array(image)
        
        # Gérer les images en mode RGBA
        if len(img_array.shape) == 3 and img_array.shape[2] == 4:
            # Convertir RGBA en RGB
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
        elif len(img_array.shape) == 3:
            # Convertir RGB en BGR pour OpenCV
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Convertir en niveaux de gris
        gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY) if len(img_array.shape) == 3 else img_array
        
        # Améliorer la qualité pour l'OCR
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Extraire le texte avec gestion d'erreur spécifique
        try:
            text = pytesseract.image_to_string(thresh, lang='fra+eng')
            return text.strip()
        except pytesseract.TesseractNotFoundError:
            # Essayer de reconfigurer Tesseract
            tesseract_path = configure_tesseract()
            if tesseract_path:
                print(f"Tesseract reconfiguré vers: {tesseract_path}")
                text = pytesseract.image_to_string(thresh, lang='fra+eng')
                return text.strip()
            else:
                error_msg = "Tesseract OCR non trouvé. Veuillez installer Tesseract ou vérifier le PATH."
                if 'st' in globals():
                    st.warning(f"⚠️ {error_msg}")
                print(f"Avertissement OCR {file_path}: {error_msg}")
                return ""
                
    except Exception as e:
        if 'tesseract' in str(e).lower():
            error_msg = f"Erreur Tesseract: {str(e)}"
            if 'st' in globals():
                st.warning(f"⚠️ OCR non disponible pour {os.path.basename(file_path)}: {error_msg}")
            print(f"Avertissement OCR {file_path}: {error_msg}")
            return ""
        else:
            if 'st' in globals():
                st.error(f"Erreur OCR {file_path}: {e}")
            print(f"Erreur OCR {file_path}: {e}")
            return None

def read_notes_file(file_path: str) -> Dict:
    """Lit un fichier _notes.txt contenant des métadonnées JSON."""
    try:
        encoding = detect_file_encoding(file_path)
        
        with open(file_path, 'r', encoding=encoding) as f:
            notes_data = json.load(f)
        
        debug_logger.info(f"📝 Fichier notes trouvé : {file_path}")
        
        return notes_data if isinstance(notes_data, dict) else {}
        
    except Exception as e:
        debug_logger.error(f"Erreur lecture fichier notes {file_path}: {e}")
        return {}

def validate_file_path(file_path: str) -> bool:
    """Valide qu'un chemin de fichier existe et est accessible."""
    return os.path.exists(file_path) and os.path.isfile(file_path)

def validate_directory_path(directory_path: str) -> bool:
    """Valide qu'un chemin de répertoire existe et est accessible."""
    return os.path.exists(directory_path) and os.path.isdir(directory_path)

def get_file_size(file_path: str) -> int:
    """Retourne la taille d'un fichier en bytes."""
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0

def is_file_too_large(file_path: str, max_size_mb: int = 100) -> bool:
    """Vérifie si un fichier dépasse la taille maximale autorisée."""
    file_size = get_file_size(file_path)
    max_size_bytes = max_size_mb * 1024 * 1024
    return file_size > max_size_bytes

def merge_metadata_sources(rag_data: Dict, data_json: Dict, notes_data: Dict) -> Dict:
    """Fusionne les métadonnées de différentes sources avec priorité."""
    # Commencer par les données de base
    merged = rag_data.copy() if rag_data else {}
    
    # Ajouter les données .data.json si pas de ._rag_.data
    if not rag_data and data_json:
        # Utiliser les métadonnées déjà calculées par read_data_json_file
        merged = data_json.copy()
    
    # Enrichir avec les données notes (toujours appliquées)
    if notes_data:
        # Ajouter les clés du fichier notes qui ne sont pas déjà présentes
        for key, value in notes_data.items():
            if key not in merged or not merged[key]:
                merged[key] = value
        
        # Enrichir la description avec les notes
        if merged.get('description'):
            notes_description = _build_description_from_notes(notes_data)
            if notes_description:
                merged['description'] += f" | Notes: {notes_description}"
        else:
            merged['description'] = _build_description_from_notes(notes_data)
        
        # Enrichir les tags avec les notes
        existing_tags = merged.get('tags', '').split(',') if merged.get('tags') else []
        notes_tags = _build_tags_from_notes(notes_data)
        if notes_tags:
            all_tags = existing_tags + notes_tags.split(',')
            merged['tags'] = ','.join(list(set(filter(None, all_tags))))  # Supprimer les doublons
        
        # Marquer la source d'enrichissement
        if 'source_format' in merged:
            merged['source_format'] += '+notes'
        else:
            merged['source_format'] = 'notes_only'
        
        # Conserver les données originales des notes
        merged['notes_data'] = notes_data
    
    return merged

def _build_description_from_notes(notes_data: Dict) -> str:
    """Construit une description à partir des données de notes."""
    parts = []
    
    # Ajouter les paires clé-valeur importantes
    important_keys = ['description', 'resume', 'objectif', 'contexte', 'commentaire']
    for key in important_keys:
        if key in notes_data and notes_data[key]:
            parts.append(f"{key.capitalize()}: {notes_data[key]}")
    
    # Ajouter les autres clés (sauf celles déjà traitées)
    for key, value in notes_data.items():
        if key.lower() not in important_keys and value and isinstance(value, str):
            parts.append(f"{key}: {value}")
    
    return ' | '.join(parts)

def _build_tags_from_notes(notes_data: Dict) -> str:
    """Construit des tags à partir des données de notes."""
    tags = []
    
    # Tags basés sur des mots-clés dans les clés
    tag_keywords = ['tag', 'categorie', 'type', 'theme', 'sujet', 'domaine']
    for key, value in notes_data.items():
        key_lower = key.lower()
        if any(keyword in key_lower for keyword in tag_keywords) and value:
            if isinstance(value, str):
                tags.append(value)
    
    # Tags basés sur des valeurs booléennes ou indicateurs
    for key, value in notes_data.items():
        if isinstance(value, bool) and value:
            tags.append(key)
        elif isinstance(value, str) and value.lower() in ['true', 'oui', 'yes', 'o', '1']:
            tags.append(key)
    
    return ','.join(tags)

def detect_cv_files(files: List[str]) -> List[str]:
    """Détecte les fichiers CV de présentation (*_CV_*.pdf)."""
    cv_files = []
    for file in files:
        if ('_CV_' in file.upper() and 
            file.lower().endswith('.pdf')):
            cv_files.append(file)
    return cv_files

def detect_ba_files(files: List[str]) -> List[str]:
    """Détecte les fichiers BA de support oral (*_BA_*.pdf)."""
    ba_files = []
    for file in files:
        if ('_BA_' in file.upper() and 
            file.lower().endswith('.pdf')):
            ba_files.append(file)
    return ba_files

def enrich_metadata_with_presentation_files(metadata: Dict, cv_files: List[str], ba_files: List[str]) -> Dict:
    """Enrichit les métadonnées avec les informations des fichiers de présentation (CV et BA) et le niveau de maturité."""
    # Copier les métadonnées existantes
    enriched = metadata.copy() if metadata else {}
    
    # Ajouter les informations de présentation si disponibles
    if cv_files or ba_files:
        enriched['cv_files'] = cv_files
        enriched['ba_files'] = ba_files
        enriched['has_presentation'] = True
        enriched['presentation_count'] = len(cv_files) + len(ba_files)
        
        # Enrichir la description avec les présentations
        existing_desc = enriched.get('description', '')
        presentation_parts = []
        
        if cv_files:
            presentation_parts.append(f"{len(cv_files)} CV/candidature: {', '.join(cv_files)}")
        if ba_files:
            presentation_parts.append(f"{len(ba_files)} support oral: {', '.join(ba_files)}")
        
        presentation_info = f"Contient {' et '.join(presentation_parts)}"
        
        if existing_desc:
            enriched['description'] = f"{existing_desc} | {presentation_info}"
        else:
            enriched['description'] = presentation_info
        
        # Enrichir les tags
        existing_tags = enriched.get('tags', '')
        presentation_tags = []
        
        if cv_files:
            presentation_tags.extend(['presentation', 'CV', 'candidature'])
        if ba_files:
            presentation_tags.extend(['support-oral', 'BA', 'presentation-orale'])
        
        if existing_tags:
            all_tags = existing_tags.split(',') + presentation_tags
            enriched['tags'] = ','.join(set(all_tags))  # Éviter les doublons
        else:
            enriched['tags'] = ','.join(set(presentation_tags))
    
    # Ajouter le niveau de maturité (toujours, même sans fichiers de présentation)
    enriched = add_maturity_info(enriched, cv_files, ba_files)
    
    return enriched

def determine_project_maturity(metadata: Dict, cv_files: List[str], ba_files: List[str]) -> str:
    """Détermine le niveau de maturité du projet basé sur la présence des fichiers."""
    
    has_data_json = metadata.get('source_format') in ['data_json', 'data_json+notes']
    has_cv = len(cv_files) > 0
    has_ba = len(ba_files) > 0
    
    # Logique de maturité
    if not has_data_json:
        return 'Idée'  # Pas de .data.json = simple idée
    elif has_data_json and not has_cv and not has_ba:
        return 'Initié'  # .data.json seul = projet initié
    elif has_data_json and has_cv and not has_ba:
        return 'Envoyé'  # .data.json + CV = candidature envoyée
    elif has_data_json and has_cv and has_ba:
        return 'Démarche'  # .data.json + CV + BA = entretien oral prévu/réalisé
    else:
        return 'Initié'  # Cas par défaut

def add_maturity_info(metadata: Dict, cv_files: List[str], ba_files: List[str]) -> Dict:
    """Ajoute les informations de maturité aux métadonnées."""
    enriched = metadata.copy() if metadata else {}
    
    # Déterminer le niveau de maturité
    maturity = determine_project_maturity(metadata, cv_files, ba_files)
    enriched['maturity_level'] = maturity
    
    # Ajouter des tags de maturité
    existing_tags = enriched.get('tags', '')
    maturity_tag = f'maturité-{maturity.lower()}'
    
    if existing_tags:
        all_tags = existing_tags.split(',') + [maturity_tag]
        enriched['tags'] = ','.join(set(all_tags))  # Éviter les doublons
    else:
        enriched['tags'] = maturity_tag
    
    # Enrichir la description avec le niveau de maturité
    existing_desc = enriched.get('description', '')
    maturity_info = f"Niveau de maturité: {maturity}"
    
    if existing_desc:
        enriched['description'] = f"{existing_desc} | {maturity_info}"
    else:
        enriched['description'] = maturity_info
    
    # Ajuster la priorité selon la maturité
    if maturity in ['Envoyé', 'Démarche'] and not enriched.get('priority'):
        enriched['priority'] = 'high'
    elif maturity == 'Initié' and not enriched.get('priority'):
        enriched['priority'] = 'normal'
    elif maturity == 'Idée' and not enriched.get('priority'):
        enriched['priority'] = 'low'
    
    return enriched

def extract_text_from_data_json(file_path: str) -> Optional[str]:
    """Extrait et formaté le contenu d'un fichier .data.json pour l'indexation."""
    try:
        # Lire et parser le fichier .data.json
        data_json_data = read_data_json_file(file_path)
        
        if not data_json_data:
            return None
        
        # Construire un texte recherchable à partir des métadonnées
        text_parts = []
        
        # Titre du projet
        if data_json_data.get('project'):
            text_parts.append(f"PROJET: {data_json_data['project']}")
        
        # Description principale
        if data_json_data.get('description'):
            text_parts.append(f"DESCRIPTION: {data_json_data['description']}")
        
        # Catégorie
        if data_json_data.get('category'):
            text_parts.append(f"CATÉGORIE: {data_json_data['category']}")
        
        # Auteur/Contact
        if data_json_data.get('author'):
            text_parts.append(f"AUTEUR: {data_json_data['author']}")
        
        # Date
        if data_json_data.get('date'):
            text_parts.append(f"DATE: {data_json_data['date']}")
        
        # Tags
        if data_json_data.get('tags'):
            text_parts.append(f"TAGS: {data_json_data['tags']}")
        
        # Données originales pour la recherche
        original_data = data_json_data.get('original_data', {})
        
        # Ajouter les champs importants du .data.json original
        important_fields = [
            'dossier', 'entreprise', 'action', 'todo', 'Commentaire', 
            'Lieu', 'Origine', 'contact', 'tel', 'mail', 'url'
        ]
        
        for field in important_fields:
            value = original_data.get(field)
            if value and str(value).strip() and value != 'N/A':
                text_parts.append(f"{field.upper()}: {value}")
        
        # Joindre tout le texte
        full_text = "\n".join(text_parts)
        
        debug_logger.info(f"📊 Texte extrait du .data.json : {len(full_text)} caractères")
        
        return full_text
        
    except Exception as e:
        debug_logger.error(f"Erreur extraction .data.json {file_path}: {e}")
        return None
