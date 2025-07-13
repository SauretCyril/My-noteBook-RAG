# 🤖 RAG Knowledge Assistant

**Assistant intelligent basé sur RAG (Retrieval Augmented Generation) pour analyser vos documents et répondre à vos questions.**

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Framework-Streamlit-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Fonctionnalités

- 📄 **Analyse de documents** : PDF, DOC, TXT, JSON
- 🔍 **Recherche intelligente** : Recherche vectorielle avec TF-IDF
- 💬 **Chat interactif** : Interface conversationnelle avec Mistral AI
- 📊 **Extraction de listes** : Génération automatique de listes (entreprises, compétences, projets)
- 🎯 **Détection de candidatures** : Analyse spécialisée pour les recherches d'emploi
- 🧹 **Traitement par lots** : Import massif de documents

## 🚀 Démarrage rapide

### Lancement simple
```bash
# Sur Windows (Recommandé)
start.bat

# Alternative directe
python app.py
```

### Accès à l'application
Ouvrez votre navigateur : **http://localhost:8501**

```
rag_app/                          # 📦 Package principal
├── config/                       # ⚙️ Configuration
│   └── settings.py              # Paramètres globaux
├── core/                        # 🏛️ Logique métier
│   └── vector_database.py       # Base vectorielle optimisée
├── services/                    # 🔧 Services applicatifs
├── ui/                          # 🎨 Interface utilisateur
│   ├── components/              # Composants réutilisables
│   │   └── sidebar.py
│   └── pages/                   # Pages Streamlit modulaires
│       ├── home.py              # ✅ Tableau de bord
│       └── database_management.py  # ✅ Gestion base
├── utils/                       # 🛠️ Utilitaires
└── main.py                     # Point d'entrée principal
```

## 📋 Fonctionnalités

### ✅ Disponibles (v2.0)
- **🏠 Tableau de bord** : Statistiques et graphiques
- **🗃️ Gestion de base** : Administration complète
- **📊 Visualisations** : Graphiques de répartition
- **⚙️ Configuration** : Paramètres centralisés
- **💾 Compatibilité** : Données existantes préservées

### 🚧 En Migration
- **📁 Traitement par lots** : Migration depuis l'ancienne architecture
- **🔍 Recherche avancée** : Refactorisation en cours
- **🖼️ Galerie d'images** : Interface en cours de migration

### 🎯 Applications Héritées (Pleinement Fonctionnelles)
- **Traitement par lots** avec métadonnées `._rag_.data`
- **Vision avancée** (BLIP, OCR, classification)
- **Interface de chat** pour questions/réponses

## 📦 Installation

```bash
# Dépendances de base
pip install -r requirements/base.txt

# Avec fonctionnalités vision
pip install -r requirements/vision.txt

# Environnement de développement
pip install -r requirements/dev.txt
```

## 📚 Documentation

- `guide.ipynb` : Guide de restructuration et planification
- `BATCH_PROCESSING_GUIDE.md` : Guide du traitement par lots
- `RAG_APP_GUIDE.md` : Documentation application principale
- `IMAGE_CLASSIFICATION_GUIDE.md` : Guide de classification d'images

## 🔧 Développement

### Structure de Développement
```bash
# Tests unitaires
pytest tests/

# Formatage du code
black rag_app/
isort rag_app/

# Linting
flake8 rag_app/
```

### Migration Progressive
1. **Phase 1** : Architecture de base ✅
2. **Phase 2** : Migration des services
3. **Phase 3** : Tests et optimisations

## 📊 Compatibilité

- **Données** : Compatible avec toutes les bases existantes
- **Scripts** : Anciens scripts de lancement conservés
- **APIs** : Interfaces préservées pour la migration

## 🤝 Contribution

1. Utiliser la nouvelle architecture `rag_app/`
2. Suivre les conventions de nommage
3. Ajouter des tests pour nouveaux modules
4. Mettre à jour la documentation
