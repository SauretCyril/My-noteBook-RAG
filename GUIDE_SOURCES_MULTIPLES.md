# 📂 Guide - Gestion Multi-Sources
# taskkill /f /im streamlit.exe
# streamlit run app_launcher.py --server.port 8502
## 🎯 Objectif

Cette nouvelle interface permet d'ajouter **n'importe quelles sources** de données à votre base vectorielle RAG, sans limitation aux répertoires prédéfinis.

## 🚀 Fonctionnalités

### ➕ Ajout de Sources Flexibles

#### **Raccourcis Rapides**
- 📁 **Actions-11-Projects** : Projets actuels (recommandé)
- 📁 **Actions-4b_new** : Archives des anciens projets
- 📁 **Desktop** : Bureau utilisateur
- 📁 **Documents** : Dossier Documents

#### **Chemins Personnalisés**
- Saisissez n'importe quel chemin : `C:\MesProjets\Dossier1`
- Supports réseau : `\\serveur\partage\projets`
- Clés USB : `E:\MesDonnees`
- Dossiers cloud : `C:\Users\MonNom\OneDrive\Projets`

### 📋 Gestion Multi-Sources

#### **Interface Interactive**
- ✅ **Vérification automatique** : Existence et accessibilité des chemins
- 📊 **Comptage de fichiers** : Estimation du nombre de documents
- 👁️ **Prévisualisation** : Scan et analyse de chaque source
- 🗑️ **Suppression flexible** : Retrait individuel des sources

#### **Types de Sources Supportés**
- 📁 **Répertoires locaux** : Disques durs, SSD
- 🌐 **Partages réseau** : Serveurs d'entreprise
- 💾 **Supports amovibles** : Clés USB, disques externes
- ☁️ **Dossiers cloud synchronisés** : OneDrive, Dropbox, Google Drive
- 📦 **Archives** : Tout répertoire contenant des documents

## 🔍 Détection Intelligente des Conflits

### **Analyse Automatique**
- 🧮 **Échantillonnage** : Analyse des 100 premiers documents
- 📊 **Statistiques** : Répartition par sources existantes
- ⚠️ **Conflits** : Détection des incompatibilités
- ✅ **Compatibilité** : Identification des sources cohérentes

### **Types de Conflits**
1. **Actions-11 vs Actions-4b** : Mélange projets actuels/archives
2. **Sources multiples** : Combinaison de différents emplacements
3. **Nouvelles sources** : Ajout de chemins inédits

### **Recommandations**
- 🔄 **Ajouter** : Pour enrichir la base existante
- 🧹 **Nettoyer** : Pour un nouveau départ (recommandé en cas de conflit)

## 📊 Traitement Multi-Sources

### **Options Globales**
- 📄 **Types de fichiers** : PDF, TXT, Images (PNG, JPG, JPEG)
- 📏 **Taille maximale** : Limite configurable par fichier
- 🔍 **Vision avancée** : OCR et classification d'images
- 🏷️ **Métadonnées** : Support des formats `.data.json`, `._rag_.data`, notes

### **Traitement Parallèle**
1. **Validation** : Vérification de toutes les sources
2. **Progression** : Barre de progression globale
3. **Source par source** : Traitement séquentiel avec feedback
4. **Agrégation** : Compilation des résultats globaux

### **Résultats Détaillés**
- 📊 **Statistiques globales** : Succès, erreurs, ignorés
- 📂 **Détail par source** : Résultats individuels
- 🖼️ **Images traitées** : Aperçu des analyses visuelles
- 💾 **Sauvegarde automatique** : Base vectorielle mise à jour

## 🛠️ Exemples d'Utilisation

### **Cas 1 : Projets Multiples**
```
Sources ajoutées :
- h:\Entreprendre\Actions-11-Projects (Actuels)
- h:\Entreprendre\Actions-4b_new (Archives)
- C:\Users\MonNom\Desktop\NouveauxProjets (Brouillons)
```

### **Cas 2 : Équipe Distribuée**
```
Sources ajoutées :
- \\serveur\projets\equipe1 (Équipe développement)
- \\serveur\projets\equipe2 (Équipe design)
- C:\Users\MonNom\OneDrive\MesProjets (Personnel)
```

### **Cas 3 : Migration de Données**
```
Sources ajoutées :
- E:\AncienPC\Projets (Migration USB)
- C:\Sauvegarde\ProjetArchives (Archives locales)
- \\nas\backup\projets2024 (Sauvegarde réseau)
```

## ⚙️ Configuration Avancée

### **Paramètres Recommandés**

#### **Pour Performances Optimales**
- ✅ Types de fichiers : PDF, TXT uniquement
- 📏 Taille max : 50 MB
- ❌ Vision avancée : Désactivée

#### **Pour Analyse Complète**
- ✅ Types de fichiers : Tous (PDF, TXT, Images)
- 📏 Taille max : 200 MB
- ✅ Vision avancée : Activée

### **Gestion Mémoire**
- 🧹 **Nettoyage régulier** : Base vectorielle trop volumineuse
- 💾 **Sauvegarde** : Backup avant ajouts importants
- 📊 **Monitoring** : Surveillance de la taille de base

## 🚨 Bonnes Pratiques

### **Avant Traitement**
1. 🔍 **Prévisualisation** : Scanner chaque source individuellement
2. ⚠️ **Analyse conflits** : Vérifier la compatibilité
3. 🧹 **Nettoyage** : Vider la base si nécessaire
4. 💾 **Sauvegarde** : Backup de la base actuelle

### **Pendant Traitement**
1. 🔌 **Alimentation** : Assurer la stabilité électrique
2. 🌐 **Réseau** : Maintenir les connexions aux sources réseau
3. 💾 **Espace disque** : Vérifier l'espace disponible
4. ⏱️ **Patience** : Le traitement peut prendre du temps

### **Après Traitement**
1. 📊 **Vérification** : Contrôler les résultats
2. 🔍 **Test recherche** : Valider l'indexation
3. 🗑️ **Nettoyage** : Vider la liste des sources
4. 📝 **Documentation** : Noter les sources traitées

## 🆘 Dépannage

### **Problèmes Courants**

#### **Source Non Trouvée**
```
❌ Répertoire non trouvé ou inaccessible
```
**Solutions :**
- Vérifier le chemin exact
- Contrôler les permissions d'accès
- Tester la connexion réseau (si applicable)

#### **Conflit de Sources**
```
⚠️ Conflit détecté entre Actions-11 et Actions-4b
```
**Solutions :**
- Nettoyer la base avant traitement
- Ou accepter la base mixte

#### **Échec de Traitement**
```
❌ Erreur traitement source X : Permission denied
```
**Solutions :**
- Vérifier les droits d'accès
- Exécuter en administrateur si nécessaire
- Exclure les fichiers problématiques

### **Optimisations**

#### **Sources Volumineuses**
- 📊 Limiter les types de fichiers
- 📏 Réduire la taille maximale
- 🔍 Désactiver la vision avancée

#### **Base Saturée**
- 🧹 Nettoyer régulièrement
- 📂 Séparer par thématiques
- 💾 Archiver les anciennes données

## 📞 Support

Pour toute question ou problème :
1. 📊 Utiliser "Analyser la base" pour diagnostiquer
2. 🧹 Essayer "Nettoyer la base" en cas de conflit
3. 👁️ Prévisualiser les sources avant traitement
4. 📝 Noter les messages d'erreur pour assistance

---

**💡 Astuce :** Cette interface flexible permet de créer une base vectorielle centralisée à partir de toutes vos sources de données, où qu'elles se trouvent !
