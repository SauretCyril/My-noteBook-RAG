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
        if 'st' in globals():
            st.error(f"Erreur lecture fichier d'annonce {file_path}: {e}")
        print(f"Erreur lecture fichier d'annonce {file_path}: {e}")
        return {}

def find_files_recursive(directory: str, extensions: List[str]) -> List[Tuple[str, Dict]]:
    """Trouve tous les fichiers avec les extensions spécifiées de manière récursive."""
    files_found = []
    
    for root, dirs, files in os.walk(directory):
        # Chercher un fichier d'annonce dans ce répertoire
        annonce_data = {}
        annonce_files = [f for f in files if f.startswith('._rag_.') and f.endswith('.data')]
        
        if annonce_files:
            annonce_path = os.path.join(root, annonce_files[0])
            annonce_data = read_annonce_file(annonce_path)
            if 'st' in globals():
                st.info(f"📋 Fichier d'annonce trouvé : {annonce_path}")
        
        # Chercher les fichiers à traiter
        for file in files:
            file_path = os.path.join(root, file)
            file_ext = os.path.splitext(file)[1].lower()
            
            if file_ext in extensions and not file.startswith('._rag_.'):
                files_found.append((file_path, annonce_data))
    
    return files_found

def extract_text_from_file(file_path: str) -> Optional[str]:
    """Extrait le texte d'un fichier selon son extension."""
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
        if 'st' in globals():
            st.error(f"Erreur extraction {file_path}: {e}")
        print(f"Erreur extraction {file_path}: {e}")
        return None

def extract_text_from_pdf_file(file_path: str) -> Optional[str]:
    """Extrait le texte d'un fichier PDF."""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        if 'st' in globals():
            st.error(f"Erreur extraction PDF {file_path}: {e}")
        print(f"Erreur extraction PDF {file_path}: {e}")
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
