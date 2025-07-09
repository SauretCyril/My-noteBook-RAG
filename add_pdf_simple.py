"""
Script simple pour ajouter un fichier PDF au système RAG.

Ce script prend un chemin de fichier PDF prédéfini et l'intègre à la base de 
connaissances RAG sans nécessiter de paramètres en ligne de commande.
"""

import os
import sys
import json
import PyPDF2
import nltk
from nltk.tokenize import sent_tokenize
from typing import List, Dict
import re

# Configuration - MODIFIEZ CES VALEURS SELON VOS BESOINS
PDF_PATH = "H:/Entreprendre/Actions-4b_new/A002/A002_CV_CyrilSauret.pdf"  # Chemin vers votre PDF
CREATE_BACKUP = True  # True pour créer une sauvegarde, False sinon
VIEW_ONLY = False  # True pour seulement afficher l'extraction sans ajouter à la base

# Répertoire de données par défaut
DATA_DIR = 'data'
DOCS_FILE = os.path.join(DATA_DIR, 'anthropic_docs.json')

def setup_directories():
    """Crée les répertoires nécessaires s'ils n'existent pas"""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Créer un fichier de documents vide s'il n'existe pas
    if not os.path.exists(DOCS_FILE):
        with open(DOCS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)
        print(f"Fichier de documents créé: {DOCS_FILE}")

def ensure_nltk_resources():
    """S'assure que les ressources NLTK requises sont téléchargées"""
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        print("Téléchargement des ressources NLTK...")
        nltk.download('punkt', quiet=True)

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extrait le texte d'un fichier PDF.
    
    Args:
        pdf_path: Chemin vers le fichier PDF
        
    Returns:
        Le texte extrait du PDF
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Le fichier {pdf_path} n'existe pas")
    
    try:
        with open(pdf_path, 'rb') as file:
            # Créer un lecteur PDF
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Extraire le texte de chaque page
            text = ""
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:  # Vérifier que le texte a bien été extrait
                        text += page_text + "\n\n"
                except Exception as e:
                    print(f"⚠️ Erreur à l'extraction de la page {page_num}: {str(e)}")
                    
            if not text.strip():
                print("⚠️ Aucun texte n'a pu être extrait du PDF. Vérifiez que le PDF n'est pas numérisé ou protégé.")
                
            return text
    except Exception as e:
        raise Exception(f"Erreur lors de l'extraction du texte du PDF: {str(e)}")

def get_pdf_metadata(pdf_path: str) -> Dict:
    """
    Récupère les métadonnées d'un fichier PDF.
    
    Args:
        pdf_path: Chemin vers le fichier PDF
        
    Returns:
        Un dictionnaire contenant les métadonnées du PDF
    """
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        metadata = pdf_reader.metadata
        
        # Convertir les métadonnées en dictionnaire Python standard
        info = {}
        if metadata:
            for key in metadata:
                try:
                    # Nettoyer la clé en retirant les caractères spéciaux
                    clean_key = key
                    if clean_key.startswith('/'):
                        clean_key = clean_key[1:]
                    info[clean_key] = str(metadata[key])
                except:
                    pass
                
        # Ajouter le nombre de pages
        info['page_count'] = len(pdf_reader.pages)
        
    return info

def chunk_text(text: str, max_chunk_size: int = 2000, overlap: int = 200) -> List[str]:
    """
    Divise un texte long en chunks plus petits avec chevauchement.
    
    Args:
        text: Le texte à diviser
        max_chunk_size: Taille maximale d'un chunk en caractères
        overlap: Chevauchement entre les chunks en caractères
        
    Returns:
        Une liste de chunks de texte
    """
    # Si le texte est déjà assez court, le retourner tel quel
    if len(text) <= max_chunk_size:
        return [text]
    
    try:
        # Utiliser la tokenization par phrases pour éviter de couper au milieu d'une phrase
        sentences = sent_tokenize(text)
    except Exception as e:
        print(f"⚠️ Erreur lors de la tokenization: {str(e)}. Utilisation d'une méthode simple de découpage.")
        # Méthode alternative simple si NLTK échoue
        sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = []
    current_size = 0
    
    for sentence in sentences:
        sentence_size = len(sentence)
        
        # Si une seule phrase est trop longue, il faudra la couper brutalement
        if sentence_size > max_chunk_size:
            if current_chunk:  # Ajouter le chunk actuel s'il existe
                chunks.append(' '.join(current_chunk))
                
            # Diviser la phrase longue en morceaux
            for i in range(0, sentence_size, max_chunk_size - overlap):
                chunk = sentence[i:i + max_chunk_size]
                if len(chunk) >= max_chunk_size / 2:  # Éviter les chunks trop petits
                    chunks.append(chunk)
            
            current_chunk = []
            current_size = 0
        # Sinon, ajouter la phrase au chunk actuel ou en créer un nouveau
        elif current_size + sentence_size > max_chunk_size:
            chunks.append(' '.join(current_chunk))
            
            # Commencer un nouveau chunk avec chevauchement
            overlap_start = max(0, len(current_chunk) - 2)  # Utiliser les 2 dernières phrases pour le chevauchement
            current_chunk = current_chunk[overlap_start:] + [sentence]
            current_size = sum(len(s) for s in current_chunk)
        else:
            current_chunk.append(sentence)
            current_size += sentence_size
    
    # Ajouter le dernier chunk s'il existe
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def pdf_to_rag_documents(pdf_path: str) -> List[Dict]:
    """
    Convertit un fichier PDF en format de documents pour le système RAG.
    
    Args:
        pdf_path: Chemin vers le fichier PDF
        
    Returns:
        Une liste de documents au format attendu par le système RAG
    """
    # Extraire le texte complet du PDF
    print(f"Extraction du texte de {pdf_path}...")
    text = extract_text_from_pdf(pdf_path)
    
    if not text.strip():
        return []
    
    # Obtenir les métadonnées du PDF
    print("Extraction des métadonnées...")
    metadata = get_pdf_metadata(pdf_path)
    
    # Découper le texte en chunks
    print("Segmentation du document en fragments...")
    chunks = chunk_text(text)
    
    documents = []
    file_name = os.path.basename(pdf_path)
    
    for i, chunk in enumerate(chunks):
        documents.append({
            "chunk_heading": f"{file_name} - Partie {i+1}/{len(chunks)}",
            "text": chunk,
            "chunk_link": f"{file_name.replace('.pdf', '')}-part-{i+1}",
            "source": pdf_path,
            "metadata": metadata
        })
    
    print(f"✅ {len(documents)} fragments extraits")
    return documents

def add_documents_to_database(documents: List[Dict], docs_file: str, create_backup: bool = True):
    """
    Ajoute des documents à la base de données
    
    Args:
        documents: Liste de documents à ajouter
        docs_file: Chemin du fichier de base de données
        create_backup: Si True, crée une sauvegarde avant modification
    """
    if not documents:
        print("Aucun document à ajouter.")
        return
    
    # Charger les documents existants
    existing_docs = []
    if os.path.exists(docs_file):
        try:
            with open(docs_file, 'r', encoding='utf-8') as f:
                existing_docs = json.load(f)
            print(f"Base de données chargée: {len(existing_docs)} documents existants")
        except Exception as e:
            print(f"Erreur lors du chargement de la base de données: {e}")
            print("Création d'une nouvelle base de données.")
    else:
        print("Base de données inexistante. Création d'une nouvelle base.")
    
    # Créer une sauvegarde si demandé
    if create_backup and os.path.exists(docs_file):
        backup_file = f"{docs_file}.backup"
        try:
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(existing_docs, f, ensure_ascii=False, indent=2)
            print(f"Sauvegarde créée: {backup_file}")
        except Exception as e:
            print(f"Erreur lors de la création de la sauvegarde: {e}")
    
    # Ajouter les nouveaux documents
    existing_docs.extend(documents)
    
    # Sauvegarder la base de données mise à jour
    try:
        with open(docs_file, 'w', encoding='utf-8') as f:
            json.dump(existing_docs, f, ensure_ascii=False, indent=2)
        print(f"✅ {len(documents)} documents ajoutés à la base de données")
        print(f"Total de documents dans la base: {len(existing_docs)}")
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde de la base de données: {e}")

def display_document_preview(documents: List[Dict], max_docs: int = 2, max_chars: int = 200):
    """
    Affiche un aperçu des documents extraits
    
    Args:
        documents: Liste de documents à afficher
        max_docs: Nombre maximum de documents à afficher
        max_chars: Nombre maximum de caractères à afficher par document
    """
    if not documents:
        print("Aucun document à afficher.")
        return
    
    print("\n" + "="*60)
    print(f"APERÇU DES DOCUMENTS EXTRAITS (montrant {min(max_docs, len(documents))} sur {len(documents)})")
    print("="*60)
    
    for i, doc in enumerate(documents[:max_docs]):
        print(f"\nDocument {i+1}:")
        print(f"Titre: {doc['chunk_heading']}")
        print(f"ID: {doc['chunk_link']}")
        if 'metadata' in doc and doc['metadata']:
            print(f"Métadonnées: {', '.join([f'{k}: {v}' for k, v in list(doc['metadata'].items())[:3]])}")
        print("\nDébut du texte:")
        print(f"{doc['text'][:max_chars]}...")
    
    if len(documents) > max_docs:
        print(f"\n... et {len(documents) - max_docs} autres fragments")
    
    print("="*60)

def main():
    # Afficher la configuration actuelle
    print("="*60)
    print(f"INTÉGRATION DE PDF DANS LE SYSTÈME RAG")
    print("="*60)
    print(f"Fichier PDF: {PDF_PATH}")
    print(f"Mode 'visualisation uniquement': {VIEW_ONLY}")
    print(f"Création de sauvegarde: {CREATE_BACKUP}")
    print("="*60)
    
    # Créer les répertoires nécessaires
    setup_directories()
    
    # S'assurer que les ressources NLTK sont disponibles
    ensure_nltk_resources()
    
    # Vérifier que le fichier existe
    pdf_path = os.path.abspath(PDF_PATH)
    if not os.path.exists(pdf_path):
        print(f"❌ Erreur: Le fichier {pdf_path} n'existe pas")
        input("\nAppuyez sur Entrée pour quitter...")
        sys.exit(1)
        
    if not pdf_path.lower().endswith('.pdf'):
        print(f"❌ Erreur: Le fichier {pdf_path} n'est pas un PDF")
        input("\nAppuyez sur Entrée pour quitter...")
        sys.exit(1)
    
    try:
        # Extraire les documents du PDF
        documents = pdf_to_rag_documents(pdf_path)
        
        if not documents:
            print("❌ Aucun contenu extrait du PDF. Vérifiez que le PDF contient du texte sélectionnable.")
            input("\nAppuyez sur Entrée pour quitter...")
            sys.exit(1)
        
        # Afficher un aperçu des documents extraits
        display_document_preview(documents)
        
        # Ajouter les documents à la base de données si ce n'est pas en mode view-only
        if not VIEW_ONLY:
            add_documents_to_database(documents, DOCS_FILE, CREATE_BACKUP)
            print("\n⚠️ N'oubliez pas de régénérer les bases de données vectorielles dans le notebook!")
            print("   Exécutez la cellule 'regenerate_vector_databases()' dans guide.ipynb")
    
    except Exception as e:
        print(f"❌ Erreur lors du traitement du PDF: {str(e)}")
        input("\nAppuyez sur Entrée pour quitter...")
        sys.exit(1)
    
    print("\nTraitement terminé avec succès!")
    input("\nAppuyez sur Entrée pour quitter...")

if __name__ == "__main__":
    main()