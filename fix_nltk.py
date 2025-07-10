#!/usr/bin/env python3
"""
Script pour télécharger et installer les ressources NLTK nécessaires
"""
import nltk
import ssl

def fix_nltk_downloads():
    """Télécharge toutes les ressources NLTK nécessaires"""
    
    # Contournement SSL si nécessaire
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context
    
    print("📥 Téléchargement des ressources NLTK...")
    
    # Liste des ressources nécessaires
    resources = [
        'punkt',           # Tokenizer classique
        'punkt_tab',       # Nouveau tokenizer
        'stopwords',       # Mots vides
        'wordnet',         # Base lexicale
        'omw-1.4',         # Multi-lingual wordnet
        'averaged_perceptron_tagger',  # POS tagger
    ]
    
    for resource in resources:
        try:
            print(f"  📦 Téléchargement de {resource}...")
            nltk.download(resource, quiet=False)
            print(f"  ✅ {resource} installé avec succès")
        except Exception as e:
            print(f"  ❌ Erreur avec {resource}: {e}")
    
    print("\n🎉 Installation des ressources NLTK terminée !")
    
    # Test de vérification
    print("\n🧪 Test de vérification...")
    try:
        from nltk.tokenize import sent_tokenize, word_tokenize
        from nltk.corpus import stopwords
        
        test_text = "Ceci est un test. NLTK fonctionne correctement !"
        sentences = sent_tokenize(test_text)
        words = word_tokenize(test_text)
        
        print(f"  ✅ Segmentation en phrases : {len(sentences)} phrases")
        print(f"  ✅ Tokenisation : {len(words)} mots")
        print("  ✅ Tous les tests passent !")
        
    except Exception as e:
        print(f"  ❌ Erreur lors du test : {e}")

if __name__ == "__main__":
    fix_nltk_downloads()
