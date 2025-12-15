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
        padding: 1rem;
        border-radius: 0.75rem;
        color: white;
    }
    .insight-box {
        background: #f0f9ff;
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0 0.5rem 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# DEMO DATA
# =============================================================================

def get_demo_campaigns():
    """Return demo campaign data for testing"""
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
            campaign_name="LinkedIn Only Campaign",
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


# =============================================================================
# DATA TAB COMPONENTS
# =============================================================================

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


def render_comparison_table(df: pd.DataFrame):
    """Render the comparison table with winners highlighted"""
    st.markdown("### 🏆 Campaign Comparison")
    
    comparison_cols = ["Campaign", "Open Rate", "Global Reply Rate", "Conversion Rate"]
    df_compare = df[comparison_cols].copy()
    
    metrics = ["Open Rate", "Global Reply Rate", "Conversion Rate"]
    winners = {}
    for metric in metrics:
        if df_compare[metric].max() > 0:
            max_idx = df_compare[metric].idxmax()
            winners[metric] = max_idx
    
    df_display = df_compare.copy()
    for metric in metrics:
        if metric in winners:
            df_display[metric] = df_display.apply(
                lambda row: f"🏆 {row[metric]:.1f}%" if row.name == winners[metric] else f"{row[metric]:.1f}%",
                axis=1
            )
        else:
            df_display[metric] = df_display[metric].apply(lambda x: f"{x:.1f}%")
    
    st.dataframe(df_display, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    cols = st.columns(3)
    for i, metric in enumerate(metrics):
        with cols[i]:
            if metric in winners:
                winner_name = df.loc[winners[metric], "Campaign"]
                st.success(f"**Best {metric}:** {winner_name}")


def render_comparison_chart(df: pd.DataFrame):
    """Render comparison bar chart grouped by campaign"""
    st.markdown("### 📊 Visual Comparison")
    
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
    
    has_email = df["Emails Sent"].sum() > 0
    has_linkedin = df["LinkedIn Sent"].sum() > 0
    
    columns = ["Campaign", "Leads"]
    
    if has_email:
        columns.extend(["Emails Sent", "Emails Opened", "Open Rate", "Email Replies", "Email Reply Rate"])
    
    if has_linkedin:
        columns.extend(["LinkedIn Sent", "LinkedIn Accepted", "Acceptance Rate", "LinkedIn Replies", "LinkedIn Reply Rate"])
    
    columns.extend(["Total Replies", "Global Reply Rate", "Conversions", "Conversion Rate"])
    
    available_columns = [col for col in columns if col in df.columns]
    df_display = df[available_columns].copy()
    
    pct_columns = [col for col in available_columns if "Rate" in col]
    format_dict = {col: "{:.1f}%" for col in pct_columns}
    
    st.dataframe(
        df_display.style.format(format_dict),
        use_container_width=True,
        hide_index=True
    )


def render_data_tab(df: pd.DataFrame):
    """Render the complete Data tab"""
    render_metrics_overview(df)
    st.markdown("---")
    render_comparison_table(df)
    st.markdown("---")
    render_comparison_chart(df)
    st.markdown("---")
    render_full_data_table(df)


# =============================================================================
# AI AGENT TAB - MAIN ANALYSIS RESULTS
# =============================================================================

def render_main_analysis_results(results: dict):
    """Render the main AI analysis results (simple overview)"""
    if "error" in results:
        st.error(f"Analysis error: {results['error']}")
        if "raw_response" in results:
            with st.expander("View raw response"):
                st.code(results.get("raw_response", "No response")[:2000])
        return
    
    if "_note" in results:
        st.warning(results["_note"])
    
    # Section 1: What we learned
    if "learnings" in results:
        st.markdown("### 📈 What We Learned From These Tests")
        learnings = results["learnings"]
        
        for learning in learnings:
            metric = learning.get("metric", "Metric")
            winner = learning.get("winner", "N/A")
            winner_value = learning.get("winner_value", "")
            loser_value = learning.get("loser_value", "")
            reasons = learning.get("reasons", [])
            
            with st.expander(f"**{metric}:** {winner} wins ({winner_value} vs {loser_value})", expanded=True):
                for reason in reasons:
                    st.markdown(f"- {reason}")
        
        if results.get("conclusion"):
            st.info(f"**Key Insight:** {results['conclusion']}")
    
    # Section 2: Spam Check
    if "spam_check" in results:
        st.markdown("### 🚨 Spam Check")
        spam_results = results["spam_check"]
        
        for campaign_spam in spam_results:
            campaign = campaign_spam.get("campaign", "Campaign")
            status = campaign_spam.get("status", "clean")
            issues = campaign_spam.get("issues", [])
            
            if status == "clean":
                st.success(f"**{campaign}:** ✅ Clean (no spam words)")
            else:
                st.warning(f"**{campaign}:** ⚠️ {len(issues)} issue(s)")
                for issue in issues:
                    word = issue.get("word", "")
                    location = issue.get("location", "")
                    replacement = issue.get("replacement", "")
                    st.markdown(f"- `{word}` in {location} → Replace with `{replacement}`")
    
    # Section 3: Optimal Campaign
    if "optimal_campaign" in results:
        st.markdown("### ✏️ Recommended: The Optimal Campaign")
        optimal = results["optimal_campaign"]
        
        st.markdown("**Combining the best elements from each campaign:**")
        
        if optimal.get("subject"):
            st.markdown(f"**Subject:** `{optimal['subject']}`")
            if optimal.get("subject_from"):
                st.caption(f"(inspired by {optimal['subject_from']})")
        
        if optimal.get("body"):
            st.markdown("**Body:**")
            st.code(clean_message_text(optimal["body"]), language=None)
            if optimal.get("body_from"):
                st.caption(f"(structure from {optimal['body_from']})")
        
        if optimal.get("linkedin"):
            st.markdown("**LinkedIn:**")
            st.code(clean_message_text(optimal["linkedin"]), language=None)
        
        if optimal.get("why"):
            st.success(f"**Why this should work:** {optimal['why']}")
    
    # Section 4: Next A/B Test
    if "next_ab_test" in results:
        st.markdown("### 🧪 Next A/B Test To Run")
        test = results["next_ab_test"]
        
        st.markdown(f"**Variable to test:** {test.get('variable', 'N/A')}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Variant A:**")
            st.code(clean_message_text(test.get("variant_a", "N/A")), language=None)
        with col2:
            st.markdown("**Variant B:**")
            st.code(clean_message_text(test.get("variant_b", "N/A")), language=None)
        
        if test.get("hypothesis"):
            st.info(f"**Hypothesis:** {test['hypothesis']}")
        
        if test.get("duration"):
            st.caption(f"⏱️ Recommended duration: {test['duration']}")


# =============================================================================
# AI AGENT TAB - DETAILED ANALYSIS COMPONENTS
# =============================================================================

def render_copywriting_results(results: dict):
    """Render detailed copywriting analysis"""
    if "error" in results:
        st.error(f"Error: {results['error']}")
        return
    
    if "_note" in results:
        st.warning(results["_note"])
    
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
    
    if "message_improvements" in results:
        st.markdown("#### ✍️ Message Improvements")
        for msg in results["message_improvements"]:
            with st.expander(f"📝 {msg.get('campaign', 'Campaign')}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Original:**")
                    st.text(clean_message_text(msg.get("original_message", "N/A")))
                with col2:
                    st.markdown("**Improved:**")
                    st.text(clean_message_text(msg.get("improved_version", "N/A")))


def render_spam_results(results: dict):
    """Render detailed spam analysis"""
    if "error" in results:
        st.error(f"Error: {results['error']}")
        return
    
    if "_note" in results:
        st.warning(results["_note"])
    
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
    
    if results.get("overall_summary"):
        st.info(f"📋 **Summary:** {results['overall_summary']}")
    
    spam_words = results.get("spam_words_found", [])
    if spam_words:
        st.markdown("#### 🔍 Spam Triggers Found")
        for item in spam_words:
            risk_emoji = "🔴" if item.get("risk_level") == "High" else "🟡" if item.get("risk_level") == "Medium" else "🟢"
            with st.expander(f"{risk_emoji} \"{item.get('word_or_phrase', 'N/A')}\" in {item.get('location', 'N/A')}"):
                st.markdown(f"**Risk Level:** {item.get('risk_level', 'N/A')}")
                st.markdown(f"**Why it's risky:** {item.get('why_its_risky', 'N/A')}")
                if item.get("original_sentence"):
                    st.markdown("**Original:**")
                    st.code(clean_message_text(item.get("original_sentence", "")), language=None)
                if item.get("suggested_replacement"):
                    st.markdown("**Replace with:**")
                    st.success(clean_message_text(item.get("suggested_replacement", "")))
    else:
        st.success("✅ No major spam triggers detected!")


def render_strategy_results(results: dict):
    """Render strategy analysis"""
    if "error" in results:
        st.error(f"Error: {results['error']}")
        return
    
    if "_note" in results:
        st.warning(results["_note"])
    
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
    
    if "channel_strategy" in results:
        st.markdown("#### 📱 Channel Strategy")
        channel = results["channel_strategy"]
        col1, col2 = st.columns(2)
        with col1:
            st.success(f"**Primary Channel:** {channel.get('primary_channel', 'N/A')}")
            st.markdown(f"*{channel.get('reasoning', '')}*")
        with col2:
            st.info(f"**Recommended Mix:** {channel.get('channel_mix', 'N/A')}")


def render_ab_test_results(results: dict):
    """Render A/B test suggestions"""
    if "error" in results:
        st.error(f"Error: {results['error']}")
        return
    
    if "_note" in results:
        st.warning(results["_note"])
    
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
        with col2:
            st.markdown("**Variant B (Challenger):**")
            variant_b = test.get("variant_b", {})
            st.text(clean_message_text(variant_b.get("full_message", "N/A")))
    
    if "subject_line_tests" in results:
        st.markdown("#### 📧 Subject Line Tests")
        for test in results["subject_line_tests"]:
            with st.expander(f"Test: {test.get('current_best', 'Subject test')}"):
                st.markdown(f"**Variant A:** `{test.get('variant_a', 'N/A')}`")
                st.markdown(f"**Variant B:** `{test.get('variant_b', 'N/A')}`")
                st.markdown(f"**Variant C:** `{test.get('variant_c', 'N/A')}`")


# =============================================================================
# AI AGENT TAB - MAIN COMPONENT
# =============================================================================

def render_ai_agent_tab(analyzer, stats_list: list[CampaignStats], campaign_content: dict):
    """Render the AI Agent tab with simple overview + detailed analysis dropdown"""
    
    if 'business_context' in st.session_state:
        analyzer.set_business_context(st.session_state.business_context)
    
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
    
    if templates_by_campaign:
        st.success(f"✅ Message templates found for {len(templates_by_campaign)} campaign(s)")
    else:
        st.info("ℹ️ No message templates found. AI will analyze based on performance data only.")
    
    # MAIN ANALYSIS
    st.markdown("---")
    st.markdown("## 🚀 Quick Analysis")
    
    if st.button("🚀 Analyze My Campaigns", type="primary", use_container_width=True, key="main_analyze_btn"):
        with st.spinner("🤖 AI is analyzing your campaigns... (this may take 30 seconds)"):
            results = analyzer.full_analysis(campaigns_data, templates_by_campaign)
            st.session_state.main_analysis_results = results
    
    if 'main_analysis_results' in st.session_state:
        render_main_analysis_results(st.session_state.main_analysis_results)
    
    # DETAILED ANALYSIS (Dropdown)
    st.markdown("---")
    with st.expander("📊 Detailed Analysis (click to expand)", expanded=False):
        st.markdown("Run in-depth analyses on specific aspects of your campaigns.")
        
        detail_tabs = st.tabs(["✍️ Copywriting", "🚨 Spam Words", "🎯 Strategy", "🧪 A/B Tests"])
        
        with detail_tabs[0]:
            st.markdown("**Deep dive into hooks, CTAs, and message structure**")
            if st.button("Run Copywriting Analysis", key="copy_btn", type="primary"):
                with st.spinner("Analyzing..."):
                    results = analyzer.analyze_copywriting(campaigns_data, templates_by_campaign)
                    st.session_state.copywriting_results = results
            if 'copywriting_results' in st.session_state:
                render_copywriting_results(st.session_state.copywriting_results)
        
        with detail_tabs[1]:
            st.markdown("**Check for spam triggers that hurt deliverability**")
            if st.button("Run Spam Analysis", key="spam_btn", type="primary"):
                with st.spinner("Analyzing..."):
                    results = analyzer.analyze_spam(campaigns_data, templates_by_campaign)
                    st.session_state.spam_results = results
            if 'spam_results' in st.session_state:
                render_spam_results(st.session_state.spam_results)
        
        with detail_tabs[2]:
            st.markdown("**Channel strategy and funnel optimization**")
            if st.button("Run Strategy Analysis", key="strategy_btn", type="primary"):
                with st.spinner("Analyzing..."):
                    results = analyzer.get_strategic_recommendations(campaigns_data, templates_by_campaign)
                    st.session_state.strategy_results = results
            if 'strategy_results' in st.session_state:
                render_strategy_results(st.session_state.strategy_results)
        
        with detail_tabs[3]:
            st.markdown("**Generate specific A/B test variants**")
            if st.button("Generate A/B Tests", key="ab_btn", type="primary"):
                with st.spinner("Generating..."):
                    results = analyzer.generate_ab_tests(campaigns_data, templates_by_campaign)
                    st.session_state.ab_results = results
            if 'ab_results' in st.session_state:
                render_ab_test_results(st.session_state.ab_results)
    
    # ASK AI
    st.markdown("---")
    st.markdown("### 💬 Ask AI")
    st.caption("Ask follow-up questions about your campaigns (answers use analysis results)")
    
    user_question = st.text_area(
        "Your question",
        placeholder="Examples:\n- Why does Campaign A have better open rates?\n- Rewrite my subject line to be shorter\n- What's the best CTA for my target audience?",
        height=100,
        key="ai_question"
    )
    
    if st.button("💬 Ask", key="ask_btn", type="secondary", use_container_width=True):
        if user_question.strip():
            with st.spinner("Thinking..."):
                analysis_context = ""
                if 'main_analysis_results' in st.session_state and "error" not in st.session_state.main_analysis_results:
                    analysis_context = f"\n\nPREVIOUS ANALYSIS RESULTS:\n{json.dumps(st.session_state.main_analysis_results, indent=2, default=str)}"
                
                full_question = user_question + analysis_context
                response = analyzer.chat(full_question, campaigns_data, templates_by_campaign)
                st.session_state.chat_response = response
        else:
            st.warning("Please enter a question")
    
    if 'chat_response' in st.session_state:
        st.markdown("---")
        st.markdown("**🤖 AI Response:**")
        st.markdown(st.session_state.chat_response)


# =============================================================================
# SIDEBAR
# =============================================================================

def render_sidebar():
    """Render the sidebar with configuration"""
    st.sidebar.markdown("## ⚙️ Configuration")
    
    st.sidebar.markdown("### 🔑 API Keys")
    lgm_api_key = st.sidebar.text_input("LGM API Key", type="password", key="lgm_key")
    gemini_api_key = st.sidebar.text_input("Gemini API Key", type="password", key="gemini_key")
    
    st.sidebar.markdown("### 🎮 Mode")
    demo_mode = st.sidebar.checkbox("Demo Mode", value=True, help="Use sample data for testing")
    
    st.sidebar.markdown("### 📝 Business Context")
    st.sidebar.caption("This context helps AI give relevant recommendations")
    
    with st.sidebar.expander("Edit Business Context", expanded=False):
        product = st.text_input("Product", value="AI Agent for E-commerce", key="ctx_product")
        product_description = st.text_area(
            "Product Description",
            value="An intelligent AI agent that monitors, detects, and alerts e-commerce merchants about critical events affecting their online stores.",
            key="ctx_description", height=80
        )
        target = st.text_input(
            "Target Audience",
            value="E-commerce merchants, Shopify store owners, DTC brands, E-commerce managers",
            key="ctx_target"
        )
        pain_points = st.text_area(
            "Pain Points We Solve",
            value="Site crashes going unnoticed, payment failures, traffic drops, too many false alerts, manual monitoring",
            key="ctx_pain", height=80
        )
        key_differentiators = st.text_area(
            "Key Differentiators",
            value="Only statistically significant alerts (no noise), Personalized detection per store, Seasonality-aware, Works in Slack + Dashboard",
            key="ctx_diff", height=80
        )
        goal = st.text_input(
            "Sales Goal",
            value="Connect with e-commerce decision makers → Book demo → Close deals",
            key="ctx_goal"
        )
        
        st.session_state.business_context = {
            "product": product,
            "product_description": product_description,
            "target": target,
            "pain_points": pain_points,
            "key_differentiators": key_differentiators,
            "goal": goal
        }
    
    return lgm_api_key, gemini_api_key, demo_mode


# =============================================================================
# MAIN
# =============================================================================

def main():
    st.markdown('<p class="main-header">🚀 Campaign Analyzer</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Analyze your A/B tests and optimize future campaigns</p>', unsafe_allow_html=True)
    
    lgm_api_key, gemini_api_key, demo_mode = render_sidebar()
    
    if "campaign_stats" not in st.session_state:
        st.session_state.campaign_stats = []
    
    if demo_mode:
        stats_list = get_demo_campaigns()
        campaign_content = get_demo_campaign_content()
        analyzer = MockGeminiAnalyzer()
    else:
        if not lgm_api_key:
            st.warning("⚠️ Enter your LGM API key in the sidebar, or enable Demo Mode.")
            return
        
        client = LGMClient(lgm_api_key)
        
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
                with st.spinner("Fetching stats..."):
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
    
    df = stats_to_dataframe(stats_list)
    
    tab_data, tab_ai = st.tabs(["📊 Data", "🤖 AI Agent"])
    
    with tab_data:
        render_data_tab(df)
    
    with tab_ai:
        render_ai_agent_tab(analyzer, stats_list, campaign_content)
    
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #9ca3af;'>Campaign Analyzer v3.0 | Powered by LGM API + Google Gemini</p>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()