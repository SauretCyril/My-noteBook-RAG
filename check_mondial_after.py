"""Vérification rapide après indexation."""

import pickle
import os

def check_mondial_indexed():
    """Vérifie si Mondial Tissus est maintenant indexé."""
    
    db_path = 'data/docs/vector_db.pkl'
    
    if not os.path.exists(db_path):
        print("❌ Base vectorielle non trouvée après indexation")
        return
    
    with open(db_path, 'rb') as f:
        db = pickle.load(f)
    
    print(f"📊 Total documents après indexation: {len(db.documents)}")
    
    # Chercher 'mondial'
    mondial_docs = []
    for i, doc in enumerate(db.documents):
        text = doc.get('text', '').lower()
        if 'mondial' in text:
            source = doc.get('metadata', {}).get('source', 'N/A')
            mondial_docs.append((i, source))
    
    print(f"🎯 Documents contenant 'mondial': {len(mondial_docs)}")
    
    if mondial_docs:
        print("🎉 SUCCÈS! Mondial Tissus est maintenant indexé!")
        for i, (idx, source) in enumerate(mondial_docs[:3]):
            print(f"  📄 {source}")
    else:
        print("❌ Mondial Tissus toujours pas trouvé")

if __name__ == "__main__":
    check_mondial_indexed()
