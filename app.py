"""
Campaign Analyzer Dashboard
Main Streamlit application for analyzing LGM campaigns with AI
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime

from lgm_client import LGMClient, LGMAPIError, CampaignStats
from gemini_analyzer import GeminiAnalyzer, MockGeminiAnalyzer

# Page config
st.set_page_config(
    page_title="Campaign Analyzer | LGM + AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
    }
    .success-box {
        background-color: #d1fae5;
        border-left: 4px solid #10b981;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fef3c7;
        border-left: 4px solid #f59e0b;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #dbeafe;
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 1rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables"""
    if 'lgm_connected' not in st.session_state:
        st.session_state.lgm_connected = False
    if 'campaigns' not in st.session_state:
        st.session_state.campaigns = []
    if 'selected_campaigns' not in st.session_state:
        st.session_state.selected_campaigns = []
    if 'campaign_stats' not in st.session_state:
        st.session_state.campaign_stats = []
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None


def get_api_keys():
    """Get API keys from Streamlit secrets or user input"""
    lgm_key = None
    gemini_key = None
    
    # Try to get from secrets first
    try:
        lgm_key = st.secrets.get("LGM_API_KEY")
        gemini_key = st.secrets.get("GEMINI_API_KEY")
    except:
        pass
    
    return lgm_key, gemini_key


def render_sidebar():
    """Render the sidebar with configuration"""
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        
        # API Keys section
        st.markdown("### 🔑 API Keys")
        
        lgm_key_default, gemini_key_default = get_api_keys()
        
        lgm_api_key = st.text_input(
            "LGM API Key",
            value=lgm_key_default or "",
            type="password",
            help="Trouvez votre clé API dans LGM > Settings > Integrations & API"
        )
        
        gemini_api_key = st.text_input(
            "Gemini API Key",
            value=gemini_key_default or "",
            type="password",
            help="Créez une clé sur Google AI Studio"
        )
        
        # Test connection button
        if st.button("🔌 Tester la connexion LGM", use_container_width=True):
            if lgm_api_key:
                with st.spinner("Test de connexion..."):
                    client = LGMClient(lgm_api_key)
                    if client.test_connection():
                        st.success("✅ Connexion LGM réussie!")
                        st.session_state.lgm_connected = True
                    else:
                        st.error("❌ Échec de connexion. Vérifiez votre clé API.")
                        st.session_state.lgm_connected = False
            else:
                st.warning("Entrez votre clé API LGM")
        
        st.markdown("---")
        
        # Demo mode
        st.markdown("### 🎮 Mode Démo")
        demo_mode = st.checkbox(
            "Utiliser des données de démo",
            help="Testez le dashboard sans clé API"
        )
        
        st.markdown("---")
        
        # About section
        st.markdown("### ℹ️ À propos")
        st.markdown("""
        **Campaign Analyzer** analyse vos campagnes LGM avec l'IA pour :
        - 📊 Comparer les performances
        - 🎯 Identifier les patterns gagnants
        - 💡 Suggérer des optimisations
        - 🧪 Proposer des A/B tests
        """)
        
        return lgm_api_key, gemini_api_key, demo_mode


def get_demo_campaigns():
    """Return demo campaign data for testing"""
    return [
        CampaignStats(
            campaign_id="demo_1",
            campaign_name="Email > LinkedIn - CEO #1",
            total_leads=150,
            emails_sent=145,
            emails_opened=87,
            emails_clicked=23,
            emails_replied=12,
            linkedin_sent=120,
            linkedin_accepted=45,
            linkedin_replied=18,
            total_replies=30,
            total_conversions=5
        ),
        CampaignStats(
            campaign_id="demo_2",
            campaign_name="LinkedIn > Email - CMO #1",
            total_leads=120,
            emails_sent=95,
            emails_opened=62,
            emails_clicked=15,
            emails_replied=8,
            linkedin_sent=120,
            linkedin_accepted=52,
            linkedin_replied=22,
            total_replies=30,
            total_conversions=7
        ),
        CampaignStats(
            campaign_id="demo_3",
            campaign_name="Email Only - COO #1",
            total_leads=200,
            emails_sent=195,
            emails_opened=98,
            emails_clicked=28,
            emails_replied=15,
            linkedin_sent=0,
            linkedin_accepted=0,
            linkedin_replied=0,
            total_replies=15,
            total_conversions=3
        ),
        CampaignStats(
            campaign_id="demo_4",
            campaign_name="Multicanal - Voice Note",
            total_leads=80,
            emails_sent=75,
            emails_opened=52,
            emails_clicked=18,
            emails_replied=10,
            linkedin_sent=80,
            linkedin_accepted=48,
            linkedin_replied=28,
            total_replies=38,
            total_conversions=9
        ),
    ]


def get_demo_campaign_content():
    """Return demo campaign content"""
    return {
        "Email > LinkedIn - CEO #1": {
            "subject": "2 AM checkout breaks",
            "body": "Hi {{firstname}},\n\nIt's 2:30 AM. Your checkout breaks on mobile.\n\nWhen do you find out?...",
            "linkedin_1": "Thanks for connecting {{firstname}}. Your checkout can break at 2 AM..."
        },
        "LinkedIn > Email - CMO #1": {
            "subject": "{{firstName}} - 2 hours of lost revenue",
            "body": "Hey {{firstname}},\n\nQuick question: when was the last time you checked your store analytics at 3 AM?...",
            "linkedin_1": "Hey {{firstname}}, thanks for connecting. Just curious - when does your team stop checking..."
        },
        "Email Only - COO #1": {
            "subject": "Your ops team wastes time daily",
            "body": "Hi {{firstname}},\n\nI noticed {{companyName}} is scaling fast. Quick question...",
            "linkedin_1": None
        },
        "Multicanal - Voice Note": {
            "subject": "Quick voice note for {{firstName}}",
            "body": "Hi {{firstname}},\n\nI just sent you a voice note on LinkedIn...",
            "linkedin_1": "[Voice Note] Hey {{firstname}}, quick 30 second message for you..."
        }
    }


def stats_to_dataframe(stats_list: list[CampaignStats]) -> pd.DataFrame:
    """Convert CampaignStats list to DataFrame"""
    data = []
    for stat in stats_list:
        data.append({
            "Campagne": stat.campaign_name,
            "ID": stat.campaign_id,
            "Leads": stat.total_leads,
            "Emails envoyés": stat.emails_sent,
            "Emails ouverts": stat.emails_opened,
            "Open Rate": stat.open_rate,
            "Emails cliqués": stat.emails_clicked,
            "CTR": stat.click_rate,
            "Réponses Email": stat.emails_replied,
            "Reply Rate Email": stat.email_reply_rate,
            "LinkedIn envoyés": stat.linkedin_sent,
            "LinkedIn acceptés": stat.linkedin_accepted,
            "Acceptance Rate": stat.linkedin_acceptance_rate,
            "Réponses LinkedIn": stat.linkedin_replied,
            "Reply Rate LinkedIn": stat.linkedin_reply_rate,
            "Total Réponses": stat.total_replies,
            "Reply Rate Global": stat.overall_reply_rate,
            "Conversions": stat.total_conversions,
            "Conversion Rate": stat.conversion_rate
        })
    return pd.DataFrame(data)


def render_metrics_overview(df: pd.DataFrame):
    """Render the metrics overview section"""
    st.markdown("### 📊 Vue d'ensemble")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_leads = df["Leads"].sum()
        st.metric("Total Leads", f"{total_leads:,}")
    
    with col2:
        avg_open_rate = df["Open Rate"].mean()
        st.metric("Open Rate Moyen", f"{avg_open_rate:.1f}%")
    
    with col3:
        avg_reply_rate = df["Reply Rate Global"].mean()
        st.metric("Reply Rate Moyen", f"{avg_reply_rate:.1f}%")
    
    with col4:
        total_conversions = df["Conversions"].sum()
        st.metric("Total Conversions", f"{total_conversions:,}")
    
    with col5:
        avg_conversion = df["Conversion Rate"].mean()
        st.metric("Conversion Moyen", f"{avg_conversion:.1f}%")


def render_comparison_charts(df: pd.DataFrame):
    """Render comparison charts"""
    st.markdown("### 📈 Comparaison des campagnes")
    
    tab1, tab2, tab3 = st.tabs(["📧 Email", "💼 LinkedIn", "🎯 Global"])
    
    with tab1:
        # Email metrics comparison
        fig = make_subplots(rows=1, cols=2, subplot_titles=("Open Rate", "Reply Rate Email"))
        
        fig.add_trace(
            go.Bar(name="Open Rate", x=df["Campagne"], y=df["Open Rate"], marker_color="#3b82f6"),
            row=1, col=1
        )
        fig.add_trace(
            go.Bar(name="Reply Rate", x=df["Campagne"], y=df["Reply Rate Email"], marker_color="#10b981"),
            row=1, col=2
        )
        
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # LinkedIn metrics comparison
        fig = make_subplots(rows=1, cols=2, subplot_titles=("Acceptance Rate", "Reply Rate LinkedIn"))
        
        fig.add_trace(
            go.Bar(name="Acceptance", x=df["Campagne"], y=df["Acceptance Rate"], marker_color="#8b5cf6"),
            row=1, col=1
        )
        fig.add_trace(
            go.Bar(name="Reply Rate", x=df["Campagne"], y=df["Reply Rate LinkedIn"], marker_color="#f59e0b"),
            row=1, col=2
        )
        
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Global comparison radar chart
        categories = ["Open Rate", "Reply Rate Global", "Conversion Rate", "Acceptance Rate"]
        
        fig = go.Figure()
        
        colors = px.colors.qualitative.Set2
        for i, row in df.iterrows():
            fig.add_trace(go.Scatterpolar(
                r=[row["Open Rate"], row["Reply Rate Global"], row["Conversion Rate"] * 5, row["Acceptance Rate"]],
                theta=categories,
                fill='toself',
                name=row["Campagne"][:20] + "..." if len(row["Campagne"]) > 20 else row["Campagne"],
                line_color=colors[i % len(colors)]
            ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)


def render_ranking_table(df: pd.DataFrame):
    """Render the campaign ranking table"""
    st.markdown("### 🏆 Classement des campagnes")
    
    # Calculate a composite score
    df_ranked = df.copy()
    df_ranked["Score"] = (
        df_ranked["Open Rate"] * 0.2 +
        df_ranked["Reply Rate Global"] * 0.4 +
        df_ranked["Conversion Rate"] * 0.4
    ).round(2)
    
    df_ranked = df_ranked.sort_values("Score", ascending=False)
    df_ranked.insert(0, "Rang", range(1, len(df_ranked) + 1))
    
    # Style the dataframe
    display_cols = ["Rang", "Campagne", "Leads", "Open Rate", "Reply Rate Global", "Conversion Rate", "Score"]
    
    st.dataframe(
        df_ranked[display_cols].style.format({
            "Open Rate": "{:.1f}%",
            "Reply Rate Global": "{:.1f}%",
            "Conversion Rate": "{:.1f}%",
            "Score": "{:.2f}"
        }).background_gradient(subset=["Score"], cmap="Greens"),
        use_container_width=True,
        hide_index=True
    )


def render_ai_analysis(analyzer, stats_list: list[CampaignStats], campaign_content: dict):
    """Render the AI analysis section"""
    st.markdown("### 🤖 Analyse IA")
    
    # Prepare data for analysis
    campaigns_data = []
    for stat in stats_list:
        campaigns_data.append({
            "name": stat.campaign_name,
            "leads": stat.total_leads,
            "open_rate": stat.open_rate,
            "email_reply_rate": stat.email_reply_rate,
            "linkedin_acceptance_rate": stat.linkedin_acceptance_rate,
            "linkedin_reply_rate": stat.linkedin_reply_rate,
            "overall_reply_rate": stat.overall_reply_rate,
            "conversion_rate": stat.conversion_rate
        })
    
    analysis_tabs = st.tabs(["📊 Analyse", "⚔️ Comparaison", "🧪 Suggestions A/B", "✨ Générer variantes"])
    
    with analysis_tabs[0]:
        if st.button("🔍 Lancer l'analyse complète", key="analyze_btn"):
            with st.spinner("Analyse en cours avec Gemini..."):
                results = analyzer.analyze_campaigns(campaigns_data, campaign_content)
                st.session_state.analysis_results = results
        
        if st.session_state.analysis_results:
            render_analysis_results(st.session_state.analysis_results)
    
    with analysis_tabs[1]:
        if st.button("⚔️ Comparer les campagnes", key="compare_btn"):
            with st.spinner("Comparaison en cours..."):
                results = analyzer.compare_campaigns(campaigns_data, campaign_content)
                render_comparison_results(results)
    
    with analysis_tabs[2]:
        if st.button("🧪 Suggérer des A/B tests", key="suggest_btn"):
            with st.spinner("Génération des suggestions..."):
                results = analyzer.suggest_next_tests(campaigns_data, campaign_content)
                render_suggestions_results(results)
    
    with analysis_tabs[3]:
        st.markdown("Sélectionnez la campagne gagnante pour générer des variantes:")
        winner = st.selectbox(
            "Campagne de référence",
            options=[stat.campaign_name for stat in stats_list]
        )
        
        num_variants = st.slider("Nombre de variantes", 2, 5, 3)
        
        if st.button("✨ Générer des variantes", key="variants_btn"):
            winning_content = campaign_content.get(winner, {})
            with st.spinner("Génération des variantes..."):
                results = analyzer.generate_variants(winning_content, num_variants)
                render_variants_results(results)


def render_analysis_results(results: dict):
    """Render the analysis results"""
    if "error" in results:
        st.error(f"Erreur d'analyse: {results['error']}")
        if "raw_response" in results:
            with st.expander("Réponse brute"):
                st.text(results["raw_response"])
        return
    
    # Demo mode warning
    if "_note" in results:
        st.warning(results["_note"])
    
    # Global summary
    if "resume_global" in results:
        st.markdown("#### 📋 Résumé global")
        summary = results["resume_global"]
        col1, col2 = st.columns(2)
        with col1:
            st.success(f"🏆 **Meilleure campagne:** {summary.get('meilleure_campagne', 'N/A')}")
        with col2:
            st.error(f"📉 **À améliorer:** {summary.get('pire_campagne', 'N/A')}")
        st.info(f"📊 **Tendance:** {summary.get('tendance_generale', 'N/A')}")
    
    # Open rate analysis
    if "analyse_open_rate" in results:
        st.markdown("#### 📧 Analyse Open Rate")
        oar = results["analyse_open_rate"]
        st.markdown(f"**Moyenne:** {oar.get('moyenne', 'N/A')}")
        st.markdown(f"**Meilleur sujet:** `{oar.get('meilleur_sujet', 'N/A')}`")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("✅ **Patterns gagnants:**")
            for p in oar.get("patterns_gagnants", []):
                st.markdown(f"- {p}")
        with col2:
            st.markdown("❌ **Patterns perdants:**")
            for p in oar.get("patterns_perdants", []):
                st.markdown(f"- {p}")
    
    # Patterns identified
    if "patterns_identifies" in results:
        st.markdown("#### 🔍 Patterns identifiés")
        patterns = results["patterns_identifies"]
        
        for category, items in patterns.items():
            with st.expander(f"📌 {category.title()}"):
                for item in items:
                    st.markdown(f"- {item}")
    
    # Global score
    if "score_global" in results:
        st.markdown("#### 🎯 Score global")
        score = results["score_global"]
        st.markdown(f"**Note:** {score.get('note', 'N/A')}")
        st.markdown(f"**Justification:** {score.get('justification', 'N/A')}")


def render_comparison_results(results: dict):
    """Render comparison results"""
    if "error" in results:
        st.error(f"Erreur: {results['error']}")
        return
    
    if "_note" in results:
        st.warning(results["_note"])
    
    # Ranking
    if "classement" in results:
        st.markdown("#### 🏆 Classement")
        for item in results["classement"]:
            with st.expander(f"#{item.get('rang', '?')} - {item.get('campagne', 'N/A')} ({item.get('score_global', 'N/A')})"):
                st.markdown("**Forces:**")
                for f in item.get("forces", []):
                    st.markdown(f"- ✅ {f}")
                if item.get("faiblesses"):
                    st.markdown("**Faiblesses:**")
                    for f in item.get("faiblesses", []):
                        st.markdown(f"- ❌ {f}")
    
    # Conclusion
    if "conclusion" in results:
        st.info(f"💡 **Conclusion:** {results['conclusion']}")


def render_suggestions_results(results: dict):
    """Render A/B test suggestions"""
    if "error" in results:
        st.error(f"Erreur: {results['error']}")
        return
    
    if "_note" in results:
        st.warning(results["_note"])
    
    # Priority tests
    if "priorite_tests" in results:
        st.markdown("#### 🎯 Tests prioritaires")
        for test in results["priorite_tests"]:
            with st.expander(f"P{test.get('priorite', '?')} - {test.get('type_test', 'N/A')} ({test.get('impact_potentiel', 'N/A')})"):
                st.markdown(f"**Hypothèse:** {test.get('hypothese', 'N/A')}")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Variante A:** {test.get('variante_A', 'N/A')}")
                with col2:
                    st.markdown(f"**Variante B:** {test.get('variante_B', 'N/A')}")
    
    # Strategic advice
    if "conseil_strategique" in results:
        st.success(f"💡 **Conseil stratégique:** {results['conseil_strategique']}")


def render_variants_results(results: dict):
    """Render generated variants"""
    if "error" in results:
        st.error(f"Erreur: {results['error']}")
        return
    
    if "_note" in results:
        st.warning(results["_note"])
    
    # Subject variants
    if "variantes_sujet" in results:
        st.markdown("#### 📧 Variantes de sujets")
        for v in results["variantes_sujet"]:
            st.code(v.get("sujet", "N/A"))
            st.markdown(f"*Angle: {v.get('angle', 'N/A')}*")
            st.markdown("---")
    
    # Body variants
    if "variantes_corps_email" in results:
        st.markdown("#### 📝 Variantes de corps d'email")
        for v in results["variantes_corps_email"]:
            with st.expander(f"{v.get('version', 'N/A')}"):
                st.text(v.get("corps", "N/A"))


def render_data_table(df: pd.DataFrame):
    """Render the full data table"""
    st.markdown("### 📋 Données complètes")
    
    # Format percentages
    format_dict = {
        "Open Rate": "{:.1f}%",
        "CTR": "{:.1f}%",
        "Reply Rate Email": "{:.1f}%",
        "Acceptance Rate": "{:.1f}%",
        "Reply Rate LinkedIn": "{:.1f}%",
        "Reply Rate Global": "{:.1f}%",
        "Conversion Rate": "{:.1f}%"
    }
    
    st.dataframe(
        df.style.format(format_dict),
        use_container_width=True,
        hide_index=True
    )
    
    # Export button
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Exporter en CSV",
        data=csv,
        file_name=f"campaign_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv"
    )


def main():
    """Main application"""
    init_session_state()
    
    # Header
    st.markdown('<p class="main-header">🚀 Campaign Analyzer</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Analysez vos campagnes LGM avec l\'intelligence artificielle</p>', unsafe_allow_html=True)
    
    # Sidebar
    lgm_api_key, gemini_api_key, demo_mode = render_sidebar()
    
    # Main content
    if demo_mode:
        st.info("🎮 **Mode démo activé** - Utilisation de données fictives pour la démonstration")
        stats_list = get_demo_campaigns()
        campaign_content = get_demo_campaign_content()
        analyzer = MockGeminiAnalyzer()
    else:
        if not lgm_api_key:
            st.warning("⚠️ Entrez votre clé API LGM dans la sidebar pour commencer, ou activez le mode démo.")
            return
        
        # Fetch campaigns from LGM
        try:
            client = LGMClient(lgm_api_key)
            
            with st.spinner("Chargement des campagnes depuis LGM..."):
                campaigns = client.get_campaigns()
            
            if not campaigns:
                st.warning("Aucune campagne trouvée dans votre compte LGM.")
                return
            
            # Campaign selection
            st.markdown("### 🎯 Sélection des campagnes")
            
            campaign_options = {
                c.get("name", f"Campaign {c.get('id', 'unknown')}"): c.get("id") or c.get("_id")
                for c in campaigns
            }
            
            selected_names = st.multiselect(
                "Choisissez les campagnes à analyser",
                options=list(campaign_options.keys()),
                default=list(campaign_options.keys())[:5] if len(campaign_options) > 5 else list(campaign_options.keys())
            )
            
            if not selected_names:
                st.warning("Sélectionnez au moins une campagne.")
                return
            
            selected_ids = [campaign_options[name] for name in selected_names]
            
            # Fetch stats for selected campaigns
            with st.spinner("Récupération des statistiques..."):
                stats_list = client.get_selected_campaigns_stats(selected_ids)
            
            # Campaign content (would need to be fetched or provided)
            campaign_content = {}  # TODO: Add campaign content fetching
            
            # Initialize Gemini analyzer
            if gemini_api_key:
                analyzer = GeminiAnalyzer(gemini_api_key)
            else:
                st.warning("⚠️ Sans clé Gemini, l'analyse IA utilisera des réponses de démonstration.")
                analyzer = MockGeminiAnalyzer()
                
        except LGMAPIError as e:
            st.error(f"Erreur API LGM: {str(e)}")
            return
    
    # Convert stats to DataFrame
    df = stats_to_dataframe(stats_list)
    
    # Render sections
    render_metrics_overview(df)
    
    st.markdown("---")
    
    render_comparison_charts(df)
    
    st.markdown("---")
    
    render_ranking_table(df)
    
    st.markdown("---")
    
    render_ai_analysis(analyzer, stats_list, campaign_content)
    
    st.markdown("---")
    
    render_data_table(df)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #9ca3af;'>Campaign Analyzer v1.0 | Powered by LGM API + Google Gemini</p>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
