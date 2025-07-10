# 📁 Guide du Traitement par Lots - RAG Batch Processing

## Vue d'ensemble
Cette extension du système RAG permet de traiter des répertoires entiers de documents en utilisant des fichiers `._annonce_.data` pour contextualiser automatiquement les documents. Le système inclut maintenant des fonctionnalités de **vision avancée** pour l'analyse intelligente des images.

## 🎯 Fonctionnalités Principales

### 📁 **Traitement Récursif**
- Parcourt automatiquement tous les sous-dossiers
- Traite plusieurs types de fichiers simultanément
- Gestion intelligente des erreurs et des fichiers corrompus

### 📋 **Fichiers d'Annonce** - Contextualisation Automatique

**Qu'est-ce qu'un fichier d'annonce ?**
Les fichiers d'annonce sont des fichiers spéciaux nommés `._annonce_.data` que **vous devez créer manuellement** dans vos dossiers. Ils permettent de **contextualiser automatiquement** tous les documents d'un dossier. Le système RAG ne crée pas ces fichiers - il les lit et applique leurs métadonnées aux documents.

**⚠️ Important : Création Manuelle Requise**
- **Vous créez** : Les fichiers `._annonce_.data` doivent être créés par vous
- **Le système lit** : Le RAG lit ces fichiers et applique les métadonnées
- **Application automatique** : Une fois créés, les métadonnées sont appliquées automatiquement

**Principe de fonctionnement :**
1. **Vous créez** un fichier `._annonce_.data` dans un dossier avec vos métadonnées
2. Le système cherche ce fichier dans chaque dossier traité
3. Il lit les métadonnées que vous avez définies
4. Il applique ces métadonnées à tous les fichiers du dossier
5. Les sous-dossiers peuvent avoir leurs propres fichiers d'annonce (héritage hiérarchique)

**Formats supportés :**
- **JSON** : Format structuré complet
- **Texte** : Format clé:valeur simple
- **Héritage** : Métadonnées propagées aux sous-dossiers

**Exemple concret :**
```
Mon_Projet/
├── ._annonce_.data → {"project": "Projet X", "category": "Documentation"}
├── manuel.pdf        # Sera indexé avec : project="Projet X", category="Documentation"
├── guide.txt         # Sera indexé avec : project="Projet X", category="Documentation"
└── images/
    ├── ._annonce_.data → {"type": "image", "usage": "illustration"}
    └── schema.png    # Héritera de : Projet X + Documentation + image + illustration
```

### 🔄 **Traitement par Lots**
- Barre de progression en temps réel
- Traitement optimisé pour de gros volumes
- Rapport détaillé des succès/erreurs

### 🔍 **Vision Avancée (Nouveau)**
- **Génération de descriptions** automatiques d'images avec BLIP
- **Classification intelligente** par catégories
- **OCR avancé** pour extraction de texte
- **Indexation multimodale** (texte + images)
- **Galerie d'images** avec recherche et filtres

### 🔍 **Recherche Avancée**
- Filtrage par catégories, projets, auteurs
- Recherche combinée texte + métadonnées
- Tri par pertinence et similarité
- Recherche dans les images par description et contenu

## 🚀 Installation et Démarrage

### 1. **Prérequis**
```bash
# Installer les dépendances
pip install -r requirements.txt

# Installer Tesseract pour OCR (Windows)
install_tesseract.bat

# Initialiser NLTK (IMPORTANT - Nouvelles ressources requises)
fix_nltk.bat
# OU
python fix_nltk.py
# OU manuellement :
python -c "import nltk; import ssl; ssl._create_default_https_context = ssl._create_unverified_context; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('omw-1.4')"
```

**⚠️ Note importante :** La nouvelle version de NLTK nécessite `punkt_tab` en plus de `punkt`. Le script `fix_nltk.bat` installe automatiquement toutes les ressources nécessaires.

### 2. **Lancement**
```bash
# Méthode 1 : Script batch
launch_batch_app.bat

# Méthode 2 : Commande directe
streamlit run rag_batch_app.py --server.port 8502
```

### 3. **Accès**
- URL : `http://localhost:8502`
- Interface web intuitive avec menu de navigation

## 📋 Utilisation du Système

### **Étape 1 : Préparer vos Dossiers et Créer les Fichiers d'Annonce**

**⚠️ Étape Cruciale : Création Manuelle des Fichiers `._annonce_.data`**

Avant de lancer le traitement par lots, vous devez **créer manuellement** les fichiers `._annonce_.data` dans vos dossiers. Le système RAG ne crée pas ces fichiers automatiquement.

#### **Comment Créer un Fichier d'Annonce :**

1. **Naviguer vers votre dossier** de documents
2. **Créer un nouveau fichier** nommé exactement `._annonce_.data`
3. **Choisir le format** : JSON (recommandé) ou texte simple
4. **Saisir vos métadonnées** selon vos besoins

#### **Exemple de Création :**

**Option 1 : Format JSON (Recommandé)**
```json
{
    "title": "Projet RAG - Documentation",
    "category": "Documentation",
    "project": "Système RAG",
    "author": "Équipe Dev",
    "description": "Documentation complète du système RAG",
    "tags": "documentation,technique,rag,ia",
    "date": "2024-07-09",
    "type": "documentation",
    "priority": "high",
    "status": "active"
}
```

**Option 2 : Format Texte Simple**
```
title: Projet RAG - Documentation
category: Documentation
project: Système RAG
author: Équipe Dev
description: Documentation complète du système RAG
tags: documentation,technique,rag,ia
date: 2024-07-09
type: documentation
priority: high
status: active
```

#### **Workflow Complet :**

1. **Organiser vos documents** par dossiers thématiques
2. **Créer un fichier `._annonce_.data`** dans chaque dossier
3. **Définir les métadonnées** appropriées pour chaque contexte
4. **Lancer le traitement par lots** - le système appliquera automatiquement les métadonnées

### **Étape 2 : Traitement par Lots**

1. **Accéder au Menu** : `📁 Traitement par Lots`
2. **Sélectionner le Répertoire** : Indiquer le chemin du dossier racine
3. **Configurer les Options** :
   - Types de fichiers à traiter (PDF, TXT, images)
   - Taille maximale des fichiers
   - Options de segmentation
4. **Scanner** : Prévisualiser les fichiers qui seront traités
5. **Lancer le Traitement** : Traitement automatique avec barre de progression

### **Étape 3 : Recherche et Utilisation**

1. **Recherche Simple** : Menu `❓ Poser Questions`
2. **Recherche Avancée** : Menu `🔍 Recherche Avancée`
   - Filtrer par catégories, projets, auteurs
   - Régler la similarité minimale
   - Limiter le nombre de résultats

## 🗂️ Formats de Fichiers Supportés

### **Documents Texte**
- **PDF** : Extraction automatique du texte
- **TXT** : Lecture directe
- **OCR** : Extraction de texte depuis images

### **Images** (avec OCR)
- **PNG** : Extraction de texte via Tesseract
- **JPG/JPEG** : Reconnaissance de caractères
- **Préprocessing** : Amélioration automatique de la qualité

### **Métadonnées**
- **JSON** : Format structuré complet
- **Texte** : Format clé:valeur simple
- **Héritage** : Métadonnées propagées aux sous-dossiers

## 📊 Exemples d'Usage

### **Cas 1 : Documentation Projet**
```
Structure :
Projet_X/
├── ._annonce_.data → {"project": "Projet X", "category": "Documentation"}
├── cahier_des_charges.pdf
├── specifications_techniques.pdf
└── guide_utilisateur.pdf

Résultat :
- Tous les PDF classés automatiquement dans "Projet X"
- Catégorie "Documentation" assignée
- Recherche possible par projet ou contenu
```

### **Cas 2 : Archive Personnelle**
```
Structure :
Documents_Perso/
├── CV/
│   ├── ._annonce_.data → {"category": "CV", "type": "professionnel"}
│   └── cv_2024.pdf
├── Formations/
│   ├── ._annonce_.data → {"category": "Formation", "project": "Apprentissage"}
│   └── certificat_ia.pdf
└── Projets/
    ├── ._annonce_.data → {"category": "Projet", "status": "active"}
    └── projet_personnel.txt

Résultat :
- Classification automatique par catégorie
- Possibilité de rechercher "mes CV" ou "mes formations"
- Filtrage par statut (actif/inactif)
```

### **Cas 3 : Base de Connaissances Entreprise**
```
Structure :
Entreprise_Docs/
├── ._annonce_.data → {"author": "Entreprise", "confidentiality": "internal"}
├── RH/
│   ├── ._annonce_.data → {"category": "RH", "department": "Ressources Humaines"}
│   └── politique_rh.pdf
├── Technique/
│   ├── ._annonce_.data → {"category": "Technique", "department": "IT"}
│   └── architecture_system.pdf
└── Marketing/
    ├── ._annonce_.data → {"category": "Marketing", "department": "Communication"}
    └── strategie_2024.pdf

Résultat :
- Segmentation par département
- Recherche transversale ou spécialisée
- Gestion des niveaux de confidentialité
```

### **Cas 4 : Traitement d'Images avec Vision Avancée (Nouveau)**
```
Structure :
Mes_Images/
├── ._annonce_.data → {"project": "Documentation Visuelle", "author": "Design Team"}
├── screenshots/
│   ├── ._annonce_.data → {"category": "Interface", "type": "screenshot"}
│   ├── dashboard.png      # OCR + Description: "A web dashboard showing statistics"
│   └── login_screen.jpg   # OCR + Description: "Login form with email field"
├── documents_scannes/
│   ├── ._annonce_.data → {"category": "Document", "type": "scan"}
│   ├── facture_001.png    # OCR: "Facture #001 - Montant: 1200€"
│   └── contrat.jpg        # OCR: "Contrat de service - Signature requise"
└── photos/
    ├── ._annonce_.data → {"category": "Photo", "type": "événement"}
    └── reunion_equipe.jpg  # Description: "Group of people in meeting room"

Résultat avec Vision Avancée :
- Screenshots classifiés automatiquement en "Interface/Écran"
- Documents scannés avec extraction OCR complète
- Photos avec descriptions automatiques
- Recherche possible par : "facture", "dashboard", "réunion", etc.
- Galerie d'images avec filtres par catégorie et projet
```

### **Cas 5 : Base de Connaissances Multimodale**
```
Structure :
Knowledge_Base/
├── ._annonce_.data → {"organization": "TechCorp", "access_level": "internal"}
├── documentation/
│   ├── ._annonce_.data → {"category": "Documentation", "language": "fr"}
│   ├── manuel_utilisateur.pdf
│   └── guide_installation.txt
├── presentations/
│   ├── ._annonce_.data → {"category": "Présentation", "format": "slide"}
│   └── pitch_commercial.pdf
└── supports_visuels/
    ├── ._annonce_.data → {"category": "Visuel", "usage": "formation"}
    ├── diagramme_architecture.png  # Description: "System architecture diagram"
    ├── flowchart_process.jpg       # Description: "Business process flowchart"
    └── mockup_interface.png        # Description: "User interface mockup design"

Résultat :
- Recherche unifiée texte + images
- "Montre-moi l'architecture" → trouve le diagramme + documentation
- "Formation commerciale" → trouve présentations + supports visuels
- Classification automatique par type de contenu
```

## ⚙️ Configuration Avancée

### **Personnalisation des Métadonnées**
```python
# Dans create_document_metadata()
metadata = {
    'title': annonce_data.get('title', file_name),
    'category': annonce_data.get('category', 'Non classé'),
    'project': annonce_data.get('project', ''),
    'department': annonce_data.get('department', ''),  # Nouveau champ
    'confidentiality': annonce_data.get('confidentiality', 'public'),  # Nouveau champ
    'custom_field': annonce_data.get('custom_field', ''),  # Champ personnalisé
    # ... autres champs
}
```

### **Filtres de Recherche Personnalisés**
```python
# Dans show_advanced_search()
# Ajouter de nouveaux filtres
departments = vector_db.get_departments()  # Fonction à créer
selected_departments = st.multiselect("Départements:", departments)

confidentiality_levels = ['public', 'internal', 'confidential']
selected_confidentiality = st.multiselect("Confidentialité:", confidentiality_levels)
```

### **Optimisation des Performances**
```python
# Traitement par chunks pour de gros volumes
BATCH_SIZE = 100  # Traiter par groupes de 100 fichiers
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB max par fichier
SEGMENT_SIZE = 500  # Taille des segments de texte
```

## 🔧 Dépannage

### **Problèmes Courants**

**1. "Répertoire non trouvé"**
```bash
# Vérifier le chemin
ls "C:\Mon\Chemin\Dossier"
# Utiliser des chemins absolus
```

**2. "Fichier d'annonce non lu"**
```bash
# Vérifier l'encodage (UTF-8 recommandé)
# Valider la syntaxe JSON
python -m json.tool example_._annonce_.data
```

**3. "Erreur d'extraction PDF"**
```bash
# PDF potentiellement corrompu
# Essayer avec un autre lecteur PDF
# Vérifier les permissions de lecture
```

**4. "Mémoire insuffisante"**
```python
# Réduire la taille des lots
BATCH_SIZE = 50
# Augmenter la segmentation
SEGMENT_SIZE = 300
```

### **Optimisations**

**1. Traitement Plus Rapide**
```python
# Parallélisation simple
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

def process_file_parallel(file_path):
    # Traitement d'un fichier
    return extract_text_from_file(file_path)

# Utilisation
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(process_file_parallel, file_paths))
```

**2. Gestion Mémoire**
```python
# Traitement streaming pour gros fichiers
def process_large_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        while True:
            chunk = f.read(8192)  # Lire par chunks
            if not chunk:
                break
            # Traiter le chunk
            process_chunk(chunk)
```

**3. Cache des Résultats**
```python
# Éviter de retraiter les mêmes fichiers
import hashlib

def get_file_hash(file_path):
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

# Vérifier si déjà traité
if file_hash not in processed_files:
    # Traiter le fichier
    pass
```

## 📈 Monitoring et Métriques

### **Suivi des Performances**
```python
# Ajouter des métriques
processing_stats = {
    'total_files': len(files_list),
    'processing_time': time.time() - start_time,
    'files_per_second': len(files_list) / processing_time,
    'total_size_mb': sum(os.path.getsize(f) for f, _ in files_list) / 1024 / 1024,
    'average_file_size': total_size_mb / len(files_list)
}
```

### **Logs Détaillés**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('batch_processing.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info(f"Traitement démarré pour {len(files_list)} fichiers")
```

## 🔄 Intégrations Futures

### **Bases de Données Externes**
- **PostgreSQL** : Stockage des métadonnées
- **MongoDB** : Documents NoSQL
- **Elasticsearch** : Recherche textuelle avancée

### **APIs Externes**
- **Google Drive** : Traitement cloud
- **SharePoint** : Intégration entreprise
- **Dropbox** : Synchronisation automatique

### **Intelligence Artificielle**
- **Classification automatique** : Catégorisation par contenu
- **Extraction d'entités** : Reconnaissance de noms, dates, lieux
- **Résumé automatique** : Génération de descriptions

## 📞 Support et Ressources

### **Documentation**
- **Guide utilisateur** : Ce fichier
- **API Reference** : Code source commenté
- **Exemples** : Dossier `examples/`

### **Communauté**
- **Issues** : Rapporter des bugs
- **Discussions** : Partager des améliorations
- **Contributions** : Pull requests bienvenues

### **Performance**
- **Benchmarks** : Tests de performance
- **Optimisations** : Conseils d'amélioration
- **Monitoring** : Outils de suivi

---

**Version** : 1.0.0  
**Dernière mise à jour** : Juillet 2025  
**Compatibilité** : Python 3.8+, Windows/Linux/Mac

Cette extension transforme votre système RAG en une véritable plateforme de gestion documentaire intelligente, capable de traiter des volumes importants de documents avec contextualisation automatique.

### **Questions Fréquentes sur les Fichiers d'Annonce**

**Q: Le système RAG crée-t-il automatiquement les fichiers `._annonce_.data` ?**
**R:** Non, vous devez les créer manuellement. Le système les lit mais ne les crée jamais.

**Q: Que se passe-t-il si je n'ai pas de fichier `._annonce_.data` ?**
**R:** Le traitement fonctionne quand même, mais les documents n'auront que des métadonnées basiques (nom du fichier, taille, etc.).

**Q: Puis-je modifier un fichier `._annonce_.data` après traitement ?**
**R:** Oui, mais vous devrez relancer le traitement pour que les modifications soient prises en compte.

**Q: Les fichiers `._annonce_.data` sont-ils traités comme des documents ?**
**R:** Non, ils sont ignorés lors du traitement et servent uniquement à fournir des métadonnées.

**Q: Peut-on avoir des fichiers `._annonce_.data` vides ?**
**R:** Techniquement oui, mais ils n'apporteront aucune valeur ajoutée.

**Q: Le nom `._annonce_.data` est-il obligatoire ?**
**R:** Oui, exactement ce nom. Le système cherche spécifiquement ce nom de fichier.

**Q: Le système va-t-il écraser mes fichiers `*_annonce_.pdf` existants ?**
**R:** NON ! Le système ne modifie JAMAIS vos fichiers existants. Il les lit uniquement pour extraire le contenu.

**Q: Mes documents importants sont-ils en sécurité ?**
**R:** Absolument. Le système fonctionne en lecture seule et ne modifie aucun fichier existant.

**Q: Que se passe-t-il avec mes fichiers `*_annonce_.pdf` ?**
**R:** Ils sont traités comme des documents normaux : contenu extrait, indexé, mais fichier original préservé.

## 🛡️ Protection des Fichiers Existants

### **⚠️ IMPORTANT : Fichiers à Ne Jamais Écraser**

Le système RAG **ne modifie JAMAIS** vos fichiers existants. Il fonctionne en **lecture seule** :

**Fichiers Protégés :**
- **`*_annonce_.pdf`** : Vos documents PDF d'annonce existants
- **Tous vos PDF, TXT, images** : Vos documents de travail
- **Fichiers `._annonce_.data`** : Vos fichiers de métadonnées (s'ils existent)

**Ce que fait le système :**
- **LIT** vos fichiers pour extraire le contenu
- **COPIE** les images dans un dossier de stockage (optionnel)
- **INDEXE** le contenu dans la base vectorielle
- **Ne modifie JAMAIS** vos fichiers originaux

### **Exemple avec Fichiers d'Annonce :**

```
Mon_Dossier/
├── important_annonce_.pdf      # ← VOS DOCUMENTS PDF (préservés)
├── projet_annonce_.pdf         # ← VOS DOCUMENTS PDF (préservés)
├── presentation.pdf            # ← VOS DOCUMENTS (préservés)
├── ._annonce_.data                 # ← MÉTADONNÉES (optionnel, créé par vous)
└── data/
    └── images/                 # ← STOCKAGE SYSTÈME (copies d'images)
```

**Résultat du traitement :**
- **`important_annonce_.pdf`** → Contenu extrait et indexé (fichier intact)
- **`projet_annonce_.pdf`** → Contenu extrait et indexé (fichier intact)
- **`presentation.pdf`** → Contenu extrait et indexé (fichier intact)
- **`._annonce_.data`** → Métadonnées lues et appliquées (fichier intact)

### **Garanties de Sécurité :**

1. **Aucune modification** : Le système n'écrit jamais dans vos fichiers
2. **Lecture seule** : Tous les accès sont en mode lecture
3. **Stockage séparé** : Les données extraites vont dans la base vectorielle
4. **Préservation totale** : Vos fichiers restent exactement comme avant
