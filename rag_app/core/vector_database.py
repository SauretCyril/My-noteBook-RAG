#Module de base de données vectorielle refactorisé.

import pickle
import numpy as np
from typing import List, Dict, Optional, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
import os

from ..config.settings import VECTOR_DB_FILE
#Base de données vectorielle optimisée et modulaire.
class VectorDatabase:
    #Classe pour gérer une base de données vectorielle avec des documents et des images.

    def __init__(self):
        self.documents = []
        self.images = []
        self.vectors = None
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        # Compteurs globaux pour les annonces
        self.stats = {
            'annonces_new': 0,
            'annonces_attente': 0
        }

    def _apply_project_rules(self, meta: Dict[str, Any]) -> Dict[str, Any]:
        """Applique les règles d'enrichissement des métadonnées selon le type de projet."""
        # Prend en compte  et 'categorie' (orthographe alternative)
        category = meta.get('categorie', '').strip().upper()
        # Règles pour Annonce
        if category == 'ANNONCE':
            etat = str(meta.get('Etat', '')).strip().upper()
            todo = str(meta.get('Todo', '')).strip().upper()
            if etat == 'NEW':
                meta['statut_annonce'] = 'Annonce non postulé'
            elif etat == 'TODO' and 'RÉPONDUE' in todo:
                meta['statut_annonce'] = 'Attente'
        # Squelette pour autres types
        elif category == 'ATELIER':
            # TODO: Ajouter les règles spécifiques Atelier
            pass
        elif category == 'PORTAIL':
            # TODO: Ajouter les règles spécifiques Portail
            pass
        elif category == 'DOSSIER':
            # TODO: Ajouter les règles spécifiques Dossier
            pass
        elif category == 'PUBLICATION':
            # TODO: Ajouter les règles spécifiques Publication
            pass
        elif category == 'DEV':
            # TODO: Ajouter les règles spécifiques DEV
            pass
        # Ajoutez ici d'autres types et règles
        return meta

    def _detect_annonce_category(self, text: str) -> bool:
        """Détecte si le contenu correspond à une offre d'emploi (catégorie 'Annonce')."""
        if not text or len(text) < 50:
            return False
        # Critères typiques d'une annonce d'emploi (à adapter selon vos données)
        keywords = [
            "poste à pourvoir", "profil recherché", "missions", "responsabilités", "candidature", "envoyer votre cv", "recrutement", "contrat", "rémunération", "description du poste", "compétences requises", "nous recherchons", "offre d'emploi", "type de contrat", "expérience exigée", "salaire", "contact rh", "processus de recrutement"
        ]
        text_lower = text.lower()
        matches = sum(1 for kw in keywords if kw in text_lower)
        return matches >= 2  # Au moins 2 mots-clés pour valider

    def _build_enriched_text(self, text: str, metadata: Dict[str, Any]) -> str:
        """Construit un texte enrichi à partir des métadonnées pour améliorer l'indexation."""
        parts = []
        # Ajout des métadonnées clés (sans 'title')
        for key in ["entreprise", "company", "enterprise", "categorie", "author", "date", "description", "tags"]:
            val = metadata.get(key)
            if val and val != "N/A" and str(val).strip():
                parts.append(f"{key.capitalize()}: {val}")
        # Ajout du champ project construit
        dossier = metadata.get('dossier', '').strip()
        description = metadata.get('description', '').strip()
        if dossier and description:
            project_value = f"{dossier}_{description}"
            parts.append(f"Project: {project_value}")
        # Ajout du texte principal
        if text and text.strip():
            parts.append(text.strip())
        # Nettoyage et suppression des doublons
        unique_parts = []
        seen = set()
        for part in parts:
            part_clean = part.strip()
            if part_clean and part_clean not in seen:
                unique_parts.append(part_clean)
                seen.add(part_clean)
        return "\n".join(unique_parts)

    # def add_document(self, text: str, metadata: Dict[str, Any]) -> None:
    #     """Ajoute un document à la base vectorielle avec enrichissement du texte, application des règles projet, détection d'anomalies et mise à jour des compteurs annonces."""
    #     meta = dict(metadata)  # Copie pour ne pas modifier l'original
    #     # Détection automatique de la catégorie 'Annonce' selon le contenu
    #     if self._detect_annonce_category(text) and not meta.get('categorie'):
    #         meta['categorie'] = 'Annonce'
    #     # Construction du champ project à partir de dossier + '_' + description
    #     dossier = meta.get('dossier', '').strip()
    #     description = meta.get('description', '').strip()
    #     if dossier and description:
    #         meta['project'] = f"{dossier}_{description}"
    #     # Application des règles selon le type de projet
    #     meta = self._apply_project_rules(meta)
    #     # Détection d'anomalies sur les métadonnées
    #     anomalies = self._detect_metadata_anomalies(meta)
    #     if anomalies:
    #         meta['anomalies'] = anomalies
    #     # Mise à jour des compteurs pour les annonces
    #     cat_value = meta.get('categorie', '').strip().lower()
    #     if cat_value == 'annonce':
    #         etat = str(meta.get('Etat', '')).strip().lower()
    #         todo = str(meta.get('Todo', '')).strip().lower()
    #         if etat == 'new':
    #             self.stats['annonces_new'] += 1
    #         elif etat == 'todo' and 'répondue' in todo:
    #             self.stats['annonces_attente'] += 1
    #     enriched_text = self._build_enriched_text(text, meta)
    #     document = {
    #         'text': enriched_text,
    #         'metadata': meta,
    #         'timestamp': datetime.now().isoformat(),
    #         'type': 'document'
    #     }
    #     self.documents.append(document)
    #     self._update_vectors()
    def _detect_metadata_anomalies(self, meta: Dict[str, Any]) -> list:
        """Détecte les anomalies dans les métadonnées d'un document .data.json et retourne une liste d'anomalies."""
        anomalies = []
        # Champs obligatoires
        required_fields = [ 'categorie', 'date', 'description']
        for field in required_fields:
            val = meta.get(field, None)
            if not val or str(val).strip() in ('', 'N/A', 'None', 'null'):
                anomalies.append(f"Champ manquant ou vide: {field}")
            if not val or str(val).strip() in ('Dossier Vide'):
                anomalies.append(f"Dossier Nouveau à renseigner")
        # Format de la date
        date_val = meta.get('date', None)
        if date_val:
            try:
                # Tenter de parser la date (format ISO ou courant)
                from dateutil.parser import parse
                parse(str(date_val))
            except Exception:
                anomalies.append(f"Format de date invalide: {date_val}")
        # Catégorie incohérente
        # Utilise uniquement 'categorie' (présent dans les fichiers .data.json)
        category = meta.get('categorie', '').strip().lower()
        valid_categories = ['annonce', 'atelier', 'portail', 'dossier', 'publication', 'dev', 'documentation', 'cv', 'lettre', 'formation', 'marketing', 'technique', 'finance', 'juridique']
        if category and category not in valid_categories:
            anomalies.append(f"Catégorie inconnue ou incohérente: {category}")
        # Doublons ou incohérences entre champs
        # Ajoutez ici d'autres règles métier spécifiques
        return anomalies
        
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
            category = doc.get('metadata', {}).get('categorie')
            if category:
                categories.add(category)
        return sorted(list(categories))
        
    def get_projects(self) -> List[str]:
        """Retourne tous les projets disponibles."""
        projects = set()
        for doc in self.documents:
            meta = doc.get('metadata', {})
            dossier = meta.get('dossier', '').strip()
            description = meta.get('description', '').strip()
            if dossier and description:
                project_value = f"{dossier}_{description}"
                projects.add(project_value)
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

    def add_document(self, text: str, metadata: Dict[str, Any]) -> None:
        """Ajoute un document à la base vectorielle avec enrichissement du texte, application des règles projet, détection d'anomalies et mise à jour des compteurs annonces."""
        meta = dict(metadata)  # Copie pour ne pas modifier l'original
        # Détection automatique de la catégorie 'Annonce' selon le contenu
        if self._detect_annonce_category(text) and not meta.get('categorie'):
            meta['categorie'] = 'Annonce'
        # Construction du champ project à partir de dossier + '_' + description
        dossier = meta.get('dossier', '').strip()
        description = meta.get('description', '').strip()
        if dossier and description:
            meta['project'] = f"{dossier}_{description}"
        # Application des règles selon le type de projet
        meta = self._apply_project_rules(meta)
        # Détection d'anomalies sur les métadonnées
        anomalies = self._detect_metadata_anomalies(meta)
        if anomalies:
            meta['anomalies'] = anomalies
        # Mise à jour des compteurs pour les annonces
        cat_value = meta.get('categorie', '').strip().lower()
        if cat_value == 'annonce':
            etat = str(meta.get('Etat', '')).strip().lower()
            todo = str(meta.get('Todo', '')).strip().lower()
            if etat == 'new':
                self.stats['annonces_new'] += 1
            elif etat == 'todo' and 'répondue' in todo:
                self.stats['annonces_attente'] += 1
        enriched_text = self._build_enriched_text(text, meta)
        document = {
            'text': enriched_text,
            'metadata': meta,
            'timestamp': datetime.now().isoformat(),
            'type': 'document'
        }
        self.documents.append(document)
        self._update_vectors()
        meta = dict(metadata)
        # Extraction de l'entreprise depuis les tags si le champ est absent
        if not meta.get('entreprise'):
            tags = meta.get('tags', '')
            # Exemple : si le tag contient 'engIT', l'entreprise est engIT
            # Adapte ce parsing selon ta convention de tags
            for tag in tags.split(','):
                tag = tag.strip()
                # Ajoute ici une liste blanche ou une regex si besoin
                if tag and tag.lower() not in ['annonce', 'gpt-summary', 'maturité-initié', 'todo']:
                    meta['entreprise'] = tag
                    break

    def verify_entreprise_indexation(self) -> None:
        """Affiche un rapport exhaustif sur la présence et la valeur du champ 'entreprise' dans chaque document."""
        print("=== Vérification exhaustive du champ 'entreprise' ===")
        total = len(self.documents)
        missing = 0
        for i, doc in enumerate(self.documents, 1):
            meta = doc.get('metadata', {})
            entreprise = meta.get('entreprise', None)
            print(f"Document {i}/{total} : entreprise = {repr(entreprise)} | source = {meta.get('source', '')}")
            if not entreprise or entreprise in ["", "N/A", "None", None]:
                missing += 1
        print(f"\nTotal documents : {total}")
        print(f"Documents sans entreprise : {missing}")
        print(f"Documents avec entreprise : {total - missing}")
