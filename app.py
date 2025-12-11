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
        - 📊 Compare performance
        - 🎯 Identify winning patterns
        - 💡 Suggest optimizations
        - 🧪 Propose A/B tests
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
            "Campaign": stat.campaign_name,
            "ID": stat.campaign_id,
            "Leads": stat.total_leads,
            "Emails Sent": stat.emails_sent,
            "Emails Opened": stat.emails_opened,
            "Open Rate": stat.open_rate,
            "Emails Clicked": stat.emails_clicked,
            "CTR": stat.click_rate,
            "Emails Replied": stat.emails_replied,
            "Reply Rate Email": stat.email_reply_rate,
            "LinkedIn Sent": stat.linkedin_sent,
            "LinkedIn Accepted": stat.linkedin_accepted,
            "Acceptance Rate": stat.linkedin_acceptance_rate,
            "LinkedIn Replied": stat.linkedin_replied,
            "Reply Rate LinkedIn": stat.linkedin_reply_rate,
            "Total Responses": stat.total_replies,
            "Reply Rate Global": stat.overall_reply_rate,
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
        avg_reply_rate = df["Reply Rate Global"].mean()
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
        # Email metrics comparison
        fig = make_subplots(rows=1, cols=2, subplot_titles=("Open Rate", "Reply Rate Email"))
        
        fig.add_trace(
            go.Bar(name="Open Rate", x=df["Campaign"], y=df["Open Rate"], marker_color="#3b82f6"),
            row=1, col=1
        )
        fig.add_trace(
            go.Bar(name="Reply Rate", x=df["Campaign"], y=df["Reply Rate Email"], marker_color="#10b981"),
            row=1, col=2
        )
        
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # LinkedIn metrics comparison
        fig = make_subplots(rows=1, cols=2, subplot_titles=("Acceptance Rate", "Reply Rate LinkedIn"))
        
        fig.add_trace(
            go.Bar(name="Acceptance", x=df["Campaign"], y=df["Acceptance Rate"], marker_color="#8b5cf6"),
            row=1, col=1
        )
        fig.add_trace(
            go.Bar(name="Reply Rate", x=df["Campaign"], y=df["Reply Rate LinkedIn"], marker_color="#f59e0b"),
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
    display_cols = ["Rang", "Campaign", "Leads", "Open Rate", "Reply Rate Global", "Conversion Rate", "Score"]
    
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
    st.markdown("### 🤖 AI Analysis")
    
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
    
    analysis_tabs = st.tabs(["📊 Analysis", "⚔️ Comparison", "🧪 A/B Suggestions", "✨ Generate Variants"])
    
    with analysis_tabs[0]:
        if st.button("🔍 Run Full Analysis", key="analyze_btn"):
            with st.spinner("Analyzing with Gemini..."):
                results = analyzer.analyze_campaigns(campaigns_data, campaign_content)
                st.session_state.analysis_results = results
        
        if st.session_state.analysis_results:
            render_analysis_results(st.session_state.analysis_results)
    
    with analysis_tabs[1]:
        if st.button("⚔️ Compare Campaigns", key="compare_btn"):
            with st.spinner("Comparing..."):
                results = analyzer.compare_campaigns(campaigns_data, campaign_content)
                render_comparison_results(results)
    
    with analysis_tabs[2]:
        if st.button("🧪 Suggest A/B Tests", key="suggest_btn"):
            with st.spinner("Generating suggestions..."):
                results = analyzer.suggest_next_tests(campaigns_data, campaign_content)
                render_suggestions_results(results)
    
    with analysis_tabs[3]:
        st.markdown("Select the winning campaign to generate variants:")
        winner = st.selectbox(
            "Reference campaign",
            options=[stat.campaign_name for stat in stats_list]
        )
        
        num_variants = st.slider("Number of variants", 2, 5, 3)
        
        if st.button("✨ Generate Variants", key="variants_btn"):
            winning_content = campaign_content.get(winner, {})
            with st.spinner("Generating variants..."):
                results = analyzer.generate_variants(winning_content, num_variants)
                render_variants_results(results)


def render_analysis_results(results: dict):
    """Render the analysis results"""
    if "error" in results:
        st.error(f"Analysis error: {results['error']}")
        if "raw_response" in results:
            with st.expander("Raw response"):
                st.text(results["raw_response"])
        return
    
    # Demo mode warning
    if "_note" in results:
        st.warning(results["_note"])
    
    # Global summary
    if "global_summary" in results:
        st.markdown("#### 📋 Global Summary")
        summary = results["global_summary"]
        col1, col2 = st.columns(2)
        with col1:
            st.success(f"🏆 **Best campaign:** {summary.get('best_campaign', 'N/A')}")
        with col2:
            st.error(f"📉 **Needs improvement:** {summary.get('worst_campaign', 'N/A')}")
        st.info(f"📊 **Trend:** {summary.get('general_trend', 'N/A')}")
    
    # Open rate analysis
    if "open_rate_analysis" in results:
        st.markdown("#### 📧 Open Rate Analysis")
        oar = results["open_rate_analysis"]
        st.markdown(f"**Average:** {oar.get('average', 'N/A')}")
        st.markdown(f"**Best subject:** `{oar.get('best_subject', 'N/A')}`")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("✅ **Winning patterns:**")
            for p in oar.get("winning_patterns", []):
                st.markdown(f"- {p}")
        with col2:
            st.markdown("❌ **Losing patterns:**")
            for p in oar.get("losing_patterns", []):
                st.markdown(f"- {p}")
    
    # Patterns identified
    if "identified_patterns" in results:
        st.markdown("#### 🔍 Patterns Identified")
        patterns = results["identified_patterns"]
        
        for category, items in patterns.items():
            with st.expander(f"📌 {category.title()}"):
                for item in items:
                    st.markdown(f"- {item}")
    
    # Global score
    if "global_score" in results:
        st.markdown("#### 🎯 Global Score")
        score = results["global_score"]
        st.markdown(f"**Score:** {score.get('score', 'N/A')}")
        st.markdown(f"**Justification:** {score.get('justification', 'N/A')}")


def render_comparison_results(results: dict):
    """Render comparison results"""
    if "error" in results:
        st.error(f"Error: {results['error']}")
        return
    
    if "_note" in results:
        st.warning(results["_note"])
    
    # Ranking
    if "ranking" in results:
        st.markdown("#### 🏆 Ranking")
        for item in results["ranking"]:
            with st.expander(f"#{item.get('rank', '?')} - {item.get('campaign', 'N/A')} ({item.get('global_score', 'N/A')})"):
                st.markdown("**Strengths:**")
                for f in item.get("strengths", []):
                    st.markdown(f"- ✅ {f}")
                if item.get("weaknesses"):
                    st.markdown("**Weaknesses:**")
                    for f in item.get("weaknesses", []):
                        st.markdown(f"- ❌ {f}")
    
    # Conclusion
    if "conclusion" in results:
        st.info(f"💡 **Conclusion:** {results['conclusion']}")


def render_suggestions_results(results: dict):
    """Render A/B test suggestions"""
    if "error" in results:
        st.error(f"Error: {results['error']}")
        return
    
    if "_note" in results:
        st.warning(results["_note"])
    
    # Priority tests
    if "priority_tests" in results:
        st.markdown("#### 🎯 Priority Tests")
        for test in results["priority_tests"]:
            with st.expander(f"P{test.get('priority', '?')} - {test.get('test_type', 'N/A')} ({test.get('potential_impact', 'N/A')})"):
                st.markdown(f"**Hypothesis:** {test.get('hypothesis', 'N/A')}")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Variant A:** {test.get('variant_A', 'N/A')}")
                with col2:
                    st.markdown(f"**Variant B:** {test.get('variant_B', 'N/A')}")
    
    # Strategic advice
    if "strategic_advice" in results:
        st.success(f"💡 **Strategic Advice:** {results['strategic_advice']}")


def render_variants_results(results: dict):
    """Render generated variants"""
    if "error" in results:
        st.error(f"Error: {results['error']}")
        return
    
    if "_note" in results:
        st.warning(results["_note"])
    
    # Subject variants
    if "subject_variants" in results:
        st.markdown("#### 📧 Subject Variants")
        for v in results["subject_variants"]:
            st.code(v.get("subject", "N/A"))
            st.markdown(f"*Angle: {v.get('angle', 'N/A')}*")
            st.markdown("---")
    
    # Body variants
    if "email_body_variants" in results:
        st.markdown("#### 📝 Email Body Variants")
        for v in results["email_body_variants"]:
            with st.expander(f"{v.get('version', 'N/A')}"):
                st.text(v.get("body", "N/A"))


def render_data_table(df: pd.DataFrame):
    """Render the full data table"""
    st.markdown("### 📋 Full Data")
    
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
        
        # Campaign ID input section
        st.markdown("### 🎯 Campaign Selection")
        
        st.markdown("""
        <div style="background-color: #dbeafe; border-left: 4px solid #3b82f6; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;">
        <strong>💡 How to find your Campaign IDs?</strong><br>
        1. Go to <a href="https://app.lagrowthmachine.com" target="_blank">app.lagrowthmachine.com</a><br>
        2. Open a campaign<br>
        3. The ID is in the URL: <code>app.lagrowthmachine.com/campaigns/<strong>CAMPAIGN_ID</strong>/...</code>
        </div>
        """, unsafe_allow_html=True)
        
        # Text area for campaign IDs
        campaign_input = st.text_area(
            "Enter your Campaign IDs (one per line)",
            placeholder="example-campaign-id-1\nexample-campaign-id-2\nexample-campaign-id-3",
            height=150,
            help="Copy the IDs from your LGM campaign URLs"
        )
        
        # Optional: Campaign names
        with st.expander("➕ Add custom names (optional)"):
            st.markdown("Format: `campaign_id:Campaign Name` (one per line)")
            names_input = st.text_area(
                "Campaign names",
                placeholder="campaign-id-1:Email > LinkedIn CEO #1\ncampaign-id-2:LinkedIn > Email CMO #1",
                height=100
            )
        
        # Parse campaign IDs
        campaign_ids = []
        campaign_names = {}
        
        if campaign_input:
            campaign_ids = [cid.strip() for cid in campaign_input.strip().split("\n") if cid.strip()]
        
        if names_input:
            for line in names_input.strip().split("\n"):
                if ":" in line:
                    cid, name = line.split(":", 1)
                    campaign_names[cid.strip()] = name.strip()
        
        if not campaign_ids:
            st.warning("⚠️ Enter at least one Campaign ID to start the analysis.")
            return
        
        # Fetch stats button
        if st.button("📊 Fetch Statistics", type="primary", use_container_width=True):
            try:
                with st.spinner(f"Fetching stats for {len(campaign_ids)} campaign(s)..."):
                    stats_list = client.get_campaigns_stats_by_ids(campaign_ids, campaign_names)
                    st.session_state.campaign_stats = stats_list
                st.success(f"✅ {len(stats_list)} campaign(s) loaded successfully!")
            except LGMAPIError as e:
                st.error(f"LGM API Error: {str(e)}")
                return
        
        # Use cached stats if available
        if not st.session_state.campaign_stats:
            st.info("👆 Click the button above to load data")
            return
        
        stats_list = st.session_state.campaign_stats
        campaign_content = {}  # Can be extended to fetch content
        
        # Initialize Gemini analyzer
        if gemini_api_key:
            analyzer = GeminiAnalyzer(gemini_api_key)
        else:
            st.warning("⚠️ Without Gemini key, AI analysis will use demo responses.")
            analyzer = MockGeminiAnalyzer()
    
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