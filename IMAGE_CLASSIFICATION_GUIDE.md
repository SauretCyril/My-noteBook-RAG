# 🖼️ Guide d'Utilisation - Classification d'Images

## Vue d'ensemble
Cette extension du système RAG permet de classifier et rechercher des images PNG/JPG via l'analyse automatique de leur contenu. Le système utilise plusieurs technologies complémentaires pour une analyse complète.

## 🔧 Technologies Utilisées

### 1. **OCR (Optical Character Recognition)**
- **Outil** : Tesseract OCR
- **Fonction** : Extrait le texte présent dans les images
- **Usage** : Documents scannés, captures d'écran, panneaux, etc.

### 2. **Description Automatique**
- **Modèle** : BLIP (Bootstrapped Language-Image Pre-training)
- **Fonction** : Génère des descriptions textuelles du contenu visuel
- **Usage** : Analyse de scènes, objets, personnes, etc.

### 3. **Classification par Catégories**
- **Méthode** : Analyse hybride (OCR + Description)
- **Catégories** : Automatiques et personnalisables
- **Usage** : Organisation et filtrage des images

### 4. **Recherche Vectorielle**
- **Technologie** : TF-IDF sur le texte composite
- **Fonction** : Recherche par similarité textuelle
- **Usage** : Trouver des images par mots-clés

## 📋 Fonctionnalités Principales

### 🖼️ **Ajout d'Images**
- **Formats supportés** : PNG, JPG, JPEG
- **Traitement automatique** :
  - Extraction de texte (OCR)
  - Génération de description
  - Classification par catégories
  - Création de tags

### 🔍 **Recherche d'Images**
- **Par catégories** : Filtrage par type de contenu
- **Par texte** : Recherche dans descriptions et texte extrait
- **Recherche multimodale** : Combine texte et images dans les résultats

### 🏷️ **Catégories Automatiques**
- **Documents** : Factures, certificats, contrats
- **Personnes** : Portraits, groupes
- **Architecture** : Bâtiments, intérieurs
- **Nature** : Paysages, animaux, plantes
- **Transport** : Véhicules, routes
- **Nourriture** : Repas, cuisine
- **Graphiques** : Schémas, tableaux, diagrammes

## 🚀 Guide d'Installation

### 1. **Prérequis**
```bash
# Installation des dépendances Python
pip install -r requirements_vision.txt

# Installation de Tesseract OCR
# Méthode 1 : Via script automatique
install_tesseract.bat

# Méthode 2 : Via winget
winget install UB-Mannheim.TesseractOCR

# Méthode 3 : Téléchargement manuel
# https://github.com/UB-Mannheim/tesseract/wiki
```

### 2. **Lancement**
```bash
# Lancement de l'application complète
launch_vision_app.bat

# Ou commande directe
streamlit run rag_vision_app.py
```

## 📖 Guide d'Utilisation

### **Étape 1 : Ajouter des Images**
1. Allez dans le menu **"🖼️ Ajouter Images"**
2. Glissez-déposez vos images PNG/JPG
3. Visualisez l'analyse automatique :
   - Texte extrait par OCR
   - Description générée
   - Catégories détectées
4. Personnalisez si nécessaire :
   - Titre personnalisé
   - Tags supplémentaires
   - Description modifiée
5. Cliquez sur **"Ajouter à la base"**

### **Étape 2 : Rechercher des Images**
1. **Recherche par catégories** :
   - Menu **"🔍 Recherche d'Images"**
   - Sélectionnez les catégories souhaitées
   - Visualisez les résultats en grille

2. **Recherche par texte** :
   - Tapez votre requête dans le champ de recherche
   - Les résultats incluent les images pertinentes
   - Voir les scores de similarité

### **Étape 3 : Questions Multimodales**
1. Menu **"❓ Poser Questions"**
2. Posez des questions incluant des images :
   - "Montre-moi les documents financiers"
   - "Quelles images contiennent du texte ?"
   - "Trouve les photos de nature"
3. Les réponses combinent texte et images

## 🎯 Cas d'Usage Pratiques

### **1. Gestion de Documents**
- **Factures** : Classification automatique, extraction de montants
- **Certificats** : Reconnaissance et archivage
- **Contrats** : Indexation par mots-clés

### **2. Archive Photos**
- **Événements** : Classification par contenu
- **Lieux** : Reconnaissance de paysages
- **Personnes** : Détection automatique

### **3. Analyse de Contenu**
- **Graphiques** : Extraction de données
- **Panneaux** : Lecture de texte
- **Diagrammes** : Classification technique

### **4. Recherche Multimodale**
- **Requêtes complexes** : "Trouve les images avec du texte français"
- **Combinaisons** : Documents + images dans les résultats
- **Filtrage** : Par type, date, catégorie

## ⚙️ Configuration Avancée

### **Personnalisation des Catégories**
Modifiez la fonction `classify_image_content()` dans `rag_vision_app.py` :

```python
def classify_image_content(image, text_content="", description=""):
    categories = []
    
    # Ajoutez vos propres règles de classification
    if "votre_mot_clé" in text_content.lower():
        categories.append("Votre_Catégorie")
    
    return categories
```

### **Amélioration de l'OCR**
Pour des langues spécifiques :
```python
# Dans extract_text_from_image()
text = pytesseract.image_to_string(thresh, lang='fra+eng+deu')  # Français + Anglais + Allemand
```

### **Modèles de Vision Alternatifs**
Remplacez BLIP par d'autres modèles :
- **CLIP** : Meilleure compréhension contextuelle
- **GPT-4 Vision** : Descriptions plus détaillées
- **Modèles locaux** : Pour la confidentialité

## 🔧 Dépannage

### **Problèmes Courants**

**1. "Tesseract non détecté"**
```bash
# Solution 1 : Vérifier l'installation
tesseract --version

# Solution 2 : Configurer le chemin
# Ajouter dans le code :
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

**2. "Erreur de modèle BLIP"**
```bash
# Solution : Réinstaller transformers
pip uninstall transformers
pip install transformers>=4.30.0
```

**3. "Mémoire insuffisante"**
```python
# Solution : Redimensionner les images
max_size = (800, 600)
image.thumbnail(max_size)
```

**4. "OCR imprécis"**
```python
# Solution : Préprocessing amélioré
def preprocess_image(image):
    # Convertir en niveaux de gris
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    
    # Améliorer le contraste
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    
    # Débruitage
    denoised = cv2.fastNlMeansDenoising(enhanced)
    
    return denoised
```

## 📊 Performances

### **Limitations**
- **Taille d'image** : Maximum 10MB recommandé
- **Nombre d'images** : Testé jusqu'à 1000 images
- **Vitesse d'analyse** : 2-5 secondes par image
- **Précision OCR** : 85-95% selon la qualité

### **Optimisations**
- **Batch processing** : Traiter plusieurs images simultanément
- **Caching** : Sauvegarder les résultats d'analyse
- **Compression** : Réduire la taille des images stockées

## 🔄 Intégrations Futures

### **APIs Externes**
- **Google Vision API** : OCR commercial
- **Azure Computer Vision** : Analyse avancée
- **AWS Rekognition** : Reconnaissance d'objets

### **Bases de Données Vectorielles**
- **ChromaDB** : Meilleure recherche vectorielle
- **Pinecone** : Solution cloud
- **Weaviate** : Recherche sémantique

### **Modèles Avancés**
- **CLIP** : Embeddings image-texte
- **GPT-4V** : Descriptions contextuelles
- **Modèles spécialisés** : Selon le domaine

## 📞 Support

### **Resources**
- **Documentation Tesseract** : https://tesseract-ocr.github.io/
- **Modèles BLIP** : https://huggingface.co/Salesforce/blip-image-captioning-base
- **OpenCV** : https://opencv.org/

### **Problèmes Spécifiques**
1. **Performance** : Réduire la taille des images
2. **Précision** : Améliorer le préprocessing
3. **Mémoire** : Traiter par lots plus petits
4. **Compatibilité** : Vérifier les versions des dépendances

---

**Version** : 1.0.0  
**Dernière mise à jour** : Juillet 2025  
**Compatibilité** : Python 3.8+, Windows/Linux/Mac
