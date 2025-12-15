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
            options=["AI Agent Sales", "Custom"],
            index=0,
            help="Select your business type for tailored AI analysis"
        )
        
        if business_preset == "AI Agent Sales":
            business_context = {
                "product": "AI Agent",
                "goal": "Connect with leads → Book meetings → Close deals",
                "target": "Decision makers (CEOs, CTOs, Founders)",
                "industry": "B2B SaaS",
                "additional": ""
            }
        else:
            with st.expander("📝 Custom business context"):
                business_context = {
                    "product": st.text_input("Product/Service", value="AI Agent"),
                    "goal": st.text_input("Goal", value="Connect → Meeting → Close"),
                    "target": st.text_input("Target ICP", value="Decision makers"),
                    "industry": st.text_input("Industry", value="B2B SaaS"),
                    "additional": st.text_area("Additional context", value="", height=80)
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
    """Render the AI analysis section with new focused tabs"""
    st.markdown("### 🤖 AI Analysis")
    
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
    
    # New tabs
    analysis_tabs = st.tabs(["✍️ Copywriting", "🎯 Strategy", "🧪 A/B Tests", "💬 Ask AI"])
    
    with analysis_tabs[0]:
        st.markdown("**Deep analysis of your message copywriting**")
        st.caption("Focus on hooks, CTAs, tone, and what makes messages work or fail.")
        
        if st.button("✍️ Analyze Copywriting", key="copy_btn", type="primary", use_container_width=True):
            with st.spinner("Analyzing copywriting with AI..."):
                results = analyzer.analyze_copywriting(campaigns_data, templates_by_campaign)
                st.session_state.copywriting_results = results
        
        if 'copywriting_results' in st.session_state:
            render_copywriting_results(st.session_state.copywriting_results)
    
    with analysis_tabs[1]:
        st.markdown("**Strategic recommendations for your funnel**")
        st.caption("Channel strategy, audience insights, and 90-day roadmap.")
        
        if st.button("🎯 Get Strategic Recommendations", key="strategy_btn", type="primary", use_container_width=True):
            with st.spinner("Generating strategic recommendations..."):
                results = analyzer.get_strategic_recommendations(campaigns_data, templates_by_campaign)
                st.session_state.strategy_results = results
        
        if 'strategy_results' in st.session_state:
            render_strategy_results(st.session_state.strategy_results)
    
    with analysis_tabs[2]:
        st.markdown("**Concrete A/B tests with ready-to-use messages**")
        st.caption("Not just ideas - actual messages you can copy and test.")
        
        if st.button("🧪 Generate A/B Tests", key="ab_btn", type="primary", use_container_width=True):
            with st.spinner("Generating A/B test suggestions..."):
                results = analyzer.generate_ab_tests(campaigns_data, templates_by_campaign)
                st.session_state.ab_results = results
        
        if 'ab_results' in st.session_state:
            render_ab_test_results(st.session_state.ab_results)
    
    with analysis_tabs[3]:
        st.markdown("**Ask anything about your campaigns**")
        st.caption("Get specific answers, rewrite messages, or dive deeper into any topic.")
        
        user_question = st.text_area(
            "Your question",
            placeholder="Examples:\n- Why is my Food campaign underperforming?\n- Rewrite my LinkedIn message to be shorter\n- What's the ideal follow-up sequence?",
            height=100
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
            st.markdown("### 🤖 AI Response")
            st.markdown(st.session_state.chat_response)


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
                    st.code(hook.get("hook", "N/A"))
                    st.markdown(f"*Campaign: {hook.get('campaign', 'N/A')}*")
                    st.markdown(f"**Why it works:** {hook.get('why_it_works', 'N/A')}")
        
        with col2:
            st.markdown("**❌ Worst Hooks:**")
            for hook in hooks.get("worst_hooks", []):
                with st.expander(f"📉 {hook.get('reply_rate', 'N/A')} reply rate"):
                    st.code(hook.get("hook", "N/A"))
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
                st.code(improvement.get("original_message", "N/A"))
                
                st.markdown("**Improved Version:**")
                st.code(improvement.get("improved_version", "N/A"))
                
                if improvement.get("changes_made"):
                    st.markdown("**Changes Made:**")
                    for change in improvement["changes_made"]:
                        st.markdown(f"- {change}")


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
            st.code(variant_a.get("full_message", "N/A"))
        
        with col2:
            st.markdown("**Variant B (Challenger):**")
            variant_b = test.get("variant_b", {})
            st.code(variant_b.get("full_message", "N/A"))
    
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
    
    # Render sections
    df = stats_to_dataframe(stats_list)
    
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
        "<p style='text-align: center; color: #9ca3af;'>Campaign Analyzer v2.0 | Powered by LGM API + Google Gemini</p>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()