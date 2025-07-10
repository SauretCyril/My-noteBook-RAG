# 🤖 RAG Knowledge Base Manager - Version Professionnelle

Système RAG (Retrieval-Augmented Generation) professionnel pour la gestion documentaire avec interface Streamlit moderne et architecture modulaire.

## 🚀 Démarrage Rapide

### Lancement de l'Application v2.0 (Recommandé)
```bash
# Nouvelle version avec architecture professionnelle
launch_rag_v2_app.bat
# Ou directement : streamlit run app.py --server.port 8503
```

### Applications Héritées (Compatibilité)
```bash
# Application principale originale
launch_rag_app.bat

# Traitement par lots avec vision
launch_batch_app.bat

# Application vision spécialisée  
launch_vision_app.bat
```

## 🏗️ Architecture v2.0

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
