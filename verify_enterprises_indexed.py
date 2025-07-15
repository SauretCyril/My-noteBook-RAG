import os
from rag_app.core.vector_database import VectorDatabase

def main():
    # Charger la base vectorielle
    db = VectorDatabase.load()
    print(f"Documents indexés : {len(db.documents)}")
    entreprises = set()
    for doc in db.documents:
        meta = doc.get('metadata', {})
        # Cherche tous les alias possibles
        for key in ['entreprise', 'company', 'enterprise']:
            val = meta.get(key, '').strip()
            if val and val.lower() not in ['n/a', 'none', '']:
                entreprises.add(val)
    print(f"Entreprises détectées : {len(entreprises)}")
    for e in sorted(entreprises):
        print(f"- {e}")
    if not entreprises:
        print("Aucune entreprise détectée. Vérifiez l'indexation ou les champs de métadonnées.")

if __name__ == "__main__":
    main()
