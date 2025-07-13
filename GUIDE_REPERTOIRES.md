## 🎯 GUIDE : CHOIX DU RÉPERTOIRE DANS LE RAG

### ✅ NOUVELLES FONCTIONNALITÉS

L'interface de traitement par lots a été améliorée pour vous permettre de choisir facilement le répertoire à traiter :

#### 📂 **Sélection rapide par boutons radio**
- 🟢 **Actions-11-Projects** _(Recommandé)_ : Projets actuels avec .data.json
- 🟡 **Actions-4b_new** _(Archive)_ : Anciens projets et documents  
- 🔵 **Personnalisé** : N'importe quel répertoire

#### 🧠 **Détection intelligente des conflits**
- Analyse automatique de la base vectorielle existante
- Avertissement si mélange de répertoires différents
- Recommandations contextuelles selon votre choix

#### 🧹 **Gestion de la base**
- Bouton "Nettoyer la base" pour vider complètement
- Bouton "Analyser la base" pour voir le contenu détaillé
- Statistics temps réel des documents indexés

### 🚀 UTILISATION

1. **Lancez l'application** : `python launch_simple.bat`
2. **Allez dans "📁 Traitement Lots"**
3. **Choisissez votre répertoire** via les boutons radio :
   - Pour les projets actuels → **Actions-11-Projects**
   - Pour les archives → **Actions-4b_new**
   - Pour autre chose → **Personnalisé**
4. **Suivez les recommandations** affichées
5. **Lancez le traitement**

### 💡 CAS D'USAGE

#### **Traiter Actions-4b_new uniquement**
- Sélectionnez "Actions-4b_new (Ancien répertoire)"
- Si conflit détecté → Cliquez "🧹 Nettoyer la base"
- Lancez le traitement

#### **Traiter Actions-11-Projects uniquement**  
- Sélectionnez "Actions-11-Projects (Projets actuels)"
- Si conflit détecté → Cliquez "🧹 Nettoyer la base"
- Lancez le traitement

#### **Mélanger les deux répertoires**
- Traitez d'abord un répertoire
- Puis traitez l'autre (les documents s'ajoutent)
- ⚠️ Attention aux doublons potentiels

### 🎉 AVANTAGES

✅ **Flexibilité totale** : Choisissez n'importe quel répertoire  
✅ **Sécurité** : Détection automatique des conflits  
✅ **Simplicité** : Interface guidée avec boutons rapides  
✅ **Transparence** : Statistiques et analyse de la base  
✅ **Contrôle** : Nettoyage en un clic si nécessaire  

### 🔧 RÉSOLUTION DE PROBLÈMES

**Le Chat RAG ne trouve pas mon projet ?**
1. Vérifiez que le bon répertoire a été traité
2. Utilisez "📊 Analyser la base" pour voir le contenu
3. Si mauvais répertoire → "🧹 Nettoyer" puis retraiter

**Mélange de répertoires ?**
1. L'interface vous avertira automatiquement
2. Suivez les recommandations affichées
3. Nettoyez si nécessaire pour éviter la confusion

Maintenant vous avez un contrôle total sur vos données ! 🎯
