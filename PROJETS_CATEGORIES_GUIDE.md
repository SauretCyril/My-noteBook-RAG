# 📂 Guide des Projets et Catégories RAG

## 🎯 Vue d'ensemble

Le système RAG organise automatiquement vos documents en **projets** et **catégories** pour une navigation et recherche optimales.

### 📊 Principe Fondamental

**🔑 Chaque fichier `.data.json` = Un projet complet**

```json
{
    "dossier": "P001",
    "description": "Application Mobile E-commerce",
    "categorie": "Développement",
    "contact": "Jean Dupont",
    "entreprise": "TechCorp",
    "Date": "2025-01-15",
    // ... autres champs
}
```

↓ **Conversion automatique** ↓

```
🎯 Projet: "P001_Application Mobile E-commerce"
🏷️ Catégorie: "Développement"
👤 Auteur: "Jean Dupont"
📅 Date: "2025-01-15"
```

## 🔄 Mapping Automatique des Champs

### 📋 Champs .data.json → Métadonnées RAG

| Champ .data.json | Métadonnée RAG | Description |
|------------------|----------------|-------------|
| `dossier` + `description` | **project** | Nom unique du projet |
| `categorie` | **category** | Catégorie de classification |
| `contact` / `entreprise` | **author** | Responsable du projet |
| `Date` / `Date_rep` | **date** | Date du projet |
| Multiples champs | **description** | Description enrichie |
| Booléens et mots-clés | **tags** | Tags pour la recherche |
| `etat` | **status** / **priority** | État et priorité |

### 🏗️ Construction du Nom de Projet

```python
# Format: {dossier}_{description}
"P001" + "_" + "Application Mobile E-commerce"
= "P001_Application Mobile E-commerce"
```

### 📝 Enrichissement de la Description

Fusion automatique de plusieurs champs :
- Description principale
- Commentaires
- Actions à mener
- Informations de contact
- URLs et liens

## 🏷️ Système de Catégorisation

### 1. 📊 Catégories des fichiers .data.json

Basées sur le champ `categorie` :
- **Développement** - Projets techniques
- **Marketing** - Campagnes et communication
- **Formation** - Documents éducatifs
- **Juridique** - Contrats et procédures
- **Finance** - Budgets et factures

### 2. 🤖 Catégorisation Automatique RAG

Pour les documents sans `.data.json`, analyse du contenu :

#### 📄 Documents PDF/TXT
- **Document financier** - Mots-clés : facture, prix, montant
- **Document éducatif** - Mots-clés : formation, certificat, diplôme
- **Document juridique** - Mots-clés : contrat, accord, signature
- **Communication** - Mots-clés : email, message, correspondance

#### 🖼️ Images (avec OCR)
- **Portrait/Personne** - Détection de visages
- **Architecture/Bâtiment** - Structures et bâtiments
- **Nature/Paysage** - Environnements naturels
- **Transport/Véhicule** - Moyens de transport
- **Document/Texte** - Images contenant du texte
- **Graphique/Schéma** - Diagrammes et graphiques

## 📊 Interface de Visualisation

### 🏠 Page "📂 Projets & Catégories"

#### 📊 Vue d'ensemble
- 📄 **Documents totaux** - Nombre total dans la base
- 🎯 **Projets identifiés** - Projets avec noms spécifiques
- 🏷️ **Catégories actives** - Catégories définies
- 📊 **Projets .data.json** - Issues de fichiers .data.json

#### 📂 Onglet Projets
```
📂 P001_Application Mobile E-commerce (45 documents)
├── 📄 Documents: 45
├── 📊 .data.json: 1
├── 🏷️ Catégories: Développement, Tests, Documentation
├── 👤 Auteurs: Jean Dupont, Marie Martin
├── 📁 Sources: Actions-11-Projects, docs
└── 📅 Dates: 2025-01-15, 2025-01-20
```

#### 🏷️ Onglet Catégories
```
🏷️ Développement
├── 📄 Documents: 120
├── 📂 Projets: 8
└── 📎 Types: .pdf, .txt, .png

🏷️ Marketing
├── 📄 Documents: 45
├── 📂 Projets: 3
└── 📎 Types: .pdf, .jpg
```

#### 📊 Onglet Analyse
- 💡 **Recommandations** d'amélioration
- 📊 **Matrice Projets × Catégories**
- 🔗 **Top Associations** projet-catégorie

## 🔍 Recherche par Projet/Catégorie

### 💬 Dans le Chat RAG

```
🔍 "Montre-moi les projets de développement"
🔍 "Quels sont les documents du projet P001?"
🔍 "Liste les catégories marketing disponibles"
🔍 "Documents de Jean Dupont en 2025"
```

### 🔍 Dans la Recherche Avancée

Filtres disponibles :
- **👤 Par auteur** - `contact:"Jean Dupont"`
- **📂 Par projet** - `project:"P001_Application"`
- **🏷️ Par catégorie** - `category:"Développement"`
- **📅 Par date** - `date:"2025-01-15"`
- **🏷️ Par tag** - `tags:"urgent"`

## 📁 Traitement par Lots Enrichi

### 🔍 Prévisualisation des Sources

L'interface affiche maintenant :

```
📊 Statistiques des fichiers :
📄 PDF: 25  📝 TXT: 10  🖼️ Images: 5  📎 Autres: 2

📋 Projets détectés :
🎯 3 projet(s) identifié(s) depuis les fichiers .data.json
• 📂 P001_Application Mobile E-commerce
• 📂 P002_Site Web Corporate  
• 📂 P003_Formation Équipe

🏷️ Catégories détectées :
🔖 4 catégorie(s) identifiée(s) depuis les fichiers .data.json
• 🏷️ Développement
• 🏷️ Marketing
• 🏷️ Formation
• 🏷️ Documentation
```

### 📋 Résultats de Traitement

Après traitement, affichage détaillé :

```
🎯 Projets dans la base RAG
📊 3 projet(s) issus de fichiers .data.json détectés
📂 3 projet(s) identifié(s) au total

🏷️ Catégories dans la base RAG
🔖 4 catégorie(s) identifiée(s)
🏷️ Développement: 45    🏷️ Marketing: 20
🏷️ Formation: 15        🏷️ Documentation: 8
```

## 🛠️ Bonnes Pratiques

### ✅ Structure Recommandée

```
📁 Actions-11-Projects/
├── 📁 P001-Mobile-App/
│   ├── 📄 P001.data.json          ← Métadonnées du projet
│   ├── 📄 specs.pdf
│   ├── 📄 design.png
│   └── 📄 notes.txt
├── 📁 P002-Website/
│   ├── 📄 P002.data.json          ← Métadonnées du projet  
│   ├── 📄 mockups.pdf
│   └── 📄 content.txt
```

### 📋 Fichier .data.json Type

```json
{
    "dossier": "P001",
    "description": "Application Mobile E-commerce",
    "categorie": "Développement",
    "contact": "Jean Dupont",
    "entreprise": "TechCorp",
    "Date": "2025-01-15",
    "etat": "En cours",
    "action": "Développer l'interface utilisateur",
    "todo": "Tests unitaires à compléter",
    "Commentaire": "Projet prioritaire pour Q1 2025",
    "url": "https://github.com/techcorp/mobile-app",
    "tel": "0123456789",
    "mail": "jean.dupont@techcorp.com"
}
```

### 🔧 Enrichissement Automatique

Le système génère automatiquement :

```
🎯 Projet: "P001_Application Mobile E-commerce"
🏷️ Catégorie: "Développement" 
👤 Auteur: "Jean Dupont"
📅 Date: "2025-01-15"
📝 Description: "Application Mobile E-commerce | Action: Développer l'interface utilisateur | Todo: Tests unitaires à compléter | Contact: Jean Dupont | Tel: 0123456789"
🏷️ Tags: "En cours,TechCorp,Jean Dupont,Développement"
⚡ Priorité: "normal" (basée sur l'état)
📊 Statut: "in_progress" (basé sur l'état)
```

## 🚀 Avantages

### 🎯 Organisation Automatique
- **Zéro configuration manuelle** - Tout est automatique
- **Cohérence garantie** - Mapping standardisé
- **Évolutif** - Supporte des milliers de projets

### 🔍 Recherche Enrichie
- **Recherche par projet** - Tous les documents d'un projet
- **Filtrage par catégorie** - Documents d'un type spécifique
- **Recherche combinée** - Projet + catégorie + auteur

### 📊 Analyse Avancée
- **Statistiques détaillées** - Vue d'ensemble de la base
- **Recommandations** - Amélioration de l'organisation
- **Matrice croisée** - Relations projets-catégories

### 🔄 Intégration Transparente
- **Chat RAG enrichi** - Comprend les projets et catégories
- **Interface unifiée** - Navigation fluide
- **Métadonnées riches** - Contexte complet pour l'IA

---

## 🎉 Résultat Final

Votre base RAG devient une **bibliothèque intelligente** où :
- ✅ Chaque `.data.json` crée automatiquement un projet structuré
- ✅ Les catégories organisent vos documents par thème
- ✅ La recherche et le chat comprennent votre organisation
- ✅ L'analyse vous guide pour optimiser votre structure

**🚀 Plus besoin de configuration manuelle - laissez le RAG organiser vos données !**
