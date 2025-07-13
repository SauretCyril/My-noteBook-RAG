# 🔧 Guide de Résolution - Problèmes Streamlit

## ❓ Message "Is Streamlit still running?"

Ce message apparaît quand le serveur Streamlit s'arrête de manière inattendue.

### 🔍 **Causes Fréquentes**

#### 1. **🛑 Arrêt Accidentel**
- **Ctrl+C** pressé dans le terminal
- **Fermeture du terminal** VS Code
- **Redémarrage de l'ordinateur**

#### 2. **⚡ Crash de l'Application**
- **Erreur de code** dans l'application
- **Import manquant** ou module non trouvé
- **Mémoire insuffisante**

#### 3. **🔌 Conflit de Port**
- **Port déjà utilisé** par une autre application
- **Multiples instances** Streamlit
- **Permissions réseau** insuffisantes

#### 4. **🐍 Problème d'Environnement**
- **Version Python** incompatible
- **Packages manquants** ou corrompus
- **Environnement virtuel** désactivé

---

## 🛠️ **Solutions par Ordre de Priorité**

### 🚀 **Solution 1: Redémarrage Rapide**

```bash
# Méthode directe
cd "h:\Entreprendre\Actions-11-Projects\P014\My-noteBook-RAG"
python -m streamlit run app_with_debug.py --server.port 8509
```

**✅ À utiliser si :** L'arrêt était accidentel

---

### 🔄 **Solution 2: Script de Lancement Robuste**

Utilisez le script automatisé :

```batch
# Double-clic sur le fichier ou en ligne de commande
launch_rag_robust.bat
```

**✅ Avantages :**
- 🔍 **Détection automatique** du port libre
- 🔄 **Redémarrage automatique** en cas d'erreur
- 📊 **Vérifications préalables**

---

### 🔧 **Solution 3: Diagnostic Complet**

```bash
# Lancer le diagnostic système
python -m streamlit run system_diagnostic.py --server.port 8511
```

**🔍 Le diagnostic vérifie :**
- ✅ Version Python compatible
- ✅ Packages installés
- ✅ Ports disponibles
- ✅ Structure des fichiers
- ✅ Base vectorielle

---

### 🆘 **Solution 4: Nettoyage Complet**

Si les solutions précédentes échouent :

#### A. **Tuer tous les processus Streamlit**

```bash
# Windows
taskkill /f /im python.exe
# Ou plus spécifique
netstat -ano | findstr :8509
taskkill /PID <PID_NUMBER> /F
```

#### B. **Vérifier l'environnement Python**

```bash
# Vérifier la version
python --version

# Vérifier Streamlit
python -c "import streamlit; print(streamlit.__version__)"

# Réinstaller si nécessaire
pip install --upgrade streamlit
```

#### C. **Nettoyer le cache Streamlit**

```bash
# Supprimer le cache utilisateur
rmdir /s "%USERPROFILE%\.streamlit"

# Supprimer le cache de l'application
rmdir /s ".streamlit"
```

---

## 🎯 **Solutions par Type d'Erreur**

### 📝 **ModuleNotFoundError**

```python
# Erreur: No module named 'sentence_transformers'
```

**🔧 Solution :**
```bash
pip install -r requirements.txt
# Ou spécifiquement :
pip install sentence-transformers faiss-cpu PyPDF2 pytesseract opencv-python Pillow
```

### 🔌 **Port Already in Use**

```python
# Erreur: OSError: [Errno 98] Address already in use
```

**🔧 Solutions :**

1. **Changer de port :**
```bash
python -m streamlit run app_with_debug.py --server.port 8510
```

2. **Libérer le port :**
```bash
netstat -ano | findstr :8509
taskkill /PID <PID> /F
```

### 💾 **Memory Error**

```python
# Erreur: MemoryError ou OutOfMemoryError
```

**🔧 Solutions :**
1. **Redémarrer l'application** (libère la mémoire)
2. **Fermer autres applications** gourmandes
3. **Réduire la taille** de la base vectorielle
4. **Utiliser la pagination** dans l'affichage

### 📁 **File Not Found**

```python
# Erreur: FileNotFoundError: vector_db.pkl
```

**🔧 Solution :**
- La base sera créée automatiquement au premier lancement
- Ou lancez un traitement par lots pour générer la base

---

## 🔄 **Scripts de Récupération Automatique**

### 📄 **launch_rag_robust.bat**

Script qui :
- ✅ Vérifie la disponibilité du port
- ✅ Trouve automatiquement un port libre
- ✅ Relance en cas d'erreur
- ✅ Affiche les URLs d'accès

### 📄 **system_diagnostic.py**

Interface Streamlit qui :
- ✅ Teste tous les composants
- ✅ Identifie les problèmes
- ✅ Propose des solutions
- ✅ Génère un rapport complet

---

## 📊 **Ports Streamlit Standards**

| Port | Usage | Status |
|------|-------|--------|
| **8501** | Streamlit par défaut | Souvent occupé |
| **8502-8508** | Instances multiples | Variables |
| **8509** | **RAG Application** | **Recommandé** |
| **8510** | Secours automatique | Libre |
| **8511** | Diagnostic | Libre |

---

## 🚨 **En Cas d'Urgence**

### **Redémarrage Total :**

1. **Fermer VS Code** complètement
2. **Redémarrer VS Code**
3. **Ouvrir un terminal** frais
4. **Lancer le script robuste :**

```bash
cd "h:\Entreprendre\Actions-11-Projects\P014\My-noteBook-RAG"
launch_rag_robust.bat
```

### **Vérification Finale :**

```bash
# Test rapide de fonctionnement
python -c "
import streamlit as st
import sys
print(f'Python: {sys.version}')
print(f'Streamlit: {st.__version__}')
print('✅ Environnement OK')
"
```

---

## 📱 **Applications Disponibles**

Une fois résolus les problèmes, vous avez accès à :

| URL | Application | Description |
|-----|-------------|-------------|
| **http://localhost:8509** | **RAG Principal** | Interface complète avec projets |
| **http://localhost:8511** | **Diagnostic** | Tests et vérifications |

---

## 💡 **Conseils Préventifs**

### ✅ **Bonnes Pratiques**

1. **Utiliser le script robuste** `launch_rag_robust.bat`
2. **Ne pas fermer brutalement** le terminal (Ctrl+C proprement)
3. **Vérifier les ports** avant lancement
4. **Garder l'environnement** Python à jour
5. **Sauvegarder régulièrement** la base vectorielle

### 🔍 **Surveillance**

- **Surveiller les logs** dans le terminal
- **Utiliser le diagnostic** en cas de doute
- **Tester sur port de secours** si problème
- **Redémarrer périodiquement** pour optimiser la mémoire

---

## 📞 **Support Avancé**

Si les solutions ne résolvent pas le problème :

1. **Lancer le diagnostic** et noter les erreurs
2. **Copier les messages d'erreur** complets
3. **Vérifier les logs** Streamlit dans le terminal
4. **Essayer sur un port différent** (8510, 8511)

**🎯 Dans 99% des cas, le script `launch_rag_robust.bat` résout automatiquement les problèmes !**
