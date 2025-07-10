"""Module de base de données vectorielle refactorisé."""

import pickle
import numpy as np
from typing import List, Dict, Optional, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
import os

from ..config.settings import VECTOR_DB_FILE

class VectorDatabase:
    """Base de données vectorielle optimisée et modulaire."""
    
    def __init__(self):
        self.documents = []
        self.images = []
        self.vectors = None
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
    def add_document(self, text: str, metadata: Dict[str, Any]) -> None:
        """Ajoute un document à la base vectorielle."""
        document = {
            'text': text,
            'metadata': metadata,
            'timestamp': datetime.now().isoformat(),
            'type': 'document'
        }
        self.documents.append(document)
        self._update_vectors()
        
    def add_image(self, image_path: str, text_content: str, description: str, 
                  categories: List[str], metadata: Dict[str, Any]) -> None:
        """Ajoute une image à la base vectorielle."""
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
        
        # Ajouter aussi comme document pour la recherche textuelle
        self.documents.append({
            'text': search_text,
            'metadata': {**metadata, 'type': 'image', 'image_path': image_path},
            'timestamp': datetime.now().isoformat(),
            'type': 'image_document'
        })
        
        self._update_vectors()
        
    def _update_vectors(self) -> None:
        """Met à jour les vecteurs TF-IDF."""
        if not self.documents:
            self.vectors = None
            return
            
        texts = [doc['text'] for doc in self.documents]
        try:
            self.vectors = self.vectorizer.fit_transform(texts)
        except Exception as e:
            print(f"Erreur lors de la vectorisation: {e}")
            self.vectors = None
            
    def search(self, query: str, top_k: int = 5, filter_by: Optional[Dict] = None,
               filter_type: Optional[str] = None) -> List[Dict]:
        """Recherche les documents les plus similaires avec filtrage optionnel."""
        if not self.documents or self.vectors is None:
            return []
            
        # Vectoriser la requête
        try:
            query_vector = self.vectorizer.transform([query])
        except Exception:
            return []
            
        # Calculer les similarités
        similarities = cosine_similarity(query_vector, self.vectors)[0]
        
        # Obtenir les indices triés par similarité décroissante
        top_indices = np.argsort(similarities)[::-1]
        
        results = []
        for idx in top_indices:
            if similarities[idx] < 0.1:  # Seuil de similarité minimum
                break
                
            document = self.documents[idx]
            
            # Appliquer les filtres si spécifiés
            if filter_by and not self._matches_filter(document, filter_by):
                continue
                
            if filter_type and document.get('type') != filter_type:
                continue
                
            results.append({
                'document': document,
                'similarity': float(similarities[idx])
            })
            
            if len(results) >= top_k:
                break
                
        return results
        
    def _matches_filter(self, document: Dict, filter_by: Dict) -> bool:
        """Vérifie si un document correspond aux critères de filtrage."""
        metadata = document.get('metadata', {})
        
        for key, values in filter_by.items():
            if isinstance(values, list):
                doc_value = metadata.get(key, '')
                if not any(val.lower() in doc_value.lower() for val in values):
                    return False
            else:
                if metadata.get(key, '').lower() != values.lower():
                    return False
                    
        return True
        
    def get_image_by_categories(self, categories: List[str]) -> List[Dict]:
        """Récupère les images par catégories."""
        filtered_images = []
        for img in self.images:
            img_categories = img.get('categories', [])
            if any(cat in img_categories for cat in categories):
                filtered_images.append(img)
        return filtered_images
        
    def get_all_images(self) -> List[Dict]:
        """Récupère toutes les images."""
        return self.images.copy()
        
    def get_categories(self) -> List[str]:
        """Retourne toutes les catégories disponibles."""
        categories = set()
        for doc in self.documents:
            category = doc.get('metadata', {}).get('category')
            if category:
                categories.add(category)
        return sorted(list(categories))
        
    def get_projects(self) -> List[str]:
        """Retourne tous les projets disponibles."""
        projects = set()
        for doc in self.documents:
            project = doc.get('metadata', {}).get('project')
            if project:
                projects.add(project)
        return sorted(list(projects))
        
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de la base."""
        categories = self.get_categories()
        projects = self.get_projects()
        
        total_chars = sum(len(doc['text']) for doc in self.documents)
        
        return {
            'total_documents': len(self.documents),
            'total_images': len(self.images),
            'total_characters': total_chars,
            'categories': len(categories),
            'projects': len(projects),
            'categories_list': categories,
            'projects_list': projects,
            'has_vectors': self.vectors is not None
        }
        
    def save(self, filepath: str = None) -> None:
        """Sauvegarde la base vectorielle."""
        if filepath is None:
            filepath = str(VECTOR_DB_FILE)
            
        # Créer le dossier si nécessaire
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        try:
            with open(filepath, 'wb') as f:
                pickle.dump(self, f)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
            
    @classmethod
    def load(cls, filepath: str = None) -> 'VectorDatabase':
        """Charge la base vectorielle depuis un fichier."""
        if filepath is None:
            filepath = str(VECTOR_DB_FILE)
            
        try:
            with open(filepath, 'rb') as f:
                db = pickle.load(f)
                # Vérification de compatibilité
                if isinstance(db, cls):
                    return db
                else:
                    print("Format de base incompatible, création d'une nouvelle base.")
                    return cls()
        except (FileNotFoundError, EOFError, pickle.UnpicklingError):
            print("Aucune base existante trouvée, création d'une nouvelle base.")
            return cls()
        except Exception as e:
            print(f"Erreur lors du chargement: {e}")
            return cls()
            
    def clear(self) -> None:
        """Vide complètement la base de données."""
        self.documents = []
        self.images = []
        self.vectors = None
        
    def remove_document(self, index: int) -> bool:
        """Supprime un document par son index."""
        try:
            if 0 <= index < len(self.documents):
                self.documents.pop(index)
                self._update_vectors()
                return True
            return False
        except Exception:
            return False
