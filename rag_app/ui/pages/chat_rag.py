"""Page de chat RAG intelligent avec Mistral AI."""

import streamlit as st
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

# Charger les variables d'environnement
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Utiliser st.warning seulement si le contexte Streamlit est disponible
    import sys
    if 'streamlit' in sys.modules:
        try:
            st.warning("⚠️ Module python-dotenv non installé. Exécutez: pip install python-dotenv")
        except:
            print("⚠️ Module python-dotenv non installé. Exécutez: pip install python-dotenv")

def _load_mistral_api_key() -> Optional[str]:
    """Charge la clé API Mistral depuis le fichier .env."""
    api_key = os.getenv('MISTRAL_API_KEY')
    if api_key:
        return api_key
    
    # Fallback : essayer de lire le fichier .env directement
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env')
    if os.path.exists(env_path):
        try:
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('MISTRAL_API_KEY'):
                        return line.split('=')[1].strip().strip('"')
        except Exception as e:
            # Éviter les erreurs de contexte Streamlit
            try:
                st.error(f"Erreur lecture .env: {e}")
            except:
                print(f"Erreur lecture .env: {e}")
    
    return None

def show() -> None:
    """Affiche la page de chat RAG."""
    
    st.header("💬 Chat RAG - Assistant Intelligent")
    
    # Vérification de la base vectorielle
    if 'vector_db' not in st.session_state:
        st.error("⚠️ Base vectorielle non initialisée")
        return
        
    vector_db = st.session_state.vector_db
    
    if not vector_db.documents:
        st.warning("📭 Aucun document dans la base. Ajoutez d'abord des documents via le traitement par lots.")
        return
    
    # Configuration Mistral
    _show_mistral_config()
    
    # Interface de chat
    _show_chat_interface(vector_db)
    
    # Exemples de questions
    _show_example_questions()

def _show_mistral_config() -> None:
    """Affiche la configuration Mistral AI."""
    
    with st.expander("⚙️ Configuration Mistral AI"):
        provider = st.selectbox(
            "Choisir le fournisseur Mistral",
            ["Mistral API", "Ollama Local", "Hugging Face"],
            key="mistral_provider"
        )
        
        if provider == "Mistral API":
            # Charger la clé API depuis .env
            env_api_key = _load_mistral_api_key()
            
            if env_api_key:
                st.success("🔒 Clé API Mistral chargée depuis le fichier .env")
                st.info(f"🔑 Clé: {'*' * (len(env_api_key) - 8) + env_api_key[-8:]}")
                # Stocker la clé dans la session pour utilisation
                st.session_state.mistral_api_key = env_api_key
            else:
                st.warning("❌ Aucune clé API trouvée dans le fichier .env")
                st.info("💡 Ajoutez MISTRAL_API_KEY=\"votre_clé\" dans le fichier .env")
                
                # Aide pour les limites
                st.error("⚠️ **Limite de capacité atteinte ?**")
                st.info("📖 Consultez le guide de dépannage : `MISTRAL_TROUBLESHOOTING.md`")
                st.info("🔄 **Solution rapide :** Utilisez Ollama Local (gratuit et illimité)")
                
                # Option de saisie manuelle en fallback (masquée)
                with st.expander("🔧 Saisie manuelle (fallback)"):
                    manual_key = st.text_input(
                        "Clé API Mistral (temporaire)",
                        type="password",
                        key="mistral_api_key_manual",
                        help="Cette clé ne sera pas sauvegardée"
                    )
                    if manual_key:
                        st.session_state.mistral_api_key = manual_key
            
            model = st.selectbox(
                "Modèle",
                ["mistral-small-latest", "mistral-large-latest", "mistral-medium-latest"],
                key="mistral_model",
                help="mistral-small-latest recommandé si vous avez des limites de capacité"
            )
            
        elif provider == "Ollama Local":
            ollama_url = st.text_input(
                "URL Ollama",
                value="http://localhost:11434",
                key="ollama_url"
            )
            model = st.selectbox(
                "Modèle Ollama",
                ["mistral:7b", "mistral:latest", "mistral-nemo:latest"],
                key="ollama_model"
            )
            st.success("💡 **Ollama = Solution gratuite et illimitée !**")
            st.info("� Installation : https://ollama.ai puis `ollama pull mistral:7b`")
            
            # Test de connexion Ollama
            if st.button("🔍 Tester Ollama"):
                _test_ollama_connection(ollama_url)
            
            # Guide rapide d'installation
            with st.expander("📥 Guide installation Ollama"):
                st.markdown("""
                **🚀 Installation rapide Ollama :**
                
                1. **Téléchargez Ollama :** https://ollama.ai
                2. **Installez** et redémarrez votre terminal
                3. **Téléchargez Mistral :**
                   ```bash
                   ollama pull mistral:7b
                   ```
                4. **Démarrez Ollama :**
                   ```bash
                   ollama serve
                   ```
                5. **Testez** avec le bouton ci-dessus
                
                ✅ **Avantages Ollama :**
                - 🆓 Gratuit et illimité
                - 🔒 Privé (tout en local)
                - ⚡ Pas de limites API
                """)
            
            
        else:  # Hugging Face
            model = st.selectbox(
                "Modèle Hugging Face",
                ["mistralai/Mistral-7B-Instruct-v0.1", "mistralai/Mixtral-8x7B-Instruct-v0.1"],
                key="hf_model"
            )
            st.info("⚠️ Modèles Hugging Face plus lents mais gratuits")

def _show_chat_interface(vector_db) -> None:
    """Affiche l'interface de chat."""
    
    st.markdown("### 🤖 Posez vos questions")
    
    # Initialiser l'historique de chat
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Zone de saisie de question
    question = st.text_input(
        "Votre question :",
        placeholder="Ex: Qui est Cyril Sauret ? Quelles sont ses compétences ?",
        key="user_question"
    )
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🚀 Poser la question", type="primary"):
            if question.strip():
                _process_question(question, vector_db)
                
    with col2:
        if st.button("🗑️ Vider historique"):
            st.session_state.chat_history = []
            st.rerun()
    
    with col3:
        if st.button("🔧 Diagnostic base"):
            _run_database_diagnostic(vector_db)
    
    # Afficher l'historique de chat
    _display_chat_history()

def _process_question(question: str, vector_db) -> None:
    """Traite une question utilisateur."""
    
    try:
        # 1. Recherche de documents pertinents avec debug
        with st.spinner("🔍 Recherche dans les documents..."):
            relevant_docs = vector_db.search(question, top_k=5)
        
        # DEBUG: Afficher les informations de recherche
        st.info(f"🔍 **Debug recherche :** {len(relevant_docs)} documents trouvés pour '{question}'")
        
        # DEBUG: Analyse détaillée des résultats
        if relevant_docs:
            st.success("✅ Documents trouvés par la recherche vectorielle")
            # Afficher des infos sur les documents trouvés
            for i, doc in enumerate(relevant_docs[:3]):
                if isinstance(doc, dict):
                    metadata = doc.get('metadata', {})
                    text_preview = doc.get('text', '')[:100].replace('\n', ' ')
                    source = metadata.get('source', 'N/A')
                else:
                    # Analyser la structure du document
                    doc_type = type(doc).__name__
                    doc_attrs = dir(doc)
                    st.info(f"Type document: {doc_type}, Attributs: {doc_attrs[:5]}...")
                    
                    if hasattr(doc, 'metadata'):
                        metadata = doc.metadata if isinstance(doc.metadata, dict) else {}
                        source = metadata.get('source', 'N/A')
                        text_preview = getattr(doc, 'page_content', getattr(doc, 'text', str(doc)))[:100]
                    else:
                        source = "N/A (structure inconnue)"
                        text_preview = str(doc)[:100]
                
                st.info(f"📄 Doc {i+1}: {source} - {text_preview}...")
        else:
            st.warning("❌ Recherche vectorielle retourne 0 résultats")
        
        # FORCE: Toujours utiliser la recherche directe en complément de la recherche vectorielle
        # ou quand la recherche vectorielle échoue
        should_use_direct = (
            len(relevant_docs) == 0 or 
            all(doc.get('metadata', {}).get('source') == 'N/A' for doc in relevant_docs) or
            max([doc.get('similarity', 0) for doc in relevant_docs] + [0]) < 0.3  # Similarité faible
        )
        
        if should_use_direct:
            st.info("🔄 Activation de la recherche directe (mode secours)")
            
            # Accéder directement aux documents 
            if hasattr(vector_db, 'documents'):
                direct_matches = []
                search_terms = question.lower().split()
                
                for doc in vector_db.documents:
                    doc_text = doc.get('text', '').lower()
                    doc_metadata = doc.get('metadata', {})
                    doc_source = doc_metadata.get('source', '').lower()
                    doc_tags = doc_metadata.get('tags', '').lower()
                    
                    # Rechercher dans le texte, la source et les tags
                    match_found = False
                    match_score = 0
                    
                    # Recherche précise pour tous les termes de la question
                    for term in search_terms:
                        if len(term) >= 3:  # Éviter les mots trop courts
                            # Recherche exacte dans le texte (plus importante)
                            if term in doc_text:
                                match_found = True
                                match_score += 3
                            # Recherche dans la source/nom de fichier
                            elif term in doc_source:
                                match_found = True
                                match_score += 2
                            # Recherche dans les tags
                            elif term in doc_tags:
                                match_found = True
                                match_score += 1
                    
                    # N'ajouter que si le score est suffisant
                    if match_found and match_score >= 2:
                        direct_matches.append((doc, match_score))
                
                # Dédupliquer et trier par score
                seen_sources = set()
                unique_matches = []
                
                # Trier par score décroissant
                direct_matches.sort(key=lambda x: x[1], reverse=True)
                
                for doc, score in direct_matches:
                    source = doc.get('metadata', {}).get('source', '')
                    if source not in seen_sources and source != '':
                        unique_matches.append(doc)
                        seen_sources.add(source)
                        if len(unique_matches) >= 5:
                            break
                
                if unique_matches:
                    st.success(f"✅ Trouvé {len(unique_matches)} documents via recherche directe")
                    relevant_docs = unique_matches
                    
                    # Debug: afficher les sources trouvées
                    sources_found = [doc.get('metadata', {}).get('source', 'N/A') for doc in unique_matches]
                    st.info(f"📁 Sources: {sources_found[:3]}...")
                else:
                    st.error("❌ Aucun document trouvé même avec recherche directe")
                    return
            else:
                st.error("❌ Impossible d'accéder aux documents de la base")
                return
        
        # 2. Préparation du contexte
        context = _prepare_context(relevant_docs)
        
        # 2.5 Analyse intelligente d'existence de projet
        project_analysis = _analyze_project_existence(question, relevant_docs)
        if project_analysis:
            # Si on détecte une question sur l'existence d'un projet et qu'on a des documents
            st.success("🧠 Logique d'existence de projet déclenchée !")
            response = project_analysis
        else:
            # 2.6 Analyse intelligente des questions de type "liste"
            list_analysis = _analyze_list_request(question, relevant_docs)
            if list_analysis:
                st.success("📋 Logique de génération de liste déclenchée !")
                response = list_analysis
            else:
                # DEBUG: Afficher un aperçu du contexte
                st.info(f"📝 **Contexte préparé :** {len(context)} caractères")
                with st.expander("🔍 Aperçu du contexte"):
                    st.text(context[:500] + "..." if len(context) > 500 else context)
                
                # 3. Génération de la réponse avec Mistral
                with st.spinner("🤖 Génération de la réponse avec Mistral..."):
                    response = _generate_mistral_response(question, context)
        
        # 4. Ajout à l'historique
        chat_entry = {
            'timestamp': datetime.now().strftime("%H:%M:%S"),
            'question': question,
            'response': response,
            'sources': [doc.get('metadata', {}).get('source', 'N/A') for doc in relevant_docs],
            'debug_info': f"{len(relevant_docs)} docs trouvés"
        }
        
        st.session_state.chat_history.append(chat_entry)
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Erreur lors du traitement : {str(e)}")
        
        # DEBUG: Afficher plus d'informations sur l'erreur
        import traceback
        st.code(traceback.format_exc())

def _prepare_context(relevant_docs: List[Dict]) -> str:
    """Prépare le contexte à partir des documents pertinents."""
    
    if not relevant_docs:
        return "Aucun document pertinent trouvé."
    
    context_parts = []
    
    for i, doc in enumerate(relevant_docs, 1):
        # Gérer les différents formats de documents
        if isinstance(doc, dict):
            metadata = doc.get('metadata', {})
            text = doc.get('text', '')
        else:
            # Format alternatif
            metadata = getattr(doc, 'metadata', {}) if hasattr(doc, 'metadata') else {}
            text = getattr(doc, 'text', '') if hasattr(doc, 'text') else str(doc)
        
        # Assurer une longueur raisonnable du texte
        if not text or text.strip() == '':
            text = "Contenu non disponible"
        else:
            text = text[:2000] if len(text) > 2000 else text
        
        # Construire les informations source
        source_info = f"Document {i}"
        
        # Extraire les métadonnées disponibles
        source = metadata.get('source', 'Source inconnue')
        if source and source != 'N/A' and source != 'Source inconnue':
            # Extraire juste le nom du fichier pour plus de clarté
            if '\\' in source:
                source_name = source.split('\\')[-1]
            elif '/' in source:
                source_name = source.split('/')[-1]
            else:
                source_name = source
            source_info += f" ({source_name})"
        
        category = metadata.get('category', '')
        if category and category != 'N/A' and category.strip():
            source_info += f" - Catégorie: {category}"
        
        project = metadata.get('project', '')
        if project and project != 'N/A' and project.strip():
            source_info += f" - Projet: {project}"
        
        title = metadata.get('title', '')
        if title and title.strip():
            source_info += f" - Titre: {title}"
        
        # Ajouter le contexte avec des séparateurs clairs
        context_parts.append(f"=== {source_info} ===\n{text.strip()}\n")
    
    final_context = "\n".join(context_parts)
    
    # Debug: vérifier que le contexte n'est pas vide
    if not final_context.strip() or len(final_context.strip()) < 50:
        return f"Erreur: Contexte vide ou trop court. Documents: {len(relevant_docs)}"
    
    return final_context

def _generate_mistral_response(question: str, context: str) -> str:
    """Génère une réponse avec Mistral AI."""
    
    provider = st.session_state.get('mistral_provider', 'Mistral API')
    
    # Prompt système optimisé pour l'analyse de CV et candidatures
    system_prompt = """Tu es un assistant IA spécialisé dans l'analyse de CV et de candidatures professionnelles. 
    Tu réponds en français de manière précise et structurée.
    
    Ton rôle est d'analyser les documents fournis pour répondre aux questions sur :
    - Le profil professionnel de la personne
    - Ses compétences et expériences
    - Les entreprises et postes auxquels elle a postulé
    - Son parcours de carrière
    
    Utilise UNIQUEMENT les informations contenues dans les documents fournis.
    Si une information n'est pas disponible, indique-le clairement.
    Structure tes réponses de manière claire avec des puces ou des sections si nécessaire."""
    
    user_prompt = f"""Question: {question}

Documents pertinents:
{context}

Réponds de manière précise et structurée en te basant uniquement sur les documents fournis."""
    
    try:
        if provider == "Mistral API":
            return _call_mistral_api(system_prompt, user_prompt)
        elif provider == "Ollama Local":
            return _call_ollama(system_prompt, user_prompt)
        else:  # Hugging Face
            return _call_huggingface(system_prompt, user_prompt)
            
    except Exception as e:
        return f"❌ Erreur lors de la génération : {str(e)}\n\nVeuillez vérifier votre configuration Mistral."

def _call_mistral_api(system_prompt: str, user_prompt: str) -> str:
    """Appelle l'API Mistral."""
    
    # Récupérer la clé API depuis la session ou .env
    api_key = st.session_state.get('mistral_api_key') or _load_mistral_api_key()
    model = st.session_state.get('mistral_model', 'mistral-large-latest')
    
    if not api_key:
        return "❌ Clé API Mistral non configurée. Vérifiez votre fichier .env ou configurez-la manuellement."
    
    try:
        import requests
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        response = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        elif response.status_code == 429:
            error_data = response.json()
            error_type = error_data.get('type', '')
            
            if 'service_tier_capacity_exceeded' in error_type:
                return """⚠️ **Limite de capacité Mistral dépassée**

Votre tier de service Mistral a atteint sa limite. Voici vos options :

🔄 **Solutions immédiates :**
1. **Attendez quelques minutes** puis réessayez
2. **Utilisez un modèle plus petit** : mistral-small-latest (plus rapide, moins de ressources)
3. **Configurez Ollama local** (gratuit et illimité)

💡 **Configuration Ollama recommandée :**
- Téléchargez Ollama : https://ollama.ai
- Installez Mistral : `ollama pull mistral:7b`
- Démarrez : `ollama serve`
- Changez le provider vers "Ollama Local"

🚀 **Upgrade Mistral (payant) :**
- Allez sur https://console.mistral.ai/
- Upgrade vers un tier supérieur pour plus de capacité

**Réessayez dans quelques minutes ou changez de configuration !**"""
            else:
                return f"⚠️ **Limite de requêtes atteinte** (429)\n\nAttendez quelques minutes puis réessayez.\n\nDétails: {response.text}"
        else:
            return f"❌ Erreur API Mistral: {response.status_code} - {response.text}"
            
    except ImportError:
        return "❌ Module 'requests' non installé. Exécutez: pip install requests"
    except Exception as e:
        return f"❌ Erreur API Mistral: {str(e)}"

def _call_ollama(system_prompt: str, user_prompt: str) -> str:
    """Appelle Ollama local."""
    
    ollama_url = st.session_state.get('ollama_url', 'http://localhost:11434')
    model = st.session_state.get('ollama_model', 'mistral:7b')
    
    try:
        import requests
        
        data = {
            "model": model,
            "prompt": f"{system_prompt}\n\n{user_prompt}",
            "stream": False
        }
        
        response = requests.post(
            f"{ollama_url}/api/generate",
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('response', 'Pas de réponse')
        else:
            return f"❌ Erreur Ollama: {response.status_code}"
            
    except ImportError:
        return "❌ Module 'requests' non installé. Exécutez: pip install requests"
    except Exception as e:
        return f"❌ Erreur Ollama: {str(e)}. Vérifiez qu'Ollama est démarré."

def _call_huggingface(system_prompt: str, user_prompt: str) -> str:
    """Appelle Hugging Face (version simplifiée)."""
    
    # Pour l'instant, retourner une réponse basique
    # TODO: Implémenter l'intégration Hugging Face complète
    return """🔄 Intégration Hugging Face en cours de développement.
    
    Pour l'instant, utilisez :
    - Mistral API (recommandé) : Performant et rapide
    - Ollama Local : Gratuit et privé
    
    Basé sur votre question et les documents trouvés, voici un résumé des informations disponibles :
    
    Documents analysés : Documents pertinents trouvés dans votre base.
    
    💡 Conseil : Configurez Mistral API ou Ollama pour des réponses complètes."""

def _display_chat_history() -> None:
    """Affiche l'historique de chat."""
    
    if not st.session_state.chat_history:
        return
    
    st.markdown("### 📜 Historique des conversations")
    
    for i, entry in enumerate(reversed(st.session_state.chat_history)):
        with st.expander(f"💬 {entry['timestamp']} - {entry['question'][:50]}..."):
            
            # Question
            st.markdown(f"**❓ Question :** {entry['question']}")
            
            # Réponse
            st.markdown("**🤖 Réponse :**")
            st.markdown(entry['response'])
            
            # Sources
            if entry.get('sources'):
                st.markdown("**📚 Sources consultées :**")
                for source in entry['sources']:
                    st.markdown(f"- {source}")

def _show_example_questions() -> None:
    """Affiche des exemples de questions."""
    
    with st.expander("💡 Exemples de questions"):
        
        st.markdown("""
        ### 🎯 Questions sur le profil
        - "Qui est Cyril Sauret ?"
        - "Quel est le parcours professionnel de Cyril ?"
        - "Quelles sont les compétences principales de Cyril ?"
        - "Quelle est l'expérience de Cyril en tant que développeur ?"
        
        ### 🏢 Questions sur les candidatures
        - "À quelles entreprises Cyril a-t-il postulé ?"
        - "Quels types de postes recherche Cyril ?"
        - "Dans quels secteurs d'activité Cyril cherche-t-il ?"
        - "Quelles sont les dernières candidatures de Cyril ?"
        
        ### 📋 Questions techniques
        - "Quelles technologies maîtrise Cyril ?"
        - "Quelle est l'expérience de Cyril avec Python ?"
        - "Cyril a-t-il de l'expérience en IA/Machine Learning ?"
        - "Quels projets a réalisé Cyril ?"
        
        ### 📊 Questions d'analyse
        - "Résume le profil de Cyril en quelques points"
        - "Quels sont les points forts du CV de Cyril ?"
        - "Analyse les candidatures de Cyril par secteur"
        """)
        
        # Boutons pour questions rapides
        st.markdown("**🚀 Questions rapides :**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("👨‍💼 Profil de Cyril"):
                st.session_state.user_question = "Qui est Cyril Sauret et quel est son profil professionnel ?"
                st.rerun()
                
            if st.button("🏢 Entreprises ciblées"):
                st.session_state.user_question = "À quelles entreprises Cyril Sauret a-t-il postulé ?"
                st.rerun()
        
        with col2:
            if st.button("💻 Compétences techniques"):
                st.session_state.user_question = "Quelles sont les compétences techniques de Cyril Sauret ?"
                st.rerun()
                
            if st.button("📈 Analyse complète"):
                st.session_state.user_question = "Fais une analyse complète du profil et des candidatures de Cyril Sauret"
                st.rerun()

def _test_ollama_connection(ollama_url: str) -> None:
    """Teste la connexion avec Ollama."""
    try:
        import requests
        
        # Tester la disponibilité d'Ollama
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        
        if response.status_code == 200:
            models = response.json().get('models', [])
            if models:
                st.success(f"✅ Ollama connecté ! Modèles disponibles: {len(models)}")
                
                # Afficher les modèles Mistral disponibles
                mistral_models = [m['name'] for m in models if 'mistral' in m['name'].lower()]
                if mistral_models:
                    st.info(f"🤖 Modèles Mistral: {', '.join(mistral_models)}")
                else:
                    st.warning("⚠️ Aucun modèle Mistral trouvé. Exécutez: `ollama pull mistral:7b`")
            else:
                st.warning("⚠️ Ollama connecté mais aucun modèle installé")
        else:
            st.error(f"❌ Erreur Ollama: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        try:
            st.error("❌ Impossible de se connecter à Ollama. Vérifiez qu'il est démarré.")
            st.info("💡 Démarrez Ollama avec: `ollama serve`")
        except:
            print("❌ Impossible de se connecter à Ollama. Vérifiez qu'il est démarré.")
    except ImportError:
        try:
            st.error("❌ Module 'requests' requis")
        except:
            print("❌ Module 'requests' requis")
    except Exception as e:
        try:
            st.error(f"❌ Erreur test Ollama: {str(e)}")
        except:
            print(f"❌ Erreur test Ollama: {str(e)}")

def _run_database_diagnostic(vector_db) -> None:
    """Exécute un diagnostic de la base vectorielle."""
    
    st.markdown("### 🔧 Diagnostic de la base vectorielle")
    
    try:
        # Statistiques générales
        total_docs = len(vector_db.documents) if hasattr(vector_db, 'documents') else 0
        st.info(f"📊 **Total documents :** {total_docs}")
        
        if total_docs == 0:
            st.error("❌ Base vectorielle vide !")
            return
        
        # Analyser les métadonnées
        sources = set()
        categories = set()
        projects = set()
        text_lengths = []
        
        for doc in vector_db.documents[:10]:  # Examiner les 10 premiers
            metadata = doc.get('metadata', {})
            text = doc.get('text', '')
            
            sources.add(metadata.get('source', 'N/A'))
            categories.add(metadata.get('category', 'N/A'))
            projects.add(metadata.get('project', 'N/A'))
            text_lengths.append(len(text))
        
        st.info(f"📁 **Sources uniques (échantillon) :** {len(sources)}")
        st.info(f"🏷️ **Catégories :** {len(categories)}")
        st.info(f"🎯 **Projets :** {len(projects)}")
        
        # Chercher spécifiquement Cyril Sauret
        st.markdown("### 🔍 Test de recherche 'Cyril Sauret'")
        
        cyril_docs = vector_db.search("Cyril Sauret", top_k=5)
        st.info(f"📄 **Documents trouvés pour 'Cyril Sauret' :** {len(cyril_docs)}")
        
        if cyril_docs:
            for i, doc in enumerate(cyril_docs):
                metadata = doc.get('metadata', {})
                text = doc.get('text', '')[:200]
                source = metadata.get('source', 'N/A')
                st.success(f"✅ **Doc {i+1} :** {source}")
                st.text(f"Contenu: {text}...")
        else:
            # Tests avec d'autres mots-clés
            st.warning("❌ Aucun document trouvé pour 'Cyril Sauret'")
            
            test_keywords = ["Cyril", "Sauret", "CV", "développeur", "compétences"]
            
            for keyword in test_keywords:
                test_docs = vector_db.search(keyword, top_k=3)
                if test_docs:
                    st.info(f"✅ **'{keyword}' :** {len(test_docs)} documents")
                    # Afficher le premier résultat
                    first_doc = test_docs[0]
                    text_preview = first_doc.get('text', '')[:100]
                    source = first_doc.get('metadata', {}).get('source', 'N/A')
                    st.text(f"Exemple: {source} - {text_preview}...")
                else:
                    st.warning(f"❌ **'{keyword}' :** Aucun document")
        
        # Recommandations
        st.markdown("### 💡 Recommandations")
        
        if len(cyril_docs) == 0:
            st.error("🔄 **Problème identifié :** La recherche vectorielle ne trouve pas les documents sur Cyril Sauret")
            st.info("🛠️ **Solutions possibles :**")
            st.info("1. Relancer le traitement par lots pour réindexer")
            st.info("2. Vérifier l'encodage des documents")
            st.info("3. Nettoyer et recréer la base vectorielle")
        else:
            st.success("✅ La base semble fonctionnelle")
            
    except Exception as e:
        st.error(f"❌ Erreur diagnostic : {str(e)}")

def _analyze_project_existence(question: str, relevant_docs: List[Dict]) -> Optional[str]:
    """Analyse si la question porte sur l'existence d'un projet et génère une réponse intelligente."""
    
    import re
    import os
    
    # Détecter les questions sur l'existence de projets
    existence_patterns = [
        r'(existe|connais|as-tu|avez-vous).*projet\s+([A-Z]\d{3})',
        r'projet\s+([A-Z]\d{3}).*existe',
        r'connais.*([A-Z]\d{3})',
        r'le projet\s+([A-Z]\d{3})',
        r'(as-tu|avez-vous).*infos?.*([A-Z]\d{3})',
        r'(des|les)\s+infos?.*([A-Z]\d{3})',
        r'([A-Z]\d{3}).*existe'
    ]
    
    question_lower = question.lower()
    project_code = None
    
    # Chercher le code de projet dans la question
    for pattern in existence_patterns:
        match = re.search(pattern, question, re.IGNORECASE)
        if match:
            # Prendre le dernier groupe qui contient le code du projet
            project_code = match.groups()[-1].upper()
            break
    
    if not project_code:
        return None
    
    # Analyser les documents trouvés
    if not relevant_docs:
        return f"❌ **Non, le projet {project_code} n'existe pas** dans ma base de données.\n\nAucun document trouvé pour ce projet."
    
    # Analyser les sources consultées
    sources_found = []
    project_metadata = {}
    
    for doc in relevant_docs:
        metadata = doc.get('metadata', {})
        source = metadata.get('source', '')
        
        # Si le nom de fichier/chemin contient le code du projet
        if project_code in source.upper():
            sources_found.append(os.path.basename(source))
            
            # Extraire les métadonnées du projet
            if not project_metadata:
                project_metadata = {
                    'entreprise': metadata.get('enterprise', metadata.get('company', 'N/A')),
                    'titre': metadata.get('title', 'N/A'),
                    'description': metadata.get('description', 'N/A'),
                    'statut': metadata.get('status', 'N/A'),
                    'date': metadata.get('date', 'N/A'),
                    'lieu': metadata.get('location', 'N/A'),
                    'contact': metadata.get('contact', 'N/A'),
                }
    
    if not sources_found:
        return None  # Laisser Mistral traiter normalement
    
    # Générer la réponse d'existence
    response = f"✅ **Oui, le projet {project_code} existe !** J'ai trouvé des informations à son sujet.\n\n"
    
    # Informations du projet si disponibles
    if any(v != 'N/A' and v for v in project_metadata.values()):
        response += "📋 **INFORMATIONS DU PROJET :**\n"
        if project_metadata['entreprise'] != 'N/A':
            response += f"• **Entreprise :** {project_metadata['entreprise']}\n"
        if project_metadata['titre'] != 'N/A':
            response += f"• **Poste :** {project_metadata['titre']}\n"
        if project_metadata['lieu'] != 'N/A':
            response += f"• **Lieu :** {project_metadata['lieu']}\n"
        if project_metadata['statut'] != 'N/A':
            response += f"• **Statut :** {project_metadata['statut']}\n"
        if project_metadata['date'] != 'N/A':
            response += f"• **Date :** {project_metadata['date']}\n"
        response += "\n"
    
    # Documents trouvés
    response += f"📄 **DOCUMENTS DISPONIBLES :** ({len(sources_found)})\n"
    for source in sources_found:
        response += f"• {source}\n"
    
    # Contenu disponible
    content_preview = ""
    for doc in relevant_docs[:2]:  # Premiers 2 documents
        text = doc.get('text', '')
        if text and len(text.strip()) > 50:
            preview = text.strip()[:200].replace('\n', ' ')
            content_preview += f"📝 **Extrait :** {preview}...\n\n"
    
    if content_preview:
        response += f"\n{content_preview}"
    
    response += f"\n💡 **Le projet {project_code} est donc bien référencé dans ma base de données avec ces documents associés.**"
    
    return response

def _analyze_list_request(question: str, relevant_docs: List[Dict]) -> Optional[str]:
    """Analyse les questions de type liste et génère une réponse appropriée pour les candidatures."""
    
    import re
    import os
    
    # Patterns spécialisés pour les candidatures et recherche d'emploi
    list_patterns = [
        # Entreprises et candidatures
        (r'(liste|énumère|cite|quelles?) .*entreprises?.*(postul|candidat|contact)', 'entreprises'),
        (r'(où|quelles entreprises).*(j\'ai|ai).*(postul|candidat)', 'entreprises'),
        (r'(liste|énumère|cite).*(candidatures|postulations|demandes)', 'candidatures'),
        
        # Candidatures en cours spécifiquement
        (r'(candidatures?).*(en cours|actuelles?|actives?)', 'candidatures_en_cours'),
        (r'(quelles? sont mes).*(candidatures?).*(en cours)', 'candidatures_en_cours'),
        (r'(suivi|status|état).*(candidatures?)', 'candidatures_en_cours'),
        
        # Postes et emplois
        (r'(liste|énumère|cite|quels?) .*postes?.*(demandé|postul|candidat)', 'postes'),
        (r'(liste|énumère|cite|quels?) .*emplois?.*(cherch|postul|candidat)', 'postes'),
        (r'(quels? types? de).*(postes?|emplois?|métiers?)', 'postes'),
        
        # Compétences et technologies - distinguer "mes" compétences
        (r'(mes|ma|mon).*(compétences|technologies|savoir.faire)', 'mes_competences'),
        (r'(liste|énumère|cite|quelles?) .*compétences', 'competences'),
        (r'(liste|énumère|cite|quelles?) .*technologies', 'technologies'),
        
        # Projets
        (r'(liste|énumère|cite|quels?) .*projets', 'projets'),
        (r'(quels? projets).*(réalis|fait|participé)', 'projets'),
        
        # Documents généraux
        (r'(liste|énumère|cite|quels?) .*documents', 'documents')
    ]
    
    question_lower = question.lower()
    list_type = None
    
    # Détecter le type de liste demandée
    for pattern, category in list_patterns:
        if re.search(pattern, question_lower, re.IGNORECASE):
            list_type = category
            break
    
    if not list_type:
        return None  # Pas une question de liste reconnue
    
    if not relevant_docs:
        return f"❌ Aucun document pertinent trouvé pour générer la liste de {list_type}."
    
    st.info(f"🔍 Détection: Question de liste type '{list_type}'")
    
    # Extraction spécialisée selon le type de liste
    if list_type == 'entreprises':
        # Pour les entreprises, on a besoin de TOUS les documents de candidature
        # Pas seulement ceux retournés par la recherche vectorielle
        st.info("🔍 Recherche exhaustive de toutes les candidatures...")
        return _extract_company_list_exhaustive()
    elif list_type == 'candidatures_en_cours':
        return _extract_ongoing_applications(relevant_docs)
    elif list_type == 'postes':
        return _extract_job_list(relevant_docs)
    elif list_type == 'mes_competences':
        return _extract_skills_list(relevant_docs)  # La fonction gère déjà la distinction
    elif list_type == 'competences' or list_type == 'technologies':
        return _extract_skills_list(relevant_docs)
    elif list_type == 'projets':
        return _extract_project_list(relevant_docs)
    elif list_type == 'candidatures':
        return _extract_application_list(relevant_docs)
    elif list_type == 'documents':
        return _extract_document_list(relevant_docs)
    else:
        return _extract_generic_list(relevant_docs)

def _extract_company_list(relevant_docs: List[Dict]) -> str:
    """Extrait la liste complète des entreprises depuis les documents.
    
    LOGIQUE D'EXTRACTION OPTIMISÉE:
    1. Priorité: champs company/enterprise (métadonnées dédiées)
    2. Fallback: champ author (contient l'entreprise des fichiers .data.json)
    3. Puis: extraction depuis les tags, contenu, noms de fichiers
    4. L'objectif est d'utiliser en PREMIER le champ entreprise du .data.json
    """
    
    companies = {}  # Utiliser dict pour éviter les doublons tout en gardant les détails
    
    for doc in relevant_docs:
        metadata = doc.get('metadata', {})
        source = metadata.get('source', '')
        content = doc.get('content', doc.get('text', ''))
        
        # Extraire entreprise depuis les métadonnées - ORDRE OPTIMISÉ
        # 1. Priorité au champ 'entreprise' (directement issu du .data.json)
        company_name = metadata.get('entreprise', '')
        # 2. Si pas trouvé, chercher dans 'company' puis 'enterprise' (compatibilité)
        if not company_name or company_name == 'N/A':
            company_name = metadata.get('company', metadata.get('enterprise', ''))
        project = metadata.get('project', '')
        description = metadata.get('description', '')
        todo = metadata.get('todo', '')
        
        # 3. NOUVEAU: Si toujours pas trouvé, utiliser la fonction helper pour extraire depuis le code projet
        if not company_name or company_name == 'N/A':
            company_name = _extract_company_from_project_code(source, content)
        
        # 4. Extraire entreprise depuis tags si pas dans métadonnées directes
        if not company_name or company_name == 'N/A':
            tags = metadata.get('tags', '')
            if tags:
                tag_list = [tag.strip() for tag in tags.split(',')]
                for tag in tag_list:
                    if (len(tag) > 2 and 
                        not tag.lower() in ['annonce', 'cv', 'todo', 'new', 'formation', 'candidature', 'presentation', 'cyrilsauret', 'cyril', 'sauret'] and
                        not tag.startswith('maturité-') and
                        not tag.lower() in ['gpt-summary', 'competences', 'python', 'react', 'javascript', 'pdf', 'doc', 'docx']):
                        company_name = tag
                        break
        
        # 5. Chercher entreprise dans le contenu si toujours pas trouvée
        if not company_name or company_name == 'N/A':
            import re
            # Chercher patterns d'entreprises dans le contenu - patterns améliorés
            enterprise_patterns = [
                r'entreprise[:\s]+([A-Z][A-Za-z\s&\-]+?)(?:\s|,|\.|$)',
                r'société[:\s]+([A-Z][A-Za-z\s&\-]+?)(?:\s|,|\.|$)',
                r'chez[:\s]+([A-Z][A-Za-z\s&\-]+?)(?:\s|,|\.|$)',
                r'([A-Z][A-Za-z\s&\-]+?)\s+recrute',
                r'Poste.*?chez[:\s]+([A-Z][A-Za-z\s&\-]+?)(?:\s|,|\.|$)',
                r'candidature.*?chez\s+([A-Z][A-Za-z\s&\-]+?)(?:\s|,|\.|$)',
                r'candidature.*?entreprise\s+([A-Z][A-Za-z\s&\-]+?)(?:\s|,|\.|$)',
                r'lettre.*?motivation.*?([A-Z][A-Za-z\s&\-]+?)(?:\s|,|\.|$)',
                r'postul.*?chez\s+([A-Z][A-Za-z\s&\-]+?)(?:\s|,|\.|$)'
            ]
            
            for pattern in enterprise_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    potential_name = matches[0].strip()
                    # Filtrer les faux positifs
                    if (len(potential_name) > 3 and 
                        not potential_name.lower() in ['un', 'une', 'le', 'la', 'les', 'cette', 'cette entreprise', 'votre', 'notre', 'mon', 'ma', 'mes'] and
                        not potential_name.lower().startswith('cyril')):
                        company_name = potential_name
                        break
        
        # 6. NOUVEAU: Pour les lettres de motivation (LM), analyser plus finement
        if (not company_name or company_name == 'N/A') and '_lm_' in source.lower():
            # Pour les LM, chercher dans les premières lignes qui contiennent souvent l'entreprise
            content_lines = content.split('\n')[:10]  # Premières 10 lignes
            content_start = ' '.join(content_lines).lower()
            
            # Patterns spécifiques aux lettres de motivation
            lm_patterns = [
                r'madame,?\s*monsieur,?\s*([A-Za-z\s&\-]+?)(?:\s|,|\.|$)',
                r'candidature.*?poste.*?([A-Z][A-Za-z\s&\-]+?)(?:\s|,|\.|$)',
                r'intéressé.*?par.*?([A-Z][A-Za-z\s&\-]+?)(?:\s|,|\.|$)'
            ]
            
            for pattern in lm_patterns:
                matches = re.findall(pattern, content_start, re.IGNORECASE)
                if matches:
                    potential_name = matches[0].strip()
                    if len(potential_name) > 3:
                        company_name = potential_name
                        break
        
        if company_name and company_name != 'N/A' and len(company_name) > 2:
            company_key = company_name
            
            if company_key not in companies:
                companies[company_key] = {
                    'nom': company_name,
                    'postes': [],
                    'statut_candidature': 'Non défini',
                    'etape_actuelle': '',
                    'sources': [],
                    'dates': [],
                    'projets': [],
                    'details_todo': todo
                }
            
            # Analyser le statut détaillé depuis le champ todo
            if todo:
                companies[company_key]['details_todo'] = todo
                
                # Déterminer le statut de candidature
                if 'repondue' in todo.lower():
                    companies[company_key]['statut_candidature'] = '📬 Candidature répondue'
                elif 'etape' in todo.lower():
                    # Analyser les étapes
                    if 'etape' in todo.lower() and '1' in todo:
                        if '?' in todo:
                            companies[company_key]['etape_actuelle'] = '📞 En attente appel téléphonique'
                        elif 'refus' in todo.lower():
                            companies[company_key]['etape_actuelle'] = '❌ Refus après étape 1'
                        else:
                            companies[company_key]['etape_actuelle'] = '✅ Appel téléphonique réalisé'
                    
                    elif 'etape' in todo.lower() and '2' in todo:
                        if '?' in todo:
                            companies[company_key]['etape_actuelle'] = '🤝 En attente entretien RH'
                        elif 'refus' in todo.lower():
                            companies[company_key]['etape_actuelle'] = '❌ Refus après entretien RH'
                        else:
                            companies[company_key]['etape_actuelle'] = '✅ Entretien RH réalisé'
                    
                    elif 'etape' in todo.lower() and '3' in todo:
                        if '?' in todo:
                            companies[company_key]['etape_actuelle'] = '💻 En attente entretien technique'
                        elif 'refus' in todo.lower():
                            companies[company_key]['etape_actuelle'] = '❌ Refus après entretien technique'
                        else:
                            companies[company_key]['etape_actuelle'] = '✅ Entretien technique réalisé'
                else:
                    companies[company_key]['statut_candidature'] = '📤 Candidature envoyée'
            else:
                # NOUVEAU: Si pas de todo, deviner le statut depuis le type de document
                source_lower = source.lower()
                if '_lm_' in source_lower or 'lettre' in source_lower:
                    companies[company_key]['statut_candidature'] = '📝 Lettre de motivation rédigée'
                elif '_cv_' in source_lower and company_name.lower() in source_lower:
                    companies[company_key]['statut_candidature'] = '📋 CV adapté pour l\'entreprise'
                elif any(code in source_lower for code in ['m401', 'm402', 'm403', 'm404', 'm405', 'm595', 'm596', 'm587']):
                    companies[company_key]['statut_candidature'] = '📁 Dossier de candidature constitué'
                else:
                    companies[company_key]['statut_candidature'] = '📤 Candidature en cours'
            
            # Ajouter informations complémentaires
            if source:
                source_name = os.path.basename(source)
                if source_name not in companies[company_key]['sources']:
                    companies[company_key]['sources'].append(source_name)
            
            if project and project not in companies[company_key]['projets']:
                companies[company_key]['projets'].append(project)
            
            title = metadata.get('title', '')
            if title and 'cv' not in title.lower() and title not in companies[company_key]['postes']:
                companies[company_key]['postes'].append(title)
            
            date = metadata.get('date', '')
            if date and date != 'N/A' and date not in companies[company_key]['dates']:
                companies[company_key]['dates'].append(date)
    
    if not companies:
        return "❌ Aucune entreprise trouvée dans les documents consultés."
    
    # Construire la réponse formatée complète
    response = f"🏢 **LISTE COMPLÈTE DES ENTREPRISES** ({len(companies)} trouvées)\n\n"
    
    for i, (company_key, details) in enumerate(sorted(companies.items()), 1):
        response += f"**{i}. {details['nom']}**\n"
        
        # Statut de candidature
        response += f"   📊 Statut: {details['statut_candidature']}\n"
        
        # Étape actuelle si définie
        if details['etape_actuelle']:
            response += f"   🎯 Étape: {details['etape_actuelle']}\n"
        
        # Postes candidatés
        if details['postes']:
            unique_postes = list(set(details['postes']))
            response += f"   � Postes: {', '.join(unique_postes)}\n"
        
        # Dernière activité
        if details['dates']:
            latest_date = max(details['dates']) if details['dates'] else ''
            if latest_date:
                response += f"   📅 Dernière activité: {latest_date}\n"
        
        # Projets associés
        if details['projets']:
            unique_projets = list(set(details['projets']))
            response += f"   🗂️ Projets: {', '.join(unique_projets)}\n"
        
        # Nombre de documents
        if details['sources']:
            response += f"   📄 Documents: {len(details['sources'])} fichiers\n"
        
        # Détails todo si disponible
        if details['details_todo'] and details['details_todo'].strip():
            response += f"   � Todo: {details['details_todo'][:50]}...\n"
        
        response += "\n"
    
    return response.strip()

def _extract_company_list_exhaustive() -> str:
    """Extraction exhaustive des entreprises en cherchant dans toute la base vectorielle."""
    
    try:
        # Accès à la base vectorielle depuis la session state
        vector_db = st.session_state.get('vector_db')
        if not vector_db:
            return "❌ Erreur: Base vectorielle non initialisée dans la session."
        
        # Recherche exhaustive avec plusieurs termes pour capturer toutes les candidatures
        search_terms = [
            "candidature", "entreprise", "annonce", "todo", "etape", "repondue",
            "appel", "entretien", "refus", "validation", "hr", "rh", "poste"
        ]
        
        st.info(f"🔍 Recherche exhaustive avec {len(search_terms)} termes...")
        all_docs = set()
        
        # Recherche avec chaque terme
        for term in search_terms:
            try:
                results = vector_db.search(term, top_k=200)  # Plus large
                all_docs.update(results)
                st.info(f"   📑 Terme '{term}': {len(results)} documents")
            except Exception as e:
                st.warning(f"   ⚠️ Erreur recherche '{term}': {e}")
                continue
        
        st.success(f"📄 Total documents uniques collectés: {len(all_docs)}")
        
        # Convertir en format Dict pour _extract_company_list
        docs_as_dict = []
        for doc in all_docs:
            if isinstance(doc, dict):
                # Format déjà dict
                doc_dict = {
                    'metadata': doc.get('metadata', {}),
                    'content': doc.get('content', doc.get('text', '')),
                    'text': doc.get('text', doc.get('content', ''))
                }
            else:
                # Format objet avec attributs
                doc_dict = {
                    'metadata': getattr(doc, 'metadata', {}) if hasattr(doc, 'metadata') else {},
                    'content': getattr(doc, 'page_content', getattr(doc, 'text', str(doc))) if hasattr(doc, 'page_content') else getattr(doc, 'text', str(doc)),
                    'text': getattr(doc, 'page_content', getattr(doc, 'text', str(doc))) if hasattr(doc, 'page_content') else getattr(doc, 'text', str(doc))
                }
            docs_as_dict.append(doc_dict)
        
        # Filtrer pour ne garder que les candidatures avant d'appeler _extract_company_list
        candidature_docs = []
        for doc_dict in docs_as_dict:
            metadata = doc_dict.get('metadata', {})
            todo = metadata.get('todo', '')
            tags = metadata.get('tags', '')
            content = doc_dict.get('content', '')
            source = metadata.get('source', '')
            title = metadata.get('title', '')
            
            # Vérifier si c'est une candidature avec logique élargie
            is_application = False
            detection_reason = ""
            
            # Vérification 1: Le todo contient des mots-clés de candidature
            if todo:
                todo_lower = todo.lower()
                candidature_keywords = ['repondue', 'etape', 'appel', 'entretien', 'refus', 'validation', 'hr', 'rh', 'candidature', 'postul']
                if any(keyword in todo_lower for keyword in candidature_keywords):
                    is_application = True
                    detection_reason = f"Todo: {todo}"
            
            # Vérification 2: Les tags contiennent "candidature"
            if not is_application and tags:
                if 'candidature' in tags.lower():
                    is_application = True
                    detection_reason = f"Tags: {tags}"
            
            # Vérification 3: Le contenu mentionne explicitement une candidature
            if not is_application and content:
                content_lower = content.lower()
                if ('candidature' in content_lower or 'postulé' in content_lower or 
                    'cv envoyé' in content_lower or 'lettre de motivation' in content_lower or
                    'postuler' in content_lower or 'demande d\'emploi' in content_lower):
                    is_application = True
                    detection_reason = "Contenu candidature"
            
            # Vérification 4: NOUVEAU - Analyse du nom de fichier et des patterns
            if not is_application and source:
                source_lower = source.lower()
                # Lettres de motivation
                if any(pattern in source_lower for pattern in ['_lm_', 'lettre', 'motivation', 'candidature']):
                    is_application = True
                    detection_reason = f"Fichier LM: {source}"
                # Projets avec codes (M###, A###) qui sont souvent des candidatures
                elif re.search(r'(?:^|_|-)[MA]\d{3}(?:_|-|$)', os.path.basename(source).upper()):  # Codes M### ou A### avec séparateurs
                    is_application = True
                    detection_reason = f"Projet candidature: {source}"
                # CV avec entreprises spécifiques (pas les CV génériques)
                elif '_cv_' in source_lower and not any(generic in source_lower for generic in ['cyrilsauret', 'general', 'template']):
                    is_application = True
                    detection_reason = f"CV spécifique: {source}"
            
            # Vérification 5: NOUVEAU - Analyse du titre
            if not is_application and title:
                title_lower = title.lower()
                if any(pattern in title_lower for pattern in ['candidature', 'postul', 'demande', 'lettre de motivation', 'cv pour']):
                    is_application = True
                    detection_reason = f"Titre: {title}"
            
            # Vérification 6: NOUVEAU - Détection d'entreprises dans le nom de fichier
            if not is_application and source:
                # Recherche générique d'entreprises dans le nom de fichier SEULEMENT (pas le chemin)
                filename_only = os.path.basename(source)
                
                # Patterns génériques pour détecter des noms d'entreprises dans le nom de fichier
                enterprise_patterns = [
                    r'_([A-Z][a-zA-Z\s&\-]+?)_',  # Entre underscores
                    r'-([A-Z][a-zA-Z\s&\-]+?)-',  # Entre tirets
                ]
                
                for pattern in enterprise_patterns:
                    matches = re.findall(pattern, filename_only)
                    for match in matches:
                        # Filtrer pour garder seulement ce qui ressemble à des entreprises
                        if (len(match) > 3 and 
                            not match.lower() in ['cv', 'lm', 'lettre', 'motivation', 'data', 'new', 'doc', 'pdf', 'actions', 'cyril', 'sauret', 'entreprendre'] and
                            not re.match(r'^[A-Z]\d+$', match) and  # Éviter les codes projets
                            any(c.isupper() for c in match)):  # Au moins une majuscule
                            is_application = True
                            detection_reason = f"Entreprise détectée: {match}"
                            break
                    if is_application:
                        break
            
            if is_application:
                candidature_docs.append(doc_dict)
                st.info(f"✅ Candidature détectée: {detection_reason}")
            else:
                # Debug pour comprendre pourquoi le document est rejeté
                st.warning(f"❌ Document rejeté: {os.path.basename(source)} - Aucun critère candidature")
        
        st.info(f"✅ Documents candidature filtrés: {len(candidature_docs)}")
        
        if not candidature_docs:
            return "❌ Aucun document de candidature trouvé dans la base vectorielle."
        
        # Maintenant utiliser la fonction existante avec les docs filtrés
        return _extract_company_list(candidature_docs)
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"❌ Erreur lors de l'extraction exhaustive des entreprises: {str(e)}\n\nDétails:\n```\n{error_details}\n```"

def _extract_company_from_project_code(source: str, content: str = "") -> str:
    """Extrait le nom d'entreprise depuis le code projet et le contenu de manière générique."""
    
    # Patterns génériques pour extraire les entreprises depuis les noms de fichiers
    source_lower = source.lower()
    
    # 1. Chercher des patterns d'entreprises dans le nom du fichier
    # Pattern: tout ce qui ressemble à un nom d'entreprise entre underscores ou tirets
    filename_patterns = [
        r'_([A-Z][a-zA-Z\s&\-]+?)_',  # Entre underscores
        r'-([A-Z][a-zA-Z\s&\-]+?)-',  # Entre tirets
        r'\\([A-Z][a-zA-Z\s&\-]+?)\\', # Entre slashes (chemins)
        r'/([A-Z][a-zA-Z\s&\-]+?)/',   # Entre slashes unix
    ]
    
    for pattern in filename_patterns:
        matches = re.findall(pattern, source)
        for match in matches:
            # Filtrer les faux positifs courants
            if (len(match) > 2 and 
                not match.lower() in ['cv', 'lm', 'lettre', 'motivation', 'data', 'new', 'doc', 'pdf', 'actions'] and
                not match.lower().startswith('cyril') and
                not re.match(r'^[A-Z]\d+$', match)):  # Éviter les codes projets
                return match.strip()
    
    # 2. Extraire depuis le contenu avec des patterns génériques
    if content and len(content.strip()) > 50:
        content_lines = content.split('\n')[:15]  # Premières lignes
        content_start = ' '.join(content_lines)
        
        # Patterns génériques pour entreprises dans le contenu
        content_patterns = [
            r'entreprise[:\s]+([A-Z][a-zA-Z\s&\-\.]+?)(?:\s|,|\.|$|\n)',
            r'société[:\s]+([A-Z][a-zA-Z\s&\-\.]+?)(?:\s|,|\.|$|\n)',
            r'chez[:\s]+([A-Z][a-zA-Z\s&\-\.]+?)(?:\s|,|\.|$|\n)',
            r'([A-Z][a-zA-Z\s&\-\.]+?)\s+(?:recrute|embauche)',
            r'candidature.*?(?:chez|pour)\s+([A-Z][a-zA-Z\s&\-\.]+?)(?:\s|,|\.|$|\n)',
            r'postul.*?(?:chez|pour)\s+([A-Z][a-zA-Z\s&\-\.]+?)(?:\s|,|\.|$|\n)',
            r'Madame,?\s*Monsieur,?\s*([A-Z][a-zA-Z\s&\-\.]+?)(?:\s|,|\.|$|\n)',
            r'À l\'attention de[:\s]+([A-Z][a-zA-Z\s&\-\.]+?)(?:\s|,|\.|$|\n)'
        ]
        
        for pattern in content_patterns:
            matches = re.findall(pattern, content_start, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                match = match.strip()
                # Filtrer les faux positifs
                if (len(match) > 3 and 
                    not match.lower() in ['votre', 'notre', 'cette', 'une', 'le', 'la', 'les', 'mon', 'ma', 'mes', 'son', 'sa', 'ses'] and
                    not match.lower().startswith('cyril') and
                    not match.lower().endswith('sauret') and
                    not re.match(r'^[A-Z]\d+$', match)):  # Éviter les codes
                    return match
    
    return ""

# ...existing code...
