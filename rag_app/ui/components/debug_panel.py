"""
Composant de panneau de debug pour afficher les logs système
"""

import streamlit as st
import pandas as pd
from typing import List, Dict

def show_debug_panel(page_context: str = "default"):
    """Affiche le panneau de debug en bas de l'écran"""
    
    # Initialiser les logs s'ils n'existent pas
    if 'debug_logs' not in st.session_state:
        st.session_state.debug_logs = []
    
    # Separator visual avec style amélioré
    st.markdown("---")
    st.markdown(
        """
        <div style="
            background: linear-gradient(90deg, #f0f2f6, #ffffff, #f0f2f6);
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            border: 1px solid #e1e5e9;
        ">
        """, 
        unsafe_allow_html=True
    )
    
    # Header du panneau de debug - utilisation de toute la largeur
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown("### 🔧 Zone de Debug & Logs Système")
    with col2:
        # Bouton pour effacer les logs avec clé unique
        if st.button("🗑️ Effacer", key=f"clear_debug_logs_{page_context}", help="Effacer tous les logs"):
            st.session_state.debug_logs = []
            st.experimental_rerun()
    with col3:
        # Toggle pour masquer/afficher avec clé unique
        show_debug = st.checkbox("Détails", value=False, key=f"show_debug_details_{page_context}", help="Afficher/masquer les détails")
    
    # Statistiques toujours visibles - sur toute la largeur
    logs = st.session_state.debug_logs
    
    # Si pas de logs, afficher un message informatif
    if not logs:
        st.info("📝 Aucun log système pour le moment. Les messages de debug apparaîtront ici automatiquement lors du traitement des fichiers.")
        st.markdown("</div>", unsafe_allow_html=True)
        return
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📊 Total", len(logs))
    with col2:
        errors = len([l for l in logs if l['level'] == 'ERROR'])
        st.metric("❌ Erreurs", errors, delta=f"-{errors}" if errors > 0 else "0")
    with col3:
        warnings = len([l for l in logs if l['level'] == 'WARNING'])
        st.metric("⚠️ Avertissements", warnings, delta=f"-{warnings}" if warnings > 0 else "0")
    with col4:
        infos = len([l for l in logs if l['level'] == 'INFO'])
        st.metric("ℹ️ Infos", infos)
    with col5:
        successes = len([l for l in logs if l['level'] == 'SUCCESS'])
        st.metric("✅ Succès", successes, delta=f"+{successes}" if successes > 0 else "0")
    
    if not show_debug:
        # Mode condensé - afficher juste le résumé des derniers logs
        if logs:
            last_logs = logs[-3:]  # 3 derniers logs
            st.markdown("**📋 Derniers événements:**")
            for log in reversed(last_logs):
                icon = {'ERROR': '❌', 'WARNING': '⚠️', 'INFO': 'ℹ️', 'SUCCESS': '✅'}.get(log['level'], '📝')
                st.caption(f"{log['timestamp']} | {icon} {log['level']} | {log['message'][:80]}...")
        
        st.markdown("</div>", unsafe_allow_html=True)
        return
    
    # Mode détaillé - Filtres sur toute la largeur
    st.markdown("#### 🔍 Filtres")
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        selected_levels = st.multiselect(
            "🏷️ Filtrer par niveau:",
            options=['ERROR', 'WARNING', 'INFO', 'SUCCESS'],
            default=['ERROR', 'WARNING'],
            key=f"debug_level_filter_{page_context}"
        )
    
    with col2:
        components = list(set([log['component'] for log in logs]))
        selected_components = st.multiselect(
            "📦 Filtrer par composant:",
            options=components,
            default=components,
            key=f"debug_component_filter_{page_context}"
        )
    
    with col3:
        max_entries = st.selectbox(
            "📄 Nombre d'entrées:",
            options=[10, 20, 50, 100],
            index=1,
            key=f"debug_max_entries_{page_context}"
        )
    
    # Filtrer les logs
    filtered_logs = [
        log for log in logs 
        if log['level'] in selected_levels and log['component'] in selected_components
    ]
    
    # Affichage des logs - container avec toute la largeur
    st.markdown("#### 📝 Messages de Debug")
    
    if filtered_logs:
        # Container avec style amélioré et toute la largeur
        st.markdown(
            """
            <div style="
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
                max-height: 400px;
                overflow-y: auto;
                width: 100%;
                margin: 10px 0;
            ">
            """, 
            unsafe_allow_html=True
        )
        
        # Afficher les derniers logs en premier
        recent_logs = list(reversed(filtered_logs[-max_entries:]))
        for i, log in enumerate(recent_logs):
            _render_log_entry(log, i)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Informations de navigation
        if len(filtered_logs) > max_entries:
            st.caption(f"Affichage des {max_entries} derniers logs sur {len(filtered_logs)} au total")
    else:
        st.info("🔍 Aucun log correspondant aux filtres sélectionnés.")
    
    # Fermer le container principal
    st.markdown("</div>", unsafe_allow_html=True)

def _render_log_entry(log: Dict, index: int = 0):
    """Rend une entrée de log avec le style approprié"""
    
    # Couleurs selon le niveau
    level_colors = {
        'ERROR': '❌',
        'WARNING': '⚠️', 
        'INFO': 'ℹ️',
        'SUCCESS': '✅'
    }
    
    level_styles = {
        'ERROR': 'background-color: #ffebee; border-left: 5px solid #f44336; border-radius: 4px;',
        'WARNING': 'background-color: #fff3e0; border-left: 5px solid #ff9800; border-radius: 4px;',
        'INFO': 'background-color: #e3f2fd; border-left: 5px solid #2196f3; border-radius: 4px;',
        'SUCCESS': 'background-color: #e8f5e8; border-left: 5px solid #4caf50; border-radius: 4px;'
    }
    
    icon = level_colors.get(log['level'], '📝')
    style = level_styles.get(log['level'], 'border-left: 5px solid #ccc; border-radius: 4px;')
    
    # Style alternant pour meilleure lisibilité
    bg_color = "#fafafa" if index % 2 == 0 else "#ffffff"
    
    # Affichage avec style amélioré et largeur complète
    st.markdown(
        f"""
        <div style="
            {style}
            background-color: {bg_color};
            padding: 12px 15px;
            margin: 6px 0;
            width: 100%;
            box-sizing: border-box;
            font-family: 'Source Code Pro', monospace;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 16px;">{icon}</span>
                    <strong style="color: #2c3e50; font-size: 12px;">{log['level']}</strong>
                    <span style="color: #7f8c8d; font-size: 11px;">•</span>
                    <span style="color: #3498db; font-size: 11px;">📦 {log['component']}</span>
                </div>
                <span style="color: #95a5a6; font-size: 11px; font-weight: normal;">
                    {log['timestamp']}
                </span>
            </div>
            <div style="
                color: #2c3e50; 
                font-size: 13px; 
                line-height: 1.4;
                word-wrap: break-word;
                max-width: 100%;
            ">
                {log['message']}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def add_debug_log(level: str, message: str, component: str = "system"):
    """Fonction utilitaire pour ajouter un log depuis n'importe où dans l'application"""
    if 'debug_logs' not in st.session_state:
        st.session_state.debug_logs = []
    
    import datetime
    log_entry = {
        'timestamp': datetime.datetime.now().strftime("%H:%M:%S"),
        'level': level,
        'component': component,
        'message': message
    }
    st.session_state.debug_logs.append(log_entry)
    
    # Limiter à 100 entrées
    if len(st.session_state.debug_logs) > 100:
        st.session_state.debug_logs = st.session_state.debug_logs[-100:]

# Fonctions de convenance
def debug_info(message: str, component: str = "app"):
    add_debug_log("INFO", message, component)

def debug_warning(message: str, component: str = "app"):
    add_debug_log("WARNING", message, component)

def debug_error(message: str, component: str = "app"):
    add_debug_log("ERROR", message, component)

def debug_success(message: str, component: str = "app"):
    add_debug_log("SUCCESS", message, component)
