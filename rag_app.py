#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Application RAG avec interface utilisateur Streamlit.
Cette application permet de gérer une base de connaissances RAG avec:
- Création et gestion de bases vectorielles
- Ajout de documents PDF
- Interface de chat pour poser des questions
"""

import streamlit as st
import os
import sys
import json
import pickle
import PyPDF2
import nltk
from nltk.tokenize import sent_tokenize
from typing import List, Dict, Optional, Any
import re
import pandas as pd
from datetime import datetime
import logging

# Configuration pour Streamlit
st.set_page_config(
    page_title="RAG Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration des chemins
DATA_DIR = 'data'
DOCS_FILE = os.path.join(DATA_DIR, 'anthropic_docs.json')
SUMMARY_DOCS_FILE = os.path.join(DATA_DIR, 'anthropic_summary_indexed_docs.json')

# Initialisation des répertoires
os.makedirs(DATA_DIR, exist_ok=True)

# Classes simplifiées pour la base vectorielle
class SimpleVectorDB:
    """Version simplifiée d'une base de données vectorielle pour l'application"""
    
    def __init__(self, name: str = "default"):
        self.name = name
        self.documents = []
        self.embeddings = []
        self.metadata = []
        
    def add_documents(self, docs: List[Dict]):
        """Ajoute des documents à la base"""
        self.documents.extend(docs)
        # Simulation d'embeddings (dans un vrai système, vous utiliseriez un modèle d'embedding)
        for doc in docs:
            # Simulation d'un embedding de 768 dimensions
            self.embeddings.append([0.1] * 768)
            self.metadata.append(doc)
    
    def search(self, query: str, k: int = 5) -> List[Dict]:
        """Recherche des documents similaires (version simplifiée)"""
        # Dans un vrai système, vous calculeriez la similarité avec les embeddings
        # Ici, nous faisons une recherche textuelle simple
        results = []
        query_lower = query.lower()
        
        for i, doc in enumerate(self.metadata):
            text = doc.get('text', '').lower()
            title = doc.get('chunk_heading', '').lower()
            
            if query_lower in text or query_lower in title:
                results.append({
                    'document': doc,
                    'score': 0.8,  # Score simulé
                    'index': i
                })
        
        # Retourner les k premiers résultats
        return results[:k]
    
    def get_stats(self) -> Dict:
        """Retourne des statistiques sur la base"""
        return {
            'total_documents': len(self.documents),
            'total_characters': sum(len(doc.get('text', '')) for doc in self.documents),
            'sources': list(set(doc.get('source', 'Unknown') for doc in self.documents))
        }

# Fonctions utilitaires
def ensure_nltk_resources():
    """S'assure que les ressources NLTK sont disponibles"""
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        with st.spinner("Téléchargement des ressources NLTK..."):
            nltk.download('punkt', quiet=True)

def extract_text_from_pdf(pdf_file) -> str:
    """Extrait le texte d'un fichier PDF uploadé"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            try:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
            except Exception as e:
                st.warning(f"Erreur lors de l'extraction d'une page: {str(e)}")
        return text
    except Exception as e:
        st.error(f"Erreur lors de la lecture du PDF: {str(e)}")
        return ""

def chunk_text(text: str, max_chunk_size: int = 2000, overlap: int = 200) -> List[str]:
    """Divise un texte en chunks"""
    if len(text) <= max_chunk_size:
        return [text]
    
    try:
        sentences = sent_tokenize(text)
    except:
        sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = []
    current_size = 0
    
    for sentence in sentences:
        sentence_size = len(sentence)
        
        if sentence_size > max_chunk_size:
            if current_chunk:
                chunks.append(' '.join(current_chunk))
            
            for i in range(0, sentence_size, max_chunk_size - overlap):
                chunk = sentence[i:i + max_chunk_size]
                if len(chunk) >= max_chunk_size / 2:
                    chunks.append(chunk)
            
            current_chunk = []
            current_size = 0
        elif current_size + sentence_size > max_chunk_size:
            chunks.append(' '.join(current_chunk))
            
            overlap_start = max(0, len(current_chunk) - 2)
            current_chunk = current_chunk[overlap_start:] + [sentence]
            current_size = sum(len(s) for s in current_chunk)
        else:
            current_chunk.append(sentence)
            current_size += sentence_size
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def pdf_to_rag_documents(pdf_file, filename: str) -> List[Dict]:
    """Convertit un PDF en documents RAG"""
    text = extract_text_from_pdf(pdf_file)
    
    if not text.strip():
        return []
    
    chunks = chunk_text(text)
    documents = []
    
    for i, chunk in enumerate(chunks):
        documents.append({
            "chunk_heading": f"{filename} - Partie {i+1}/{len(chunks)}",
            "text": chunk,
            "chunk_link": f"{filename.replace('.pdf', '')}-part-{i+1}",
            "source": filename,
            "metadata": {
                "filename": filename,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "upload_date": datetime.now().isoformat()
            }
        })
    
    return documents

def load_documents() -> List[Dict]:
    """Charge les documents existants"""
    if os.path.exists(DOCS_FILE):
        try:
            with open(DOCS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Erreur lors du chargement des documents: {e}")
    return []

def save_documents(documents: List[Dict]):
    """Sauvegarde les documents"""
    try:
        with open(DOCS_FILE, 'w', encoding='utf-8') as f:
            json.dump(documents, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"Erreur lors de la sauvegarde: {e}")
        return False

def simulate_mistral_response(query: str, context_docs: List[Dict]) -> str:
    """Simule une réponse de Mistral AI basée sur le contexte"""
    # Dans un vrai système, vous appelleriez l'API Mistral ici
    if not context_docs:
        return "Je n'ai pas trouvé d'informations pertinentes dans la base de connaissances pour répondre à votre question."
    
    # Construction d'une réponse basée sur les documents trouvés
    context_text = "\n\n".join([doc['text'][:500] + "..." if len(doc['text']) > 500 else doc['text'] 
                                for doc in context_docs])
    
    response = f"""Basé sur les informations disponibles dans la base de connaissances :

{context_text}

Réponse à votre question "{query}":
[Ici, une vraie intégration avec Mistral AI générerait une réponse basée sur le contexte fourni]

Sources: {', '.join(set(doc.get('source', 'Inconnu') for doc in context_docs))}
"""
    
    return response

# Interface Streamlit
def main():
    st.title("🤖 Assistant RAG - Système de Questions-Réponses")
    
    # Initialisation des ressources
    ensure_nltk_resources()
    
    # Initialisation de la session
    if 'vector_db' not in st.session_state:
        st.session_state.vector_db = SimpleVectorDB()
        # Charger les documents existants
        docs = load_documents()
        if docs:
            st.session_state.vector_db.add_documents(docs)
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Sidebar pour la navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choisissez une section:",
        ["🏠 Accueil", "📊 Gestion de la Base", "📄 Ajout de Documents", "💬 Chat & Questions"]
    )
    
    if page == "🏠 Accueil":
        show_home_page()
    elif page == "📊 Gestion de la Base":
        show_database_management()
    elif page == "📄 Ajout de Documents":
        show_document_upload()
    elif page == "💬 Chat & Questions":
        show_chat_interface()

def show_home_page():
    """Page d'accueil"""
    st.header("Bienvenue dans votre Assistant RAG")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 État de la Base de Connaissances")
        stats = st.session_state.vector_db.get_stats()
        
        st.metric("Documents", stats['total_documents'])
        st.metric("Caractères totaux", f"{stats['total_characters']:,}")
        
        if stats['sources']:
            st.write("**Sources disponibles:**")
            for source in stats['sources']:
                st.write(f"• {source}")
    
    with col2:
        st.subheader("🚀 Guide de démarrage")
        st.write("""
        1. **Gestion de la Base** : Consultez et gérez vos documents existants
        2. **Ajout de Documents** : Uploadez de nouveaux fichiers PDF
        3. **Chat & Questions** : Posez des questions sur vos documents
        """)
        
        st.info("💡 **Conseil** : Commencez par ajouter quelques documents pour enrichir votre base de connaissances.")

def show_database_management():
    """Page de gestion de la base de données"""
    st.header("📊 Gestion de la Base de Connaissances")
    
    stats = st.session_state.vector_db.get_stats()
    
    # Statistiques générales
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Documents", stats['total_documents'])
    with col2:
        st.metric("Total Caractères", f"{stats['total_characters']:,}")
    with col3:
        st.metric("Sources Uniques", len(stats['sources']))
    
    # Liste des documents
    st.subheader("📋 Documents dans la base")
    
    if st.session_state.vector_db.documents:
        documents_data = []
        for i, doc in enumerate(st.session_state.vector_db.documents):
            documents_data.append({
                "Index": i,
                "Titre": doc.get('chunk_heading', 'Sans titre'),
                "Source": doc.get('source', 'Inconnue'),
                "Taille": len(doc.get('text', '')),
                "Aperçu": doc.get('text', '')[:100] + "..."
            })
        
        df = pd.DataFrame(documents_data)
        st.dataframe(df, use_container_width=True)
        
        # Options de gestion
        st.subheader("🔧 Actions")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Recharger depuis le fichier"):
                docs = load_documents()
                st.session_state.vector_db = SimpleVectorDB()
                st.session_state.vector_db.add_documents(docs)
                st.success("Base rechargée!")
                st.experimental_rerun()
        
        with col2:
            if st.button("🗑️ Vider la base"):
                if st.checkbox("Confirmer la suppression"):
                    st.session_state.vector_db = SimpleVectorDB()
                    save_documents([])
                    st.success("Base vidée!")
                    st.experimental_rerun()
    else:
        st.info("Aucun document dans la base. Ajoutez des documents via la section 'Ajout de Documents'.")

def show_document_upload():
    """Page d'ajout de documents"""
    st.header("📄 Ajout de Documents PDF")
    
    # Upload de fichiers
    uploaded_files = st.file_uploader(
        "Choisissez des fichiers PDF à ajouter",
        type=['pdf'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.subheader("📥 Fichiers sélectionnés")
        
        for file in uploaded_files:
            st.write(f"• {file.name} ({file.size:,} bytes)")
        
        # Options de traitement
        col1, col2 = st.columns(2)
        with col1:
            chunk_size = st.slider("Taille des fragments", 1000, 4000, 2000, 100)
        with col2:
            overlap = st.slider("Chevauchement", 0, 500, 200, 50)
        
        if st.button("🚀 Traiter et Ajouter les Documents"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            all_new_docs = []
            
            for i, file in enumerate(uploaded_files):
                status_text.text(f"Traitement de {file.name}...")
                progress_bar.progress((i + 1) / len(uploaded_files))
                
                try:
                    # Extraire et traiter le document
                    documents = pdf_to_rag_documents(file, file.name)
                    
                    if documents:
                        all_new_docs.extend(documents)
                        st.success(f"✅ {file.name}: {len(documents)} fragments extraits")
                    else:
                        st.warning(f"⚠️ {file.name}: Aucun texte extrait")
                
                except Exception as e:
                    st.error(f"❌ Erreur avec {file.name}: {str(e)}")
            
            if all_new_docs:
                # Ajouter à la base vectorielle
                st.session_state.vector_db.add_documents(all_new_docs)
                
                # Sauvegarder
                current_docs = load_documents()
                current_docs.extend(all_new_docs)
                
                if save_documents(current_docs):
                    st.success(f"🎉 {len(all_new_docs)} nouveaux documents ajoutés à la base!")
                else:
                    st.error("Erreur lors de la sauvegarde")
            
            progress_bar.empty()
            status_text.empty()

def show_chat_interface():
    """Interface de chat pour poser des questions"""
    st.header("💬 Chat avec votre Base de Connaissances")
    
    # Vérifier qu'il y a des documents
    if not st.session_state.vector_db.documents:
        st.warning("⚠️ Aucun document dans la base. Ajoutez des documents pour commencer à poser des questions.")
        return
    
    # Zone de saisie de question
    user_question = st.text_input(
        "Posez votre question:",
        placeholder="Ex: Qui est Cyril Sauret ? Quelle est son expérience ?"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        ask_button = st.button("🔍 Poser la Question")
    with col2:
        if st.button("🗑️ Effacer l'historique"):
            st.session_state.chat_history = []
            st.experimental_rerun()
    
    # Traitement de la question
    if ask_button and user_question:
        with st.spinner("Recherche dans la base de connaissances..."):
            # Rechercher des documents pertinents
            search_results = st.session_state.vector_db.search(user_question, k=3)
            
            if search_results:
                # Extraire les documents pour le contexte
                context_docs = [result['document'] for result in search_results]
                
                # Générer une réponse (simulée)
                response = simulate_mistral_response(user_question, context_docs)
                
                # Ajouter à l'historique
                st.session_state.chat_history.append({
                    "question": user_question,
                    "response": response,
                    "sources": [doc.get('source', 'Inconnu') for doc in context_docs],
                    "timestamp": datetime.now().isoformat()
                })
            else:
                response = "Je n'ai pas trouvé d'informations pertinentes pour répondre à votre question."
                st.session_state.chat_history.append({
                    "question": user_question,
                    "response": response,
                    "sources": [],
                    "timestamp": datetime.now().isoformat()
                })
    
    # Affichage de l'historique
    if st.session_state.chat_history:
        st.subheader("📜 Historique des conversations")
        
        for i, chat in enumerate(reversed(st.session_state.chat_history)):
            with st.expander(f"Q: {chat['question'][:50]}...", expanded=(i == 0)):
                st.write("**Question:**", chat['question'])
                st.write("**Réponse:**")
                st.write(chat['response'])
                
                if chat['sources']:
                    st.write("**Sources:**", ", ".join(chat['sources']))
                
                st.caption(f"Posée le: {chat['timestamp']}")

if __name__ == "__main__":
    main()
