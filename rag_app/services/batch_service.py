"""Service de traitement par lots."""

import os
from typing import List, Tuple, Dict, Callable, Optional, Any
from pathlib import Path
import streamlit as st

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
        """Traite tous les fichiers d'un répertoire."""
        
        if not validate_directory_path(directory):
            return {'error': f"Répertoire non accessible: {directory}"}
        
        # Trouver tous les fichiers
        files_found = find_files_recursive(directory, file_extensions)
        
        results = {
            'success': 0,
            'errors': 0,
            'skipped': 0,
            'errors_list': [],
            'images_processed': [],
            'total_files': len(files_found)
        }
        
        total_files = len(files_found)
        
        for i, (file_path, annonce_data) in enumerate(files_found):
            try:
                if progress_callback:
                    progress_callback(i, total_files, file_path)
                    
                # Vérifier la taille du fichier
                if is_file_too_large(file_path, self.max_file_size_mb):
                    results['skipped'] += 1
                    results['errors_list'].append(f"{file_path}: Fichier trop volumineux")
                    continue
                    
                # Traiter selon le type de fichier
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
            'category': annonce_data.get('category', 'Non classé'),
            'project': annonce_data.get('project', 'Projet par défaut'),
            'author': annonce_data.get('author', 'Inconnu'),
            'date': annonce_data.get('date', ''),
            'description': annonce_data.get('description', ''),
            'tags': annonce_data.get('tags', ''),
            'priority': annonce_data.get('priority', 'normal'),
            'status': annonce_data.get('status', 'active')
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
