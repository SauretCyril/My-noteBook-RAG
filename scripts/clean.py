#!/usr/bin/env python3
"""Script de nettoyage de la base vectorielle."""

import os
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime

def clean_vector_database(vector_db_path="vector_db"):
    """Nettoie complètement la base vectorielle."""
    
    print("🧹 NETTOYAGE DE LA BASE VECTORIELLE")
    print("="*50)
    
    if os.path.exists(vector_db_path):
        # Créer une sauvegarde
        backup_name = f"vector_db_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = f"archive/{backup_name}"
        
        print(f"📦 Création de la sauvegarde: {backup_path}")
        os.makedirs("archive", exist_ok=True)
        shutil.copytree(vector_db_path, backup_path)
        
        # Supprimer l'ancienne base
        print(f"🗑️  Suppression de l'ancienne base: {vector_db_path}")
        shutil.rmtree(vector_db_path)
        
        print("✅ Base vectorielle nettoyée avec succès!")
        print(f"💾 Sauvegarde créée: {backup_path}")
    else:
        print("ℹ️  Aucune base vectorielle trouvée à nettoyer.")

def clean_cache():
    """Nettoie les caches Python et Streamlit."""
    
    print("\n🧽 NETTOYAGE DES CACHES")
    print("="*30)
    
    # Cache Python
    cache_dirs = []
    for root, dirs, files in os.walk("."):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                cache_dirs.append(os.path.join(root, dir_name))
    
    for cache_dir in cache_dirs:
        try:
            shutil.rmtree(cache_dir)
            print(f"🗑️  Supprimé: {cache_dir}")
        except Exception as e:
            print(f"⚠️  Erreur: {cache_dir} - {e}")
    
    # Cache Streamlit
    streamlit_cache = ".streamlit"
    if os.path.exists(streamlit_cache):
        try:
            shutil.rmtree(streamlit_cache)
            print(f"🗑️  Supprimé: {streamlit_cache}")
        except Exception as e:
            print(f"⚠️  Erreur: {streamlit_cache} - {e}")
    
    print("✅ Caches nettoyés!")

def clean_temp_files():
    """Nettoie les fichiers temporaires."""
    
    print("\n🗂️  NETTOYAGE DES FICHIERS TEMPORAIRES")
    print("="*40)
    
    temp_patterns = [
        "*.tmp", "*.temp", "*.log", "*.pyc", 
        ".DS_Store", "Thumbs.db", "*.bak"
    ]
    
    cleaned_count = 0
    for pattern in temp_patterns:
        for file_path in Path(".").rglob(pattern):
            try:
                file_path.unlink()
                print(f"🗑️  Supprimé: {file_path}")
                cleaned_count += 1
            except Exception as e:
                print(f"⚠️  Erreur: {file_path} - {e}")
    
    print(f"✅ {cleaned_count} fichiers temporaires supprimés!")

def main():
    """Fonction principale."""
    
    parser = argparse.ArgumentParser(description="Nettoyage du projet RAG")
    parser.add_argument("--vector-db", action="store_true", 
                       help="Nettoyer la base vectorielle")
    parser.add_argument("--cache", action="store_true", 
                       help="Nettoyer les caches")
    parser.add_argument("--temp", action="store_true", 
                       help="Nettoyer les fichiers temporaires")
    parser.add_argument("--all", action="store_true", 
                       help="Nettoyage complet")
    
    args = parser.parse_args()
    
    if not any([args.vector_db, args.cache, args.temp, args.all]):
        print("🤖 SCRIPT DE NETTOYAGE RAG")
        print("="*30)
        print("Utilisation:")
        print("  python scripts/clean.py --all          # Nettoyage complet")
        print("  python scripts/clean.py --vector-db    # Base vectorielle uniquement")
        print("  python scripts/clean.py --cache        # Caches uniquement") 
        print("  python scripts/clean.py --temp         # Fichiers temporaires uniquement")
        return
    
    print("🤖 DÉMARRAGE DU NETTOYAGE RAG")
    print("="*40)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    if args.all or args.vector_db:
        clean_vector_database()
    
    if args.all or args.cache:
        clean_cache()
    
    if args.all or args.temp:
        clean_temp_files()
    
    print("\n✨ NETTOYAGE TERMINÉ!")
    print("🎯 Votre projet RAG est maintenant propre et optimisé.")

if __name__ == "__main__":
    main()
