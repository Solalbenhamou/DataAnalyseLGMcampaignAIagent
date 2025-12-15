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
import re
from datetime import datetime

from lgm_client import LGMClient, LGMAPIError, CampaignStats
from gemini_analyzer import GeminiAnalyzer, MockGeminiAnalyzer


def clean_message_text(text: str) -> str:
    """Clean HTML tags and format message text for display"""
    if not text:
        return "N/A"
    
    # Replace <br> and <br/> with newlines
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    
    # Remove all other HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Clean up multiple newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Trim whitespace
    text = text.strip()
    
    return text

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
    if 'business_context' not in st.session_state:
        st.session_state.business_context = {
            "product": "AI Agent",
            "goal": "Connect with leads → Book meetings → Close deals",
            "target": "Decision makers (CEOs, CTOs, Founders)",
            "industry": "B2B SaaS",
            "additional": ""
        }


def get_api_keys():
    """Get API keys from Streamlit secrets or user input"""
    lgm_key = None
    gemini_key = None
    
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
            help="Find your API key in LGM > Settings > Integrations & API"
        )
        
        gemini_api_key = st.text_input(
            "Gemini API Key",
            value=gemini_key_default or "",
            type="password",
            help="Create a key on Google AI Studio"
        )
        
        # Test connection button
        if st.button("🔌 Test LGM Connection", use_container_width=True):
            if lgm_api_key:
                with st.spinner("Testing connection..."):
                    client = LGMClient(lgm_api_key)
                    if client.test_connection():
                        st.success("✅ LGM connection successful!")
                        st.session_state.lgm_connected = True
                    else:
                        st.error("❌ Connection failed. Check your API key.")
                        st.session_state.lgm_connected = False
            else:
                st.warning("Enter your LGM API key")
        
        st.markdown("---")
        
        # Business Context section
        st.markdown("### 🎯 Business Context")
        
        business_preset = st.selectbox(
            "Business preset",
            options=["AI Agent for E-commerce", "Custom"],
            index=0,
            help="Select your business type for tailored AI analysis"
        )
        
        if business_preset == "AI Agent for E-commerce":
            business_context = {
                "product": "AI Agent for E-commerce",
                "product_description": "An intelligent AI agent that monitors, detects, and alerts e-commerce merchants about critical events affecting their online stores. Features: real-time Slack/dashboard alerts, ML-powered anomaly detection with seasonality awareness, store-specific calibration, statistical relevance filtering, AI chatbot for alert explanations.",
                "key_differentiators": "1) Only statistically significant alerts (no noise), 2) Personalized detection per store, 3) Seasonality-aware, 4) Works in Slack + Dashboard, 5) AI explains the 'why' behind alerts",
                "goal": "Connect with e-commerce decision makers → Book demo/meeting → Close deals",
                "target": "E-commerce merchants, Shopify store owners, DTC brands, E-commerce managers, CTOs at online retailers",
                "pain_points": "Site crashes going unnoticed, payment failures, traffic drops, too many false alerts, lack of context on issues, manual monitoring",
                "industry": "E-commerce / SaaS",
                "additional": ""
            }
        else:
            with st.expander("📝 Custom business context"):
                business_context = {
                    "product": st.text_input("Product/Service", value="AI Agent for E-commerce"),
                    "product_description": st.text_area("Product description", value="AI-powered monitoring for e-commerce stores", height=80),
                    "key_differentiators": st.text_area("Key differentiators", value="Statistically significant alerts only", height=60),
                    "goal": st.text_input("Sales goal", value="Connect → Demo → Close"),
                    "target": st.text_input("Target ICP", value="E-commerce merchants, Shopify store owners"),
                    "pain_points": st.text_input("Pain points you solve", value="Unnoticed site issues, false alerts"),
                    "industry": st.text_input("Industry", value="E-commerce / SaaS"),
                    "additional": st.text_area("Additional context", value="", height=60)
                }
        
        st.session_state.business_context = business_context
        
        st.markdown("---")
        
        # Demo mode
        st.markdown("### 🎮 Demo Mode")
        demo_mode = st.checkbox(
            "Use demo data",
            help="Test the dashboard without API keys"
        )
        
        st.markdown("---")
        
        # About section
        st.markdown("### ℹ️ About")
        st.markdown("""
        **Campaign Analyzer** analyzes your LGM campaigns with AI to:
        - ✍️ Analyze copywriting patterns
        - 🎯 Strategic recommendations
        - 🧪 Generate A/B tests
        - 💬 Ask AI anything
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
            total_conversions=5,
            templates=[
                {"name": "Email 1", "channel": "EMAIL", "subject": "Quick question about {{companyName}}", "description": "Hi {{firstName}}, noticed {{companyName}} is scaling fast...", "replied_percent": 8},
                {"name": "LinkedIn DM", "channel": "LINKEDIN", "description": "Thanks for connecting! Quick question about your current process...", "replied_percent": 15}
            ]
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
            total_conversions=7,
            templates=[
                {"name": "Connection Request", "channel": "LINKEDIN", "description": "Hi {{firstName}}, love what you're building at {{companyName}}!", "replied_percent": 12},
                {"name": "Follow-up Email", "channel": "EMAIL", "subject": "{{firstName}} - following up", "description": "Hey {{firstName}}, wanted to follow up on my LinkedIn message...", "replied_percent": 8}
            ]
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
            total_conversions=3,
            templates=[
                {"name": "Cold Email 1", "channel": "EMAIL", "subject": "Your ops team wastes time daily", "description": "Hi {{firstName}}, I noticed {{companyName}} is scaling fast. When that happens, ops teams usually drown in manual work...", "replied_percent": 7}
            ]
        ),
    ]


def get_demo_campaign_content():
    """Return demo campaign content"""
    return {
        "Email > LinkedIn - CEO #1": {
            "subject": "Quick question about {{companyName}}",
            "body": "Hi {{firstname}},\n\nNoticed {{companyName}} is scaling fast. When that happens, CEOs usually spend hours on tasks an AI could handle.\n\nWorth a quick chat?",
            "linkedin_1": "Thanks for connecting {{firstname}}! Quick question - how much time does your team spend on repetitive tasks?"
        },
        "LinkedIn > Email - CMO #1": {
            "subject": "{{firstName}} - following up",
            "body": "Hey {{firstname}},\n\nWanted to follow up on my LinkedIn message. We help companies like {{companyName}} save 10+ hours/week with AI automation.\n\nInterested?",
            "linkedin_1": "Hi {{firstname}}, love what you're building at {{companyName}}!"
        }
    }


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
            "Emails Clicked": stat.emails_clicked,
            "CTR": stat.click_rate,
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


def render_metrics_overview(df: pd.DataFrame):
    """Render the metrics overview section"""
    st.markdown("### 📊 Overview")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_leads = df["Leads"].sum()
        st.metric("Total Leads", f"{total_leads:,}")
    
    with col2:
        avg_open_rate = df["Open Rate"].mean()
        st.metric("Avg Open Rate", f"{avg_open_rate:.1f}%")
    
    with col3:
        avg_reply_rate = df["Global Reply Rate"].mean()
        st.metric("Avg Reply Rate", f"{avg_reply_rate:.1f}%")
    
    with col4:
        total_conversions = df["Conversions"].sum()
        st.metric("Total Conversions", f"{total_conversions:,}")
    
    with col5:
        avg_conversion = df["Conversion Rate"].mean()
        st.metric("Avg Conversion", f"{avg_conversion:.1f}%")


def render_comparison_charts(df: pd.DataFrame):
    """Render comparison charts"""
    st.markdown("### 📈 Campaign Comparison")
    
    tab1, tab2, tab3 = st.tabs(["📧 Email", "💼 LinkedIn", "🎯 Global"])
    
    with tab1:
        fig = make_subplots(rows=1, cols=2, subplot_titles=("Open Rate", "Email Reply Rate"))
        
        fig.add_trace(
            go.Bar(name="Open Rate", x=df["Campaign"], y=df["Open Rate"], marker_color="#3b82f6"),
            row=1, col=1
        )
        fig.add_trace(
            go.Bar(name="Reply Rate", x=df["Campaign"], y=df["Email Reply Rate"], marker_color="#10b981"),
            row=1, col=2
        )
        
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        fig = make_subplots(rows=1, cols=2, subplot_titles=("Acceptance Rate", "LinkedIn Reply Rate"))
        
        fig.add_trace(
            go.Bar(name="Acceptance", x=df["Campaign"], y=df["Acceptance Rate"], marker_color="#8b5cf6"),
            row=1, col=1
        )
        fig.add_trace(
            go.Bar(name="Reply Rate", x=df["Campaign"], y=df["LinkedIn Reply Rate"], marker_color="#f59e0b"),
            row=1, col=2
        )
        
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        categories = ["Open Rate", "Global Reply Rate", "Conversion Rate", "Acceptance Rate"]
        
        fig = go.Figure()
        
        colors = px.colors.qualitative.Set2
        for i, row in df.iterrows():
            fig.add_trace(go.Scatterpolar(
                r=[row["Open Rate"], row["Global Reply Rate"], row["Conversion Rate"] * 5, row["Acceptance Rate"]],
                theta=categories,
                fill='toself',
                name=row["Campaign"][:20] + "..." if len(row["Campaign"]) > 20 else row["Campaign"],
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
    st.markdown("### 🏆 Campaign Ranking")
    
    df_ranked = df.copy()
    df_ranked["Score"] = (
        df_ranked["Open Rate"] * 0.2 +
        df_ranked["Global Reply Rate"] * 0.4 +
        df_ranked["Conversion Rate"] * 0.4
    ).round(2)
    
    df_ranked = df_ranked.sort_values("Score", ascending=False)
    df_ranked.insert(0, "Rank", range(1, len(df_ranked) + 1))
    
    display_cols = ["Rank", "Campaign", "Leads", "Open Rate", "Global Reply Rate", "Conversion Rate", "Score"]
    
    st.dataframe(
        df_ranked[display_cols].style.format({
            "Open Rate": "{:.1f}%",
            "Global Reply Rate": "{:.1f}%",
            "Conversion Rate": "{:.1f}%",
            "Score": "{:.2f}"
        }).background_gradient(subset=["Score"], cmap="Greens"),
        use_container_width=True,
        hide_index=True
    )


def render_ai_analysis(analyzer, stats_list: list[CampaignStats], campaign_content: dict):
    """Render the AI Agent section with unified analysis"""
    
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
            "open_rate": stat.open_rate,
            "email_reply_rate": stat.email_reply_rate,
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
    
    # Show template status
    if templates_by_campaign:
        st.success(f"✅ Message templates found for {len(templates_by_campaign)} campaign(s)")
    else:
        st.info("ℹ️ No message templates found. AI will analyze based on performance data only.")
    
    # Menu selector
    st.markdown("---")
    analysis_mode = st.selectbox(
        "Select Analysis Mode",
        ["🚀 Overall Analysis", "📊 Detailed Analysis", "💬 Ask AI"],
        key="analysis_mode_selector"
    )
    
    st.markdown("---")
    
    # ===== OVERALL ANALYSIS =====
    if analysis_mode == "🚀 Overall Analysis":
        st.markdown("### 🚀 Overall Analysis")
        st.caption("Complete diagnosis with corrections and A/B tests in one click")
        
        if st.button("🚀 Analyze My Campaigns", type="primary", use_container_width=True, key="main_analysis_btn"):
            with st.spinner("🤖 AI is analyzing your campaigns... (this may take 30 seconds)"):
                results = analyzer.full_analysis(campaigns_data, templates_by_campaign)
                st.session_state.full_analysis_results = results
        
        if 'full_analysis_results' in st.session_state:
            render_full_analysis(st.session_state.full_analysis_results)
    
    # ===== DETAILED ANALYSIS =====
    elif analysis_mode == "📊 Detailed Analysis":
        st.markdown("### 📊 Detailed Analysis")
        st.caption("Run specific analyses individually")
        
        detail_tabs = st.tabs(["✍️ Copywriting", "🚨 Spam Check", "🎯 Strategy", "🧪 A/B Tests"])
        
        with detail_tabs[0]:
            st.markdown("**Deep dive into hooks, CTAs, and message structure**")
            if st.button("Run Copywriting Analysis", key="copy_btn", type="primary", use_container_width=True):
                with st.spinner("Analyzing..."):
                    results = analyzer.analyze_copywriting(campaigns_data, templates_by_campaign)
                    st.session_state.copywriting_results = results
            if 'copywriting_results' in st.session_state:
                render_copywriting_results(st.session_state.copywriting_results)
        
        with detail_tabs[1]:
            st.markdown("**Check for spam triggers in subjects and body**")
            if st.button("Run Spam Analysis", key="spam_btn", type="primary", use_container_width=True):
                with st.spinner("Analyzing..."):
                    results = analyzer.analyze_spam(campaigns_data, templates_by_campaign)
                    st.session_state.spam_results = results
            if 'spam_results' in st.session_state:
                render_spam_results(st.session_state.spam_results)
        
        with detail_tabs[2]:
            st.markdown("**Channel strategy and funnel optimization**")
            if st.button("Run Strategy Analysis", key="strategy_btn", type="primary", use_container_width=True):
                with st.spinner("Analyzing..."):
                    results = analyzer.get_strategic_recommendations(campaigns_data, templates_by_campaign)
                    st.session_state.strategy_results = results
            if 'strategy_results' in st.session_state:
                render_strategy_results(st.session_state.strategy_results)
        
        with detail_tabs[3]:
            st.markdown("**Generate specific A/B test variants**")
            if st.button("Generate A/B Tests", key="ab_btn", type="primary", use_container_width=True):
                with st.spinner("Generating..."):
                    results = analyzer.generate_ab_tests(campaigns_data, templates_by_campaign)
                    st.session_state.ab_results = results
            if 'ab_results' in st.session_state:
                render_ab_test_results(st.session_state.ab_results)
    
    # ===== ASK AI =====
    elif analysis_mode == "💬 Ask AI":
        st.markdown("### 💬 Ask AI")
        st.caption("Ask any question about your campaigns")
        
        user_question = st.text_area(
            "Your question",
            placeholder="Examples:\n- Why is Campaign X underperforming?\n- Rewrite my LinkedIn message to be shorter\n- What's the best follow-up sequence?\n- Compare my email vs LinkedIn performance",
            height=120,
            key="ai_question"
        )
        
        if st.button("💬 Ask AI", key="chat_btn", type="primary", use_container_width=True):
            if user_question.strip():
                with st.spinner("Thinking..."):
                    response = analyzer.chat(user_question, campaigns_data, templates_by_campaign)
                    st.session_state.chat_response = response
            else:
                st.warning("Please enter a question")
        
        if 'chat_response' in st.session_state:
            st.markdown("---")
            st.markdown("**🤖 AI Response:**")
            st.markdown(st.session_state.chat_response)


def render_full_analysis(results: dict):
    """Render the complete AI analysis with diagnosis, corrections, and A/B tests"""
    if "error" in results:
        st.error(f"Analysis error: {results['error']}")
        if "raw_response" in results and results["raw_response"]:
            with st.expander("🔍 View raw AI response (for debugging)"):
                st.code(results["raw_response"])
        return
    
    if "_note" in results:
        st.warning(results["_note"])
    
    # Executive Summary
    if results.get("summary"):
        st.info(f"📋 **Summary:** {results['summary']}")
    
    # Quick Wins - Show first for immediate action
    quick_wins = results.get("quick_wins", [])
    if quick_wins:
        st.markdown("### ⚡ Quick Wins")
        cols = st.columns(len(quick_wins) if len(quick_wins) <= 3 else 3)
        for i, win in enumerate(quick_wins[:3]):
            with cols[i % 3]:
                impact_color = "🔴" if win.get("impact") == "high" else "🟡" if win.get("impact") == "medium" else "🟢"
                st.markdown(f"""
                <div style="padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; background: #fafafa;">
                    <strong>{win.get('action', 'N/A')}</strong><br>
                    <small>⏱️ {win.get('effort', 'N/A')} | {impact_color} {win.get('impact', 'N/A')} impact</small>
                </div>
                """, unsafe_allow_html=True)
    
    # Diagnosis Section
    diagnosis = results.get("diagnosis", [])
    if diagnosis:
        st.markdown("### 🔍 Campaign Diagnosis")
        for diag in diagnosis:
            status = diag.get("status", "warning")
            status_icon = "🔴" if status == "critical" else "🟡" if status == "warning" else "🟢"
            
            with st.expander(f"{status_icon} **{diag.get('campaign', 'Campaign')}** - {diag.get('performance_summary', '')}"):
                st.markdown(f"**Main Problem:** {diag.get('main_problem', 'N/A')}")
                
                root_causes = diag.get("root_causes", [])
                if root_causes:
                    st.markdown("**Root Causes:**")
                    for cause in root_causes:
                        st.markdown(f"""
                        - **{cause.get('issue', 'Issue')}** ({cause.get('location', 'N/A')})
                          - Evidence: `{clean_message_text(cause.get('evidence', 'N/A'))}`
                          - Impact: {cause.get('impact', 'N/A')}
                        """)
    
    # Spam Alerts - Show prominently if any
    spam_alerts = results.get("spam_alerts", [])
    if spam_alerts:
        st.markdown("### 🚨 Spam Alerts")
        for alert in spam_alerts:
            severity_icon = "🔴" if alert.get("severity") == "high" else "🟡" if alert.get("severity") == "medium" else "🟢"
            st.warning(f"{severity_icon} **\"{alert.get('word', 'N/A')}\"** found in {alert.get('location', 'N/A')} ({alert.get('campaign', 'N/A')}) → Replace with: **{alert.get('replace_with', 'N/A')}**")
    
    # Corrections Section
    corrections = results.get("corrections", [])
    if corrections:
        st.markdown("### ✏️ Recommended Corrections")
        for corr in corrections:
            with st.expander(f"#{corr.get('priority', '?')} - {corr.get('campaign', 'Campaign')} ({corr.get('type', 'N/A')})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**❌ Current:**")
                    st.code(clean_message_text(corr.get("current", "N/A")), language=None)
                with col2:
                    st.markdown("**✅ Corrected:**")
                    st.code(clean_message_text(corr.get("corrected", "N/A")), language=None)
                
                st.markdown(f"**Why:** {corr.get('why', 'N/A')}")
                st.success(f"**Expected Impact:** {corr.get('expected_impact', 'N/A')}")
    
    # A/B Tests Section
    ab_tests = results.get("ab_tests", [])
    if ab_tests:
        st.markdown("### 🧪 Recommended A/B Tests")
        for i, test in enumerate(ab_tests):
            with st.expander(f"Test {i+1}: {test.get('test_name', 'Test')}"):
                st.markdown(f"**Hypothesis:** {test.get('hypothesis', 'N/A')}")
                st.markdown(f"**Campaign:** {test.get('campaign', 'N/A')}")
                
                col1, col2 = st.columns(2)
                variant_a = test.get("variant_a", {})
                variant_b = test.get("variant_b", {})
                
                with col1:
                    st.markdown(f"**{variant_a.get('name', 'Variant A')}:**")
                    st.text(clean_message_text(variant_a.get("content", "N/A")))
                with col2:
                    st.markdown(f"**{variant_b.get('name', 'Variant B')}:**")
                    st.text(clean_message_text(variant_b.get("content", "N/A")))
                
                st.caption(f"📊 Metric: {test.get('metric', 'N/A')} | ⏱️ Duration: {test.get('duration', 'N/A')}")
    
    # Detailed Analysis in Sub-expander
    detailed = results.get("detailed_analysis", {})
    if detailed:
        with st.expander("📚 View Detailed Analysis"):
            # Hooks
            hooks = detailed.get("hooks", {})
            if hooks:
                st.markdown("#### 🎣 Hook Analysis")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Best Hooks:**")
                    for h in hooks.get("best", []):
                        st.success(f"`{clean_message_text(h.get('text', ''))}` - {h.get('why', '')}")
                with col2:
                    st.markdown("**Worst Hooks:**")
                    for h in hooks.get("worst", []):
                        st.error(f"`{clean_message_text(h.get('text', ''))}` - {h.get('why', '')}")
            
            # CTAs
            ctas = detailed.get("ctas", {})
            if ctas:
                st.markdown("#### 🎯 CTA Analysis")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Best CTAs:**")
                    for c in ctas.get("best", []):
                        st.markdown(f"- ✅ `{c}`")
                with col2:
                    st.markdown("**Avoid:**")
                    for c in ctas.get("worst", []):
                        st.markdown(f"- ❌ `{c}`")
            
            # Channel Insights
            channels = detailed.get("channel_insights", {})
            if channels:
                st.markdown("#### 📱 Channel Insights")
                if channels.get("email"):
                    st.markdown(f"**Email:** {channels['email']}")
                if channels.get("linkedin"):
                    st.markdown(f"**LinkedIn:** {channels['linkedin']}")
                if channels.get("recommendation"):
                    st.info(f"**Recommendation:** {channels['recommendation']}")


def render_copywriting_results(results: dict):
    """Render copywriting analysis results"""
    if "error" in results:
        st.error(f"Analysis error: {results['error']}")
        if "raw_response" in results and results["raw_response"]:
            with st.expander("🔍 View raw AI response (for debugging)"):
                st.code(results["raw_response"])
        return
    
    if "_note" in results:
        st.warning(results["_note"])
    
    # Executive Summary
    if "executive_summary" in results:
        st.markdown("#### 💡 Executive Summary")
        summary = results["executive_summary"]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"**Main Insight:**\n{summary.get('main_insight', 'N/A')}")
        with col2:
            st.warning(f"**Biggest Opportunity:**\n{summary.get('biggest_opportunity', 'N/A')}")
        with col3:
            st.success(f"**Quick Win:**\n{summary.get('quick_win', 'N/A')}")
    
    # Hook Analysis
    if "hook_analysis" in results:
        st.markdown("#### 🎣 Hook Analysis")
        hooks = results["hook_analysis"]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**✅ Best Hooks:**")
            for hook in hooks.get("best_hooks", []):
                with st.expander(f"📈 {hook.get('reply_rate', 'N/A')} reply rate"):
                    st.text(clean_message_text(hook.get("hook", "N/A")))
                    st.markdown(f"*Campaign: {hook.get('campaign', 'N/A')}*")
                    st.markdown(f"**Why it works:** {hook.get('why_it_works', 'N/A')}")
        
        with col2:
            st.markdown("**❌ Worst Hooks:**")
            for hook in hooks.get("worst_hooks", []):
                with st.expander(f"📉 {hook.get('reply_rate', 'N/A')} reply rate"):
                    st.text(clean_message_text(hook.get("hook", "N/A")))
                    st.markdown(f"*Campaign: {hook.get('campaign', 'N/A')}*")
                    st.markdown(f"**Why it fails:** {hook.get('why_it_fails', 'N/A')}")
        
        if hooks.get("hook_patterns"):
            st.markdown("**🔍 Winning Patterns:**")
            for pattern in hooks["hook_patterns"]:
                st.markdown(f"- {pattern}")
    
    # CTA Analysis
    if "cta_analysis" in results:
        st.markdown("#### 🎯 CTA Analysis")
        cta = results["cta_analysis"]
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**✅ Best CTAs:**")
            for c in cta.get("best_ctas", []):
                st.markdown(f"- `{c}`")
        with col2:
            st.markdown("**❌ CTAs to Avoid:**")
            for c in cta.get("worst_ctas", []):
                st.markdown(f"- `{c}`")
    
    # Message Improvements
    if "message_improvements" in results:
        st.markdown("#### ✨ Message Improvements")
        for improvement in results["message_improvements"]:
            with st.expander(f"🔄 {improvement.get('campaign', 'Message')}"):
                st.markdown("**Original:**")
                original = clean_message_text(improvement.get("original_message", "N/A"))
                st.text(original)
                
                st.markdown("**Improved Version:**")
                improved = clean_message_text(improvement.get("improved_version", "N/A"))
                st.text(improved)
                
                if improvement.get("changes_made"):
                    st.markdown("**Changes Made:**")
                    for change in improvement["changes_made"]:
                        st.markdown(f"- {change}")


def render_spam_results(results: dict):
    """Render spam analysis results"""
    if "error" in results:
        st.error(f"Analysis error: {results['error']}")
        if "raw_response" in results and results["raw_response"]:
            with st.expander("🔍 View raw AI response (for debugging)"):
                st.code(results["raw_response"])
        return
    
    if "_note" in results:
        st.warning(results["_note"])
    
    # Overall Risk & Score
    col1, col2 = st.columns(2)
    with col1:
        risk = results.get("overall_spam_risk", "Unknown")
        if risk == "High":
            st.error(f"⚠️ **Overall Spam Risk: {risk}**")
        elif risk == "Medium":
            st.warning(f"⚡ **Overall Spam Risk: {risk}**")
        else:
            st.success(f"✅ **Overall Spam Risk: {risk}**")
    with col2:
        score = results.get("deliverability_score", "N/A")
        st.metric("Deliverability Score", score)
    
    # Overall Summary
    if results.get("overall_summary"):
        st.info(f"📋 **Summary:** {results['overall_summary']}")
    
    # Spam Words Found
    spam_words = results.get("spam_words_found", [])
    if spam_words:
        st.markdown("#### 🔍 Spam Triggers Found")
        for item in spam_words:
            risk_emoji = "🔴" if item.get("risk_level") == "High" else "🟡" if item.get("risk_level") == "Medium" else "🟢"
            with st.expander(f"{risk_emoji} \"{item.get('word_or_phrase', 'N/A')}\" in {item.get('location', 'N/A')} ({item.get('campaign', 'N/A')})"):
                st.markdown(f"**Risk Level:** {item.get('risk_level', 'N/A')}")
                st.markdown(f"**Why it's risky:** {item.get('why_its_risky', 'N/A')}")
                
                # Show before/after if available
                if item.get("original_sentence"):
                    st.markdown("**Original:**")
                    st.code(clean_message_text(item.get("original_sentence", "")), language=None)
                
                if item.get("suggested_replacement"):
                    st.markdown("**Replace with:**")
                    st.success(clean_message_text(item.get("suggested_replacement", "")))
                elif item.get("suggested_alternative"):
                    st.success(f"**Suggested Alternative:** {item.get('suggested_alternative', 'N/A')}")
    else:
        st.success("✅ No major spam triggers detected!")
    
    # Subject Line Analysis
    subject_analysis = results.get("subject_line_analysis", [])
    if subject_analysis:
        st.markdown("#### 📧 Subject Line Analysis")
        for subj in subject_analysis:
            spam_score = subj.get("spam_score", "Unknown")
            score_emoji = "🔴" if spam_score == "High" else "🟡" if spam_score == "Medium" else "🟢"
            with st.expander(f"{score_emoji} {subj.get('campaign', 'Campaign')} - {spam_score} risk"):
                original = subj.get('original_subject') or subj.get('subject', 'N/A')
                st.markdown(f"**Current Subject:**")
                st.error(f"`{original}`")
                
                issues = subj.get("issues", [])
                if issues:
                    st.markdown("**Issues:**")
                    for issue in issues:
                        st.markdown(f"- ❌ {issue}")
                
                st.markdown(f"**Improved Subject:**")
                st.success(f"`{subj.get('improved_subject', 'N/A')}`")
    
    # Body Analysis
    body_analysis = results.get("body_analysis", [])
    if body_analysis:
        st.markdown("#### 📝 Email Body Analysis")
        for body in body_analysis:
            spam_score = body.get("spam_score", "Unknown")
            score_emoji = "🔴" if spam_score == "High" else "🟡" if spam_score == "Medium" else "🟢"
            with st.expander(f"{score_emoji} {body.get('campaign', 'Campaign')} - {spam_score} risk"):
                issues = body.get("issues_found", [])
                if issues:
                    st.markdown("**Issues Found:**")
                    for issue in issues:
                        st.markdown(f"- ❌ {issue}")
                
                # Show fix examples with before/after
                fix_examples = body.get("fix_examples", [])
                if fix_examples:
                    st.markdown("**How to fix:**")
                    for fix in fix_examples:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("❌ **Before:**")
                            st.code(clean_message_text(fix.get("original", "")), language=None)
                        with col2:
                            st.markdown("✅ **After:**")
                            st.code(clean_message_text(fix.get("fixed", "")), language=None)
                
                # Fallback to recommendations if no fix_examples
                recommendations = body.get("recommendations", [])
                if recommendations and not fix_examples:
                    st.markdown("**Recommendations:**")
                    for rec in recommendations:
                        st.markdown(f"- ✅ {rec}")
    
    # Safe Patterns
    safe_patterns = results.get("safe_patterns", [])
    if safe_patterns:
        st.markdown("#### ✅ What You're Doing Well")
        for pattern in safe_patterns:
            st.markdown(f"- 👍 {pattern}")
    
    # Top Recommendations
    top_recs = results.get("top_recommendations", [])
    if top_recs:
        st.markdown("#### 🎯 Top Priority Fixes")
        for rec in top_recs:
            impact = rec.get("impact", "Medium")
            impact_emoji = "🔴" if impact == "High" else "🟡" if impact == "Medium" else "🟢"
            with st.expander(f"#{rec.get('priority', '?')} - {rec.get('issue', 'Issue')} ({impact_emoji} {impact} impact)"):
                # Show before/after examples
                if rec.get("example_before") and rec.get("example_after"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("❌ **Before:**")
                        st.code(clean_message_text(rec.get("example_before", "")), language=None)
                    with col2:
                        st.markdown("✅ **After:**")
                        st.code(clean_message_text(rec.get("example_after", "")), language=None)
                elif rec.get("fix"):
                    st.markdown(f"**Fix:** {rec.get('fix', 'N/A')}")


def render_strategy_results(results: dict):
    """Render strategic recommendations"""
    if "error" in results:
        st.error(f"Error: {results['error']}")
        if "raw_response" in results and results["raw_response"]:
            with st.expander("🔍 View raw AI response"):
                st.code(results["raw_response"])
        return
    
    if "_note" in results:
        st.warning(results["_note"])
    
    # Funnel Analysis
    if "funnel_analysis" in results:
        st.markdown("#### 📊 Funnel Analysis")
        funnel = results["funnel_analysis"]
        
        if "connection_to_reply" in funnel:
            ctr = funnel["connection_to_reply"]
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Current Rate", ctr.get("current_rate", "N/A"))
            with col2:
                st.metric("Benchmark", ctr.get("benchmark", "N/A"))
            with col3:
                priority = ctr.get("priority", "medium")
                color = "🔴" if priority == "high" else "🟡" if priority == "medium" else "🟢"
                st.metric("Priority", f"{color} {priority.upper()}")
            
            st.info(f"**Gap Analysis:** {ctr.get('gap_analysis', 'N/A')}")
    
    # Channel Strategy
    if "channel_strategy" in results:
        st.markdown("#### 📱 Channel Strategy")
        channel = results["channel_strategy"]
        
        col1, col2 = st.columns(2)
        with col1:
            st.success(f"**Primary Channel:** {channel.get('primary_channel', 'N/A')}")
            st.markdown(f"*{channel.get('reasoning', '')}*")
        with col2:
            st.info(f"**Recommended Mix:** {channel.get('channel_mix', 'N/A')}")
    
    # Quick Wins
    if "quick_wins" in results:
        st.markdown("#### ⚡ Quick Wins")
        for win in results["quick_wins"]:
            effort = win.get("effort", "Medium")
            impact = win.get("impact", "Medium")
            
            effort_emoji = "🟢" if effort == "Low" else "🟡" if effort == "Medium" else "🔴"
            impact_emoji = "🟢" if impact == "High" else "🟡" if impact == "Medium" else "🔴"
            
            st.markdown(f"- {win.get('action', 'Action')} | Effort: {effort_emoji} | Impact: {impact_emoji}")
    
    # Final Recommendation
    if "final_recommendation" in results:
        st.markdown("---")
        st.success(f"💡 **Final Recommendation:** {results['final_recommendation']}")


def render_ab_test_results(results: dict):
    """Render A/B test suggestions"""
    if "error" in results:
        st.error(f"Error: {results['error']}")
        if "raw_response" in results and results["raw_response"]:
            with st.expander("🔍 View raw AI response"):
                st.code(results["raw_response"])
        return
    
    if "_note" in results:
        st.warning(results["_note"])
    
    # Priority Test
    if "priority_test" in results:
        st.markdown("#### 🎯 Priority Test")
        test = results["priority_test"]
        
        st.info(f"**{test.get('test_name', 'Test')}**")
        st.markdown(f"*Hypothesis: {test.get('hypothesis', 'N/A')}*")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Variant A (Control):**")
            variant_a = test.get("variant_a", {})
            st.text(clean_message_text(variant_a.get("full_message", "N/A")))
            st.caption(f"Channel: {variant_a.get('channel', 'N/A')}")
        
        with col2:
            st.markdown("**Variant B (Challenger):**")
            variant_b = test.get("variant_b", {})
            st.text(clean_message_text(variant_b.get("full_message", "N/A")))
            st.caption(f"Channel: {variant_b.get('channel', 'N/A')}")
    
    # Subject Line Tests
    if "subject_line_tests" in results:
        st.markdown("#### 📧 Subject Line Tests")
        for test in results["subject_line_tests"]:
            with st.expander("Subject Line Variants"):
                st.markdown(f"**Current Best:** `{test.get('current_best', 'N/A')}`")
                st.markdown("**Test Variants:**")
                if test.get("variant_a"):
                    st.code(test["variant_a"])
                if test.get("variant_b"):
                    st.code(test["variant_b"])
                if test.get("variant_c"):
                    st.code(test["variant_c"])
    
    # Testing Calendar
    if "testing_calendar" in results:
        st.markdown("#### 📅 Testing Calendar")
        calendar = results["testing_calendar"]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.info(f"**Week 1:**\n{calendar.get('week_1', 'N/A')}")
        with col2:
            st.info(f"**Week 2:**\n{calendar.get('week_2', 'N/A')}")
        with col3:
            st.info(f"**Week 3:**\n{calendar.get('week_3', 'N/A')}")
        with col4:
            st.success(f"**Week 4:**\n{calendar.get('week_4', 'N/A')}")


def render_data_table(df: pd.DataFrame):
    """Render the full data table"""
    st.markdown("### 📋 Full Data")
    
    format_dict = {
        "Open Rate": "{:.1f}%",
        "CTR": "{:.1f}%",
        "Email Reply Rate": "{:.1f}%",
        "Acceptance Rate": "{:.1f}%",
        "LinkedIn Reply Rate": "{:.1f}%",
        "Global Reply Rate": "{:.1f}%",
        "Conversion Rate": "{:.1f}%"
    }
    
    st.dataframe(
        df.style.format(format_dict),
        use_container_width=True,
        hide_index=True
    )
    
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Export to CSV",
        data=csv,
        file_name=f"campaign_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv"
    )


def main():
    """Main application"""
    init_session_state()
    
    # Header
    st.markdown('<p class="main-header">🚀 Campaign Analyzer</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Analyze your LGM campaigns with artificial intelligence</p>', unsafe_allow_html=True)
    
    # Sidebar
    lgm_api_key, gemini_api_key, demo_mode = render_sidebar()
    
    # Main content
    if demo_mode:
        st.info("🎮 **Demo mode activated** - Using fictitious data for demonstration")
        stats_list = get_demo_campaigns()
        campaign_content = get_demo_campaign_content()
        analyzer = MockGeminiAnalyzer()
    else:
        if not lgm_api_key:
            st.warning("⚠️ Enter your LGM API key in the sidebar to start, or enable demo mode.")
            return
        
        client = LGMClient(lgm_api_key)
        
        # Campaign Selection
        st.markdown("### 🎯 Campaign Selection")
        
        if "available_campaigns" not in st.session_state or st.button("🔄 Refresh campaign list"):
            try:
                with st.spinner("Loading campaigns from LGM..."):
                    campaigns = client.get_all_campaigns()
                    st.session_state.available_campaigns = campaigns
            except Exception as e:
                st.error(f"Error loading campaigns: {str(e)}")
                st.session_state.available_campaigns = []
        
        available_campaigns = st.session_state.get("available_campaigns", [])
        
        if not available_campaigns:
            st.warning("⚠️ No campaigns found.")
            return
        
        # Filters
        col1, col2 = st.columns([1, 1])
        with col1:
            status_filter = st.selectbox("Filter by status", ["All", "RUNNING", "PAUSED"])
        with col2:
            sort_by = st.selectbox("Sort by", ["Name (A-Z)", "Leads (High-Low)", "Reply Rate (High-Low)"])
        
        filtered_campaigns = available_campaigns
        if status_filter != "All":
            filtered_campaigns = [c for c in filtered_campaigns if c.get("status") == status_filter]
        
        if sort_by == "Name (A-Z)":
            filtered_campaigns = sorted(filtered_campaigns, key=lambda x: x.get("name", "").lower())
        elif sort_by == "Leads (High-Low)":
            filtered_campaigns = sorted(filtered_campaigns, key=lambda x: x.get("leadsCount", 0), reverse=True)
        elif sort_by == "Reply Rate (High-Low)":
            filtered_campaigns = sorted(filtered_campaigns, key=lambda x: x.get("replyRatePercent", 0), reverse=True)
        
        campaign_options = {
            f"{c['name']} ({c['leadsCount']} leads, {c.get('replyRatePercent', 0)}% reply)": c['id']
            for c in filtered_campaigns
        }
        
        selected_labels = st.multiselect("Select campaigns to analyze", list(campaign_options.keys()))
        
        selected_campaign_ids = [campaign_options[label] for label in selected_labels]
        campaign_names = {c['id']: c['name'] for c in filtered_campaigns}
        
        if not selected_labels:
            st.warning("⚠️ Select at least one campaign.")
            return
        
        st.success(f"✅ {len(selected_labels)} campaign(s) selected")
        
        if st.button("📊 Fetch Statistics", type="primary", use_container_width=True):
            try:
                with st.spinner(f"Fetching stats..."):
                    stats_list = client.get_campaigns_stats_by_ids(selected_campaign_ids, campaign_names)
                    st.session_state.campaign_stats = stats_list
                st.success(f"✅ {len(stats_list)} campaign(s) loaded!")
            except LGMAPIError as e:
                st.error(f"LGM API Error: {str(e)}")
                return
        
        if not st.session_state.campaign_stats:
            st.info("👆 Click to load data")
            return
        
        stats_list = st.session_state.campaign_stats
        campaign_content = {}
        
        if gemini_api_key:
            analyzer = GeminiAnalyzer(gemini_api_key)
        else:
            st.warning("⚠️ Add Gemini API key for real AI analysis.")
            analyzer = MockGeminiAnalyzer()
    
    # Prepare dataframe
    df = stats_to_dataframe(stats_list)
    
    # MAIN TABS: Data vs AI Agent
    main_tabs = st.tabs(["📊 Data", "🤖 AI Agent"])
    
    # ===== DATA TAB =====
    with main_tabs[0]:
        render_metrics_overview(df)
        st.markdown("---")
        
        render_comparison_charts(df)
        st.markdown("---")
        
        render_ranking_table(df)
        st.markdown("---")
        
        render_data_table(df)
    
    # ===== AI AGENT TAB =====
    with main_tabs[1]:
        render_ai_analysis(analyzer, stats_list, campaign_content)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #9ca3af;'>Campaign Analyzer v2.0 | Powered by LGM API + Google Gemini</p>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()