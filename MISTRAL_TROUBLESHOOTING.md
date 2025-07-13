# 🛠️ Guide de Dépannage Mistral

## ⚠️ Erreur 429 - Service Tier Capacity Exceeded

### 🔍 Problème
```
Service tier capacity exceeded for this model
```

Cette erreur indique que vous avez atteint la limite de votre tier gratuit Mistral.

### 🔄 Solutions Immédiates

#### 1. **Modèle Plus Léger**
- Changez vers `mistral-small-latest`
- Plus rapide et consomme moins de ressources
- Qualité toujours excellente pour la plupart des tâches

#### 2. **Attendez et Réessayez**
- Les limites se réinitialisent périodiquement
- Attendez 5-10 minutes
- Réessayez votre question

#### 3. **Ollama Local (Recommandé)**
```bash
# Installation
# 1. Téléchargez: https://ollama.ai
# 2. Installez et redémarrez le terminal

# Télécharger Mistral
ollama pull mistral:7b

# Démarrer Ollama
ollama serve
```

**Dans l'application :**
1. Allez dans "Configuration Mistral AI"
2. Sélectionnez "Ollama Local"
3. Testez la connexion
4. Profitez d'un service illimité !

### 💰 Solutions Payantes

#### Upgrade Mistral
- Allez sur https://console.mistral.ai/
- Section "Billing" 
- Upgrade vers un tier supérieur
- Plus de capacité et de vitesse

### ✅ Comparaison des Solutions

| Solution | Coût | Limite | Vitesse | Confidentialité |
|----------|------|--------|---------|-----------------|
| Mistral Free | Gratuit | Limitée | Rapide | API externe |
| Mistral Pro | Payant | Élevée | Très rapide | API externe |
| Ollama Local | Gratuit | Aucune | Moyenne | 100% local |

### 🎯 Recommandation

**Pour débuter :** Ollama Local
- Installation simple
- Gratuit et illimité
- Parfait pour tester et développer

**Pour production :** Mistral Pro
- Performance optimale
- Support professionnel
- Intégration cloud

### 🔧 Configuration Optimale

#### Ollama (Recommandé)
```yaml
Provider: Ollama Local
URL: http://localhost:11434
Modèle: mistral:7b
```

#### Mistral API (Alternative)
```yaml
Provider: Mistral API
Modèle: mistral-small-latest  # Plus économique
```

---

## 🆘 Autres Erreurs Courantes

### Erreur 401 - Unauthorized
- Vérifiez votre clé API dans le fichier `.env`
- Régénérez une nouvelle clé sur https://console.mistral.ai/

### Erreur 500 - Server Error
- Problème temporaire de Mistral
- Réessayez dans quelques minutes
- Ou basculez vers Ollama

### Timeout
- Votre connexion est lente
- Augmentez le timeout dans le code
- Ou utilisez Ollama local

---

## 📞 Support

Si les problèmes persistent :
1. Vérifiez votre configuration dans l'application
2. Testez Ollama comme alternative
3. Consultez la documentation Mistral
4. Postez une issue sur le repo GitHub
