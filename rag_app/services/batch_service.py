"""Service de traitement par lots."""

import os
from typing import List, Tuple, Dict, Callable, Optional, Any
from pathlib import Path
import streamlit as st
import json

from ..core.vector_database import VectorDatabase
from ..utils.file_utils import (
    find_files_recursive, 
    extract_text_from_file,
    validate_directory_path,
    is_file_too_large
)
from ..config.settings import PROCESSING_CONFIG

class BatchService:
    """Service pour le traitement par lots de documents et images."""
    
    def __init__(self, vector_db: VectorDatabase):
        self.vector_db = vector_db
        self.max_file_size_mb = PROCESSING_CONFIG.get('max_file_size_mb', 100)
        
    def process_directory(
        self, 
        directory: str,
        file_extensions: List[str],
        progress_callback: Optional[Callable] = None,
        enable_vision: bool = False
    ) -> Dict[str, Any]:
        """Traite tous les fichiers de tous les sous-répertoires avec leur .data.json respectif."""
        results = {
            'success': 0,
            'errors': 0,
            'skipped': 0,
            'errors_list': [],
            'images_processed': [],
            'total_files': 0
        }

        # Parcours récursif de tous les sous-répertoires
        for root, dirs, files in os.walk(directory):
            # Cherche le .data.json dans le sous-répertoire courant
            data_json_files = [f for f in files if f.endswith('.data.json')]
            if data_json_files:
                data_json_path = os.path.join(root, data_json_files[0])
                try:
                    with open(data_json_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            annonce_data = json.loads(content)
                        else:
                            print(f"⚠️ Fichier .data.json vide : {data_json_path}")
                            annonce_data = {}
                except Exception as e:
                    print(f"⚠️ Erreur lecture .data.json : {data_json_path} : {e}")
                    annonce_data = {}
            else:
                annonce_data = {}

            # Fichiers à indexer dans ce sous-répertoire (hors .data.json)
            files_found = [
                os.path.join(root, f)
                for f in files
                if os.path.splitext(f)[1].lower() in file_extensions and not f.endswith('.data.json')
            ]
            results['total_files'] += len(files_found)

            for i, file_path in enumerate(files_found):
                try:
                    if progress_callback:
                        progress_callback(i, len(files_found), file_path)
                    file_ext = Path(file_path).suffix.lower()
                    if file_ext in ['.pdf', '.txt']:
                        success = self._process_document(file_path, annonce_data)
                        if success:
                            results['success'] += 1
                        else:
                            results['errors'] += 1
                    elif file_ext in ['.png', '.jpg', '.jpeg'] and enable_vision:
                        img_result = self._process_image(file_path, annonce_data)
                        if img_result:
                            results['images_processed'].append(img_result)
                            results['success'] += 1
                        else:
                            results['skipped'] += 1
                    else:
                        results['skipped'] += 1
                except Exception as e:
                    results['errors'] += 1
                    results['errors_list'].append(f"{file_path}: {str(e)}")

        return results
        
    def _process_document(self, file_path: str, annonce_data: Dict) -> bool:
        """Traite un document (PDF ou TXT)."""
        try:
            # Extraire le texte
            text = extract_text_from_file(file_path)
            if not text or len(text.strip()) < 10:
                return False
                
            # Préparer les métadonnées
            metadata = self._prepare_metadata(file_path, annonce_data)
            
            # Ajouter à la base vectorielle
            self.vector_db.add_document(text, metadata)
            
            return True
            
        except Exception as e:
            st.error(f"Erreur traitement document {file_path}: {e}")
            return False
            
    def _process_image(self, image_path: str, annonce_data: Dict) -> Optional[Dict]:
        """Traite une image avec OCR et analyse."""
        try:
            # OCR pour extraire le texte
            text_content = extract_text_from_file(image_path) or ""
            
            # Description automatique (stub pour l'instant)
            description = self._generate_image_description(image_path)
            
            # Classification automatique
            categories = self._classify_image_content(image_path, text_content, description)
            
            # Préparer les métadonnées
            metadata = self._prepare_metadata(image_path, annonce_data)
            metadata['type'] = 'image'
            
            # Ajouter à la base vectorielle
            self.vector_db.add_image(
                image_path=image_path,
                text_content=text_content,
                description=description,
                categories=categories,
                metadata=metadata
            )
            
            return {
                'file': image_path,
                'description': description,
                'categories': categories,
                'ocr_text': text_content[:100] + "..." if len(text_content) > 100 else text_content
            }
            
        except Exception as e:
            st.error(f"Erreur traitement image {image_path}: {e}")
            return None
            
    def _prepare_metadata(self, file_path: str, annonce_data: Dict) -> Dict[str, Any]:
        """Prépare les métadonnées pour un fichier."""
        file_name = os.path.basename(file_path)
        
        metadata = {
            'source': file_path,
            'title': annonce_data.get('title', file_name),
            'categorie': annonce_data.get('categorie', annonce_data.get('category', 'inconnu')),
            'project': annonce_data.get('project', annonce_data.get('dossier', 'Non spécifié')),
            'author': annonce_data.get('author', 'Cyril Sauret'),
            'date': annonce_data.get('date', ''),
            'description': annonce_data.get('description', ''),
            'tags': annonce_data.get('tags', ''),
            'todo': annonce_data.get('Todo', ''),
            'status': annonce_data.get('Etat', '?'),
            'entreprise': annonce_data.get('entreprise', 'inconnu'),
            'commentaire': annonce_data.get('commentaire', ''),
            'Date_from': annonce_data.get('Date_from', ''),
            'Date_rep': annonce_data.get('Date_rep', ''),
            'contact': annonce_data.get('contact', ''),
            'id': annonce_data.get('id', ''),
            'mail': annonce_data.get('mail', ''),


            # Ajoute ici tous les autres champs nécessaires
        }
        
        return metadata
        
    def _generate_image_description(self, image_path: str) -> str:
        """Génère une description automatique de l'image (stub)."""
        # TODO: Intégrer le modèle BLIP pour la description automatique
        file_name = os.path.basename(image_path)
        return f"Image: {file_name}"
        
    def _classify_image_content(self, image_path: str, text_content: str = "", description: str = "") -> List[str]:
        """Classifie le contenu de l'image en catégories."""
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
        
        # Classification basée sur l'extension
        file_ext = Path(image_path).suffix.lower()
        if file_ext in ['.png', '.jpg', '.jpeg']:
            categories.append('Image')
            
        # Catégorie par défaut
        if not categories:
            categories.append('Image non classée')
            
        return categories
        
    def get_supported_extensions(self) -> Dict[str, List[str]]:
        """Retourne les extensions de fichiers supportées."""
        return {
            'documents': ['.pdf', '.txt'],
            'images': ['.png', '.jpg', '.jpeg'],
            'all': ['.pdf', '.txt', '.png', '.jpg', '.jpeg']
        }
