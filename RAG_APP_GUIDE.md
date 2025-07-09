# 🤖 RAG Knowledge Base Manager

## Vue d'ensemble
Cette application Streamlit offre une interface complète pour gérer votre base de connaissances RAG (Retrieval-Augmented Generation). Elle permet d'ajouter des documents PDF, de les vectoriser et de les interroger via une interface de chat.

## 🚀 Démarrage Rapide

### Installation des dépendances
```bash
pip install -r requirements.txt
```

### Lancement de l'application
```bash
# Méthode 1 : Script batch (Windows)
launch_rag_app.bat

# Méthode 2 : Commande directe
streamlit run rag_interface_app.py
```

L'application sera disponible sur : `http://localhost:8501`

## 📋 Fonctionnalités

### 1. 🏠 Tableau de Bord
- **Statistiques** : Nombre de documents, conversations
- **État des fichiers** : Vérification de la présence des fichiers de base
- **Démarrage rapide** : Instructions pour commencer

### 2. 🗃️ Gestion de la Base
- **Créer une nouvelle base** : Initialise une base vectorielle vide
- **Sauvegarder la base** : Sauvegarde l'état actuel
- **Recharger la base** : Charge une base existante
- **Visualisation** : Affiche les documents stockés

### 3. 📄 Ajouter Documents
- **Upload PDF** : Glissez-déposez vos fichiers PDF
- **Extraction automatique** : Extrait le texte des PDF
- **Segmentation** : Divise le texte en chunks optimaux
- **Prévisualisation** : Vérifiez le contenu avant ajout

### 4. ❓ Poser Questions
- **Interface de chat** : Posez des questions en langage naturel
- **Recherche vectorielle** : Trouve les documents pertinents
- **Réponses contextuelles** : Génère des réponses basées sur vos documents
- **Historique** : Garde trace des conversations
- **Sources** : Affiche les documents utilisés pour chaque réponse

## 🗂️ Structure des Fichiers

```
My-noteBook-RAG/
├── rag_interface_app.py      # Application principale
├── requirements.txt          # Dépendances Python
├── launch_rag_app.bat       # Script de lancement
├── data/
│   ├── anthropic_docs.json       # Base de connaissances JSON
│   ├── anthropic_docs.json.backup # Sauvegarde automatique
│   └── docs/
│       └── vector_db.pkl          # Base vectorielle
```

## 🔧 Configuration

### Paramètres par défaut
- **Taille des segments** : 500 caractères
- **Nombre de résultats** : 5 documents
- **Méthode de vectorisation** : TF-IDF
- **Similarité minimale** : 0.1

### Personnalisation
Modifiez les constantes dans `rag_interface_app.py` :
```python
DATA_DIR = "data"
KNOWLEDGE_BASE_FILE = "anthropic_docs.json"
VECTOR_DB_FILE = "vector_db.pkl"
```

## 🛠️ Utilisation Détaillée

### Ajouter un Premier Document
1. Allez dans **"Ajouter Documents"**
2. Uploadez un fichier PDF
3. Ajustez la taille des segments si nécessaire
4. Cliquez sur **"Ajouter à la base"**

### Poser une Question
1. Allez dans **"Poser Questions"**
2. Tapez votre question dans le champ de texte
3. Cliquez sur **"Rechercher"**
4. Consultez la réponse et les sources utilisées

### Gérer la Base
1. Allez dans **"Gestion de la Base"**
2. Utilisez les boutons pour :
   - Créer une nouvelle base (efface tout)
   - Sauvegarder l'état actuel
   - Recharger une base existante

## 🧩 Intégrations Possibles

### Modèles de Langage
Remplacez la fonction `generate_response()` pour intégrer :
- **Mistral AI** : API ou modèle local
- **OpenAI** : GPT-3.5/4
- **Anthropic** : Claude
- **Ollama** : Modèles locaux

### Améliorations Vectorielles
- **Embeddings** : Remplacer TF-IDF par des embeddings (OpenAI, Sentence-BERT)
- **Base vectorielle** : Utiliser ChromaDB, Pinecone, ou Weaviate
- **Recherche hybride** : Combiner recherche vectorielle et textuelle

## 🐛 Dépannage

### Erreurs Courantes

**"ModuleNotFoundError"**
```bash
pip install -r requirements.txt
```

**"NLTK data not found"**
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```

**"Permission denied"**
- Vérifiez les permissions d'écriture dans le dossier `data/`
- Exécutez en tant qu'administrateur si nécessaire

**"PDF extraction failed"**
- Vérifiez que le PDF n'est pas protégé par mot de passe
- Certains PDF scannés peuvent nécessiter un OCR

### Logs et Debugging
Les erreurs sont affichées directement dans l'interface Streamlit. Pour plus de détails, consultez la console où l'application est lancée.

## 📊 Performances

### Optimisations
- **Taille des segments** : 300-800 caractères optimal
- **Nombre de documents** : Testée jusqu'à 1000 documents
- **Mémoire** : ~100MB pour 500 documents moyens

### Limitations
- **Formats supportés** : PDF uniquement
- **Taille max par fichier** : 50MB recommandé
- **Recherche** : Basée sur TF-IDF (peut être améliorée)

## 🔄 Migrations

### Depuis l'ancienne version
Si vous avez des données existantes dans `anthropic_docs.json`, elles seront automatiquement chargées au démarrage.

### Sauvegarde manuelle
```bash
# Sauvegarde des données
cp data/anthropic_docs.json backup_$(date +%Y%m%d).json
cp data/docs/vector_db.pkl backup_vector_$(date +%Y%m%d).pkl
```

## 🤝 Contribution

### Structure du Code
- **Classes principales** : `VectorDatabase`
- **Fonctions utilitaires** : `extract_text_from_pdf`, `segment_text`
- **Interface** : Fonctions `show_*_page()`

### Ajout de Fonctionnalités
1. Créez une nouvelle fonction `show_*_page()`
2. Ajoutez-la dans le menu principal
3. Testez avec des documents variés

## 📞 Support

Pour toute question ou problème :
1. Vérifiez cette documentation
2. Consultez les logs d'erreur
3. Testez avec un document simple
4. Vérifiez les permissions de fichiers

---

**Version** : 1.0.0  
**Dernière mise à jour** : Décembre 2024  
**Compatibilité** : Python 3.8+, Windows/Linux/Mac
