"""
Campaign Analyzer Dashboard
Main Streamlit application for analyzing LGM campaigns with AI
Simplified version focused on A/B testing workflow
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import re
from datetime import datetime

from lgm_client import LGMClient, LGMAPIError, CampaignStats
from gemini_analyzer import GeminiAnalyzer, MockGeminiAnalyzer


def clean_message_text(text: str) -> str:
    """Clean HTML tags and format message text for display"""
    if not text:
        return "N/A"
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


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
    .main-header { font-size: 2.5rem; font-weight: 700; color: #1f2937; margin-bottom: 0.5rem; }
    .sub-header { font-size: 1.1rem; color: #6b7280; margin-bottom: 2rem; }
    .winner-badge { background: linear-gradient(135deg, #fbbf24, #f59e0b); color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; }
    .metric-winner { background: #ecfdf5; border: 2px solid #10b981; border-radius: 8px; padding: 10px; }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# DEMO DATA
# =============================================================================

def get_demo_campaigns():
    """Return demo campaign data"""
    return [
        CampaignStats(
            campaign_id="demo_1",
            campaign_name="A/B Test - Subject A (Question)",
            total_leads=150,
            emails_sent=145,
            emails_opened=65,
            emails_clicked=20,
            emails_replied=12,
            linkedin_sent=140,
            linkedin_accepted=52,
            linkedin_replied=18,
            total_replies=30,
            total_conversions=6,
            templates=[
                {"name": "Email 1", "channel": "EMAIL", "subject": "Quick question about {{companyName}}?", "description": "Hi {{firstName}},\n\nSaw {{companyName}} is scaling fast. Quick question - how much time does your team spend on manual monitoring?\n\nWorth a 15-min chat?", "replied_percent": 8}
            ]
        ),
        CampaignStats(
            campaign_id="demo_2",
            campaign_name="A/B Test - Subject B (Statement)",
            total_leads=150,
            emails_sent=148,
            emails_opened=45,
            emails_clicked=15,
            emails_replied=18,
            linkedin_sent=142,
            linkedin_accepted=48,
            linkedin_replied=22,
            total_replies=40,
            total_conversions=9,
            templates=[
                {"name": "Email 1", "channel": "EMAIL", "subject": "{{companyName}}'s monitoring could be smarter", "description": "Hi {{firstName}},\n\nNoticed {{companyName}} is growing fast - congrats!\n\nMost e-commerce brands at your stage lose 10+ hours/week on manual monitoring. We help fix that.\n\nInterested in a quick demo?", "replied_percent": 12}
            ]
        ),
        CampaignStats(
            campaign_id="demo_3",
            campaign_name="A/B Test - LinkedIn Only",
            total_leads=100,
            emails_sent=0,
            emails_opened=0,
            emails_clicked=0,
            emails_replied=0,
            linkedin_sent=95,
            linkedin_accepted=38,
            linkedin_replied=15,
            total_replies=15,
            total_conversions=4,
            templates=[
                {"name": "LinkedIn DM", "channel": "LINKEDIN", "subject": "", "description": "Hi {{firstName}}, love what you're building at {{companyName}}! Quick question - are you happy with how you monitor your store's performance?", "replied_percent": 15}
            ]
        ),
    ]


def get_demo_campaign_content():
    """Return demo campaign content"""
    return {}


# =============================================================================
# DATA PROCESSING
# =============================================================================

def stats_to_dataframe(stats_list: list[CampaignStats]) -> pd.DataFrame:
    """Convert CampaignStats list to DataFrame"""
    data = []
    for stat in stats_list:
        data.append({
            "Campaign": stat.campaign_name,
            "ID": stat.campaign_id,
            "Leads": stat.total_leads,
            "Emails Sent": stat.emails_sent,
            "Emails Opened": stat.emails_opened,
            "Open Rate": stat.open_rate,
            "Email Replies": stat.emails_replied,
            "Email Reply Rate": stat.email_reply_rate,
            "LinkedIn Sent": stat.linkedin_sent,
            "LinkedIn Accepted": stat.linkedin_accepted,
            "Acceptance Rate": stat.linkedin_acceptance_rate,
            "LinkedIn Replies": stat.linkedin_replied,
            "LinkedIn Reply Rate": stat.linkedin_reply_rate,
            "Total Replies": stat.total_replies,
            "Global Reply Rate": stat.overall_reply_rate,
            "Conversions": stat.total_conversions,
            "Conversion Rate": stat.conversion_rate
        })
    return pd.DataFrame(data)


# =============================================================================
# DATA TAB COMPONENTS
# =============================================================================

def render_comparison_table(df: pd.DataFrame):
    """Render the comparison table with winners highlighted"""
    st.markdown("### 🏆 Campaign Comparison")
    
    # Select key metrics for comparison
    comparison_cols = ["Campaign", "Open Rate", "Global Reply Rate", "Conversion Rate"]
    df_compare = df[comparison_cols].copy()
    
    # Find winners for each metric
    metrics = ["Open Rate", "Global Reply Rate", "Conversion Rate"]
    winners = {}
    for metric in metrics:
        max_idx = df_compare[metric].idxmax()
        winners[metric] = max_idx
    
    # Create display dataframe with winners marked
    def highlight_winner(row):
        styles = [''] * len(row)
        for i, col in enumerate(row.index):
            if col in metrics and row.name == winners[col]:
                styles[i] = 'background-color: #ecfdf5; font-weight: bold'
        return styles
    
    # Format the data
    df_display = df_compare.copy()
    for metric in metrics:
        df_display[metric] = df_display.apply(
            lambda row: f"🏆 {row[metric]:.1f}%" if row.name == winners[metric] else f"{row[metric]:.1f}%",
            axis=1
        )
    
    st.dataframe(df_display, use_container_width=True, hide_index=True)
    
    # Summary
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        winner_open = df.loc[winners["Open Rate"], "Campaign"]
        st.success(f"**Best Open Rate:** {winner_open}")
    with col2:
        winner_reply = df.loc[winners["Global Reply Rate"], "Campaign"]
        st.success(f"**Best Reply Rate:** {winner_reply}")
    with col3:
        winner_conv = df.loc[winners["Conversion Rate"], "Campaign"]
        st.success(f"**Best Conversion:** {winner_conv}")


def render_comparison_chart(df: pd.DataFrame):
    """Render simple bar chart grouped by campaign"""
    st.markdown("### 📊 Visual Comparison")
    
    # Prepare data for grouped bar chart
    metrics = ["Open Rate", "Global Reply Rate", "Conversion Rate"]
    
    fig = go.Figure()
    
    colors = ['#3b82f6', '#10b981', '#f59e0b']
    
    for i, metric in enumerate(metrics):
        fig.add_trace(go.Bar(
            name=metric,
            x=df["Campaign"],
            y=df[metric],
            marker_color=colors[i],
            text=df[metric].apply(lambda x: f"{x:.1f}%"),
            textposition='outside'
        ))
    
    fig.update_layout(
        barmode='group',
        height=400,
        xaxis_title="",
        yaxis_title="Percentage (%)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=50)
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_full_data_table(df: pd.DataFrame):
    """Render full data table with dynamic columns based on channels used"""
    st.markdown("### 📋 Full Data")
    
    # Check which channels are used
    has_email = df["Emails Sent"].sum() > 0
    has_linkedin = df["LinkedIn Sent"].sum() > 0
    
    # Build column list dynamically
    columns = ["Campaign", "Leads"]
    
    if has_email:
        columns.extend(["Emails Sent", "Emails Opened", "Open Rate", "Email Replies", "Email Reply Rate"])
    
    if has_linkedin:
        columns.extend(["LinkedIn Sent", "LinkedIn Accepted", "Acceptance Rate", "LinkedIn Replies", "LinkedIn Reply Rate"])
    
    columns.extend(["Total Replies", "Global Reply Rate", "Conversions", "Conversion Rate"])
    
    # Filter to only existing columns
    available_columns = [col for col in columns if col in df.columns]
    df_display = df[available_columns].copy()
    
    # Format percentages
    pct_columns = [col for col in available_columns if "Rate" in col]
    format_dict = {col: "{:.1f}%" for col in pct_columns}
    
    st.dataframe(
        df_display.style.format(format_dict),
        use_container_width=True,
        hide_index=True
    )


def render_data_tab(df: pd.DataFrame):
    """Render the complete Data tab"""
    render_comparison_table(df)
    st.markdown("---")
    render_comparison_chart(df)
    st.markdown("---")
    render_full_data_table(df)


# =============================================================================
# AI AGENT TAB COMPONENTS
# =============================================================================

def render_ai_analysis_results(results: dict):
    """Render the AI analysis results"""
    if "error" in results:
        st.error(f"Analysis error: {results['error']}")
        if "raw_response" in results:
            with st.expander("View raw response"):
                st.code(results.get("raw_response", "No response"))
        return
    
    if "_note" in results:
        st.warning(results["_note"])
    
    # Section 1: What we learned
    if "learnings" in results:
        st.markdown("### 📈 Ce qu'on apprend de ces tests")
        learnings = results["learnings"]
        
        for learning in learnings:
            metric = learning.get("metric", "Metric")
            winner = learning.get("winner", "N/A")
            winner_value = learning.get("winner_value", "")
            loser_value = learning.get("loser_value", "")
            reasons = learning.get("reasons", [])
            
            with st.expander(f"**{metric}:** {winner} gagne ({winner_value} vs {loser_value})", expanded=True):
                for reason in reasons:
                    st.markdown(f"- {reason}")
        
        if results.get("conclusion"):
            st.info(f"**Conclusion:** {results['conclusion']}")
    
    # Section 2: Spam Check
    if "spam_check" in results:
        st.markdown("### 🚨 Spam Check")
        spam_results = results["spam_check"]
        
        for campaign_spam in spam_results:
            campaign = campaign_spam.get("campaign", "Campaign")
            status = campaign_spam.get("status", "clean")
            issues = campaign_spam.get("issues", [])
            
            if status == "clean":
                st.success(f"**{campaign}:** ✅ Clean (aucun spam word)")
            else:
                st.warning(f"**{campaign}:** ⚠️ {len(issues)} problème(s)")
                for issue in issues:
                    word = issue.get("word", "")
                    location = issue.get("location", "")
                    replacement = issue.get("replacement", "")
                    st.markdown(f"- `{word}` dans {location} → Remplacer par `{replacement}`")
    
    # Section 3: Optimal Campaign
    if "optimal_campaign" in results:
        st.markdown("### ✏️ Recommandation : La campagne optimale")
        optimal = results["optimal_campaign"]
        
        st.markdown("**En combinant le meilleur de chaque campagne :**")
        
        if optimal.get("subject"):
            st.markdown(f"**Sujet:** `{optimal['subject']}`")
            if optimal.get("subject_from"):
                st.caption(f"(inspiré de {optimal['subject_from']})")
        
        if optimal.get("body"):
            st.markdown("**Body:**")
            st.code(clean_message_text(optimal["body"]), language=None)
            if optimal.get("body_from"):
                st.caption(f"(structure de {optimal['body_from']})")
        
        if optimal.get("linkedin"):
            st.markdown("**LinkedIn:**")
            st.code(clean_message_text(optimal["linkedin"]), language=None)
        
        if optimal.get("why"):
            st.success(f"**Pourquoi ça devrait marcher:** {optimal['why']}")
    
    # Section 4: Next A/B Test
    if "next_ab_test" in results:
        st.markdown("### 🧪 Prochain A/B test à lancer")
        test = results["next_ab_test"]
        
        st.markdown(f"**Variable à tester:** {test.get('variable', 'N/A')}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Variant A:**")
            st.code(clean_message_text(test.get("variant_a", "N/A")), language=None)
        with col2:
            st.markdown("**Variant B:**")
            st.code(clean_message_text(test.get("variant_b", "N/A")), language=None)
        
        if test.get("hypothesis"):
            st.info(f"**Hypothèse:** {test['hypothesis']}")
        
        if test.get("duration"):
            st.caption(f"⏱️ Durée recommandée: {test['duration']}")


def render_ai_agent_tab(analyzer, stats_list: list[CampaignStats], campaign_content: dict):
    """Render the AI Agent tab"""
    
    # Set business context
    if hasattr(st.session_state, 'business_context'):
        analyzer.set_business_context(st.session_state.business_context)
    
    # Prepare data for analysis
    campaigns_data = []
    templates_by_campaign = {}
    
    for stat in stats_list:
        campaigns_data.append({
            "name": stat.campaign_name,
            "leads": stat.total_leads,
            "emails_sent": stat.emails_sent,
            "open_rate": stat.open_rate,
            "email_reply_rate": stat.email_reply_rate,
            "linkedin_sent": stat.linkedin_sent,
            "linkedin_acceptance_rate": stat.linkedin_acceptance_rate,
            "linkedin_reply_rate": stat.linkedin_reply_rate,
            "overall_reply_rate": stat.overall_reply_rate,
            "conversion_rate": stat.conversion_rate
        })
        
        if stat.templates:
            templates_by_campaign[stat.campaign_name] = stat.templates
    
    if campaign_content:
        for name, content in campaign_content.items():
            if name not in templates_by_campaign:
                templates_by_campaign[name] = [content]
    
    # Template status
    if templates_by_campaign:
        st.success(f"✅ Message templates found for {len(templates_by_campaign)} campaign(s)")
    else:
        st.info("ℹ️ No message templates found. AI will analyze based on performance data only.")
    
    # Main Analysis Button
    st.markdown("---")
    if st.button("🚀 Analyser mes campagnes", type="primary", use_container_width=True, key="analyze_btn"):
        with st.spinner("🤖 Analyse en cours... (30 secondes)"):
            results = analyzer.full_analysis(campaigns_data, templates_by_campaign)
            st.session_state.analysis_results = results
    
    # Display results
    if 'analysis_results' in st.session_state:
        st.markdown("---")
        render_ai_analysis_results(st.session_state.analysis_results)
    
    # Ask AI Section
    st.markdown("---")
    st.markdown("### 💬 Ask AI")
    st.caption("Pose des questions sur tes campagnes (les réponses tiennent compte de l'analyse)")
    
    user_question = st.text_area(
        "Ta question",
        placeholder="Exemples:\n- Pourquoi Campaign A a un meilleur open rate?\n- Réécris mon hook en version plus courte\n- Quel serait le meilleur sujet d'email?",
        height=100,
        key="ai_question"
    )
    
    if st.button("💬 Demander", key="ask_btn", type="secondary", use_container_width=True):
        if user_question.strip():
            with st.spinner("Réflexion..."):
                # Include previous analysis in context if available
                analysis_context = ""
                if 'analysis_results' in st.session_state and "error" not in st.session_state.analysis_results:
                    analysis_context = f"\n\nPREVIOUS ANALYSIS RESULTS:\n{json.dumps(st.session_state.analysis_results, indent=2, default=str)}"
                
                full_question = user_question + analysis_context
                response = analyzer.chat(full_question, campaigns_data, templates_by_campaign)
                st.session_state.chat_response = response
        else:
            st.warning("Pose une question d'abord")
    
    if 'chat_response' in st.session_state:
        st.markdown("---")
        st.markdown("**🤖 Réponse:**")
        st.markdown(st.session_state.chat_response)


# =============================================================================
# SIDEBAR
# =============================================================================

def render_sidebar():
    """Render the sidebar with configuration options"""
    st.sidebar.markdown("## ⚙️ Configuration")
    
    # API Keys
    st.sidebar.markdown("### 🔑 API Keys")
    lgm_api_key = st.sidebar.text_input("LGM API Key", type="password", key="lgm_key")
    gemini_api_key = st.sidebar.text_input("Gemini API Key", type="password", key="gemini_key")
    
    # Demo mode
    st.sidebar.markdown("### 🎮 Mode")
    demo_mode = st.sidebar.checkbox("Demo Mode", value=True, help="Use sample data")
    
    # Business Context
    with st.sidebar.expander("📝 Business Context"):
        product = st.text_input("Product", value="AI Agent for E-commerce", key="ctx_product")
        target = st.text_input("Target", value="E-commerce merchants, Shopify owners", key="ctx_target")
        pain_points = st.text_area("Pain points", value="Manual monitoring, missed alerts, too many false positives", key="ctx_pain", height=80)
        
        st.session_state.business_context = {
            "product": product,
            "target": target,
            "pain_points": pain_points
        }
    
    return lgm_api_key, gemini_api_key, demo_mode


# =============================================================================
# MAIN
# =============================================================================

def main():
    # Header
    st.markdown('<p class="main-header">🚀 Campaign Analyzer</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Analyse tes A/B tests et optimise tes campagnes</p>', unsafe_allow_html=True)
    
    # Sidebar
    lgm_api_key, gemini_api_key, demo_mode = render_sidebar()
    
    # Initialize session state
    if "campaign_stats" not in st.session_state:
        st.session_state.campaign_stats = []
    
    # Get data
    if demo_mode:
        stats_list = get_demo_campaigns()
        campaign_content = get_demo_campaign_content()
        analyzer = MockGeminiAnalyzer()
    else:
        if not lgm_api_key:
            st.warning("⚠️ Entre ta clé API LGM dans la sidebar, ou active le mode demo.")
            return
        
        client = LGMClient(lgm_api_key)
        
        # Campaign Selection
        st.markdown("### 🎯 Sélection des campagnes")
        
        if "available_campaigns" not in st.session_state or st.button("🔄 Rafraîchir"):
            try:
                with st.spinner("Chargement..."):
                    campaigns = client.get_all_campaigns()
                    st.session_state.available_campaigns = campaigns
            except Exception as e:
                st.error(f"Erreur: {str(e)}")
                st.session_state.available_campaigns = []
        
        available_campaigns = st.session_state.get("available_campaigns", [])
        
        if not available_campaigns:
            st.warning("⚠️ Aucune campagne trouvée.")
            return
        
        campaign_options = {
            f"{c['name']} ({c['leadsCount']} leads)": c['id']
            for c in available_campaigns
        }
        
        selected_labels = st.multiselect("Sélectionne les campagnes à comparer", list(campaign_options.keys()))
        selected_campaign_ids = [campaign_options[label] for label in selected_labels]
        campaign_names = {c['id']: c['name'] for c in available_campaigns}
        
        if not selected_labels:
            st.warning("⚠️ Sélectionne au moins une campagne.")
            return
        
        if st.button("📊 Charger les données", type="primary", use_container_width=True):
            try:
                with st.spinner("Chargement..."):
                    stats_list = client.get_campaigns_stats_by_ids(selected_campaign_ids, campaign_names)
                    st.session_state.campaign_stats = stats_list
                st.success(f"✅ {len(stats_list)} campagne(s) chargée(s)!")
            except LGMAPIError as e:
                st.error(f"Erreur LGM: {str(e)}")
                return
        
        if not st.session_state.campaign_stats:
            st.info("👆 Clique pour charger les données")
            return
        
        stats_list = st.session_state.campaign_stats
        campaign_content = {}
        
        if gemini_api_key:
            analyzer = GeminiAnalyzer(gemini_api_key)
        else:
            st.warning("⚠️ Ajoute ta clé Gemini pour une vraie analyse AI.")
            analyzer = MockGeminiAnalyzer()
    
    # Create dataframe
    df = stats_to_dataframe(stats_list)
    
    # Main tabs
    tab_data, tab_ai = st.tabs(["📊 Data", "🤖 AI Agent"])
    
    with tab_data:
        render_data_tab(df)
    
    with tab_ai:
        render_ai_agent_tab(analyzer, stats_list, campaign_content)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #9ca3af;'>Campaign Analyzer v3.0 | LGM + Gemini AI</p>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()