"""
Gemini AI Analyzer
Analyzes campaign data and provides insights and recommendations
Focused on copywriting analysis for AI Agent Sales
"""

import google.generativeai as genai
from typing import Optional
import json
import re


class GeminiAnalyzer:
    """AI-powered campaign analyzer using Google Gemini"""
    
    def __init__(self, api_key: str, business_context: dict = None):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.business_context = business_context or {
            "product": "AI Agent for E-commerce",
            "product_description": "An intelligent AI agent that monitors, detects, and alerts e-commerce merchants about critical events affecting their online stores. Features include: real-time Slack/dashboard alerts, ML-powered anomaly detection with seasonality awareness, store-specific calibration, statistical relevance filtering (no false positives), and AI chatbot for alert explanations.",
            "key_differentiators": "1) Only statistically significant alerts (no noise), 2) Personalized detection per store, 3) Seasonality-aware, 4) Works in Slack + Dashboard, 5) AI explains the 'why' behind alerts, 6) Roadmap to auto-fix issues",
            "goal": "Connect with e-commerce decision makers → Book demo/meeting → Close deals",
            "target": "E-commerce merchants and store owners (primarily Shopify), DTC brands, E-commerce managers, CTOs/Technical leads at online retailers",
            "pain_points": "Site crashes going unnoticed, payment failures, traffic drops, too many false alerts from other tools, lack of context on why issues happen, manual monitoring is time-consuming",
            "industry": "E-commerce / SaaS",
            "integrations": "Shopify (primary), Slack, Klaviyo (email), Google Analytics/Ads, Facebook/Meta Ads, Yotpo (reviews)",
            "additional": ""
        }
    
    def set_business_context(self, context: dict):
        """Update the business context"""
        self.business_context = context
    
    def _get_context_prompt(self) -> str:
        """Build the business context section for prompts"""
        return f"""## BUSINESS CONTEXT:
- Product: {self.business_context.get('product', 'AI Agent for E-commerce')}
- What it does: {self.business_context.get('product_description', 'AI-powered monitoring and alerting for e-commerce stores')}
- Key differentiators: {self.business_context.get('key_differentiators', 'Statistically significant alerts only, personalized per store, seasonality-aware')}
- Sales Goal: {self.business_context.get('goal', 'Connect → Demo → Close')}
- Target ICP: {self.business_context.get('target', 'E-commerce merchants, Shopify store owners, DTC brands')}
- Pain points we solve: {self.business_context.get('pain_points', 'Unnoticed site issues, false alerts, manual monitoring')}
- Industry: {self.business_context.get('industry', 'E-commerce / SaaS')}
- Additional info: {self.business_context.get('additional', 'None')}
"""

    def analyze_copywriting(self, campaigns_data: list[dict], templates_by_campaign: dict) -> dict:
        """
        Deep analysis of message copywriting
        Focus on: hooks, CTAs, tone, structure, what works vs what doesn't
        """
        prompt = self._build_copywriting_prompt(campaigns_data, templates_by_campaign)
        
        try:
            response = self.model.generate_content(prompt)
            return self._extract_json(response.text)
        except Exception as e:
            return {"error": str(e), "raw_response": None}
    
    def get_strategic_recommendations(self, campaigns_data: list[dict], templates_by_campaign: dict) -> dict:
        """
        Strategic recommendations based on business context
        Focus on: funnel optimization, channel strategy, next steps
        """
        prompt = self._build_strategic_prompt(campaigns_data, templates_by_campaign)
        
        try:
            response = self.model.generate_content(prompt)
            return self._extract_json(response.text)
        except Exception as e:
            return {"error": str(e), "raw_response": None}
    
    def analyze_spam(self, campaigns_data: list[dict], templates_by_campaign: dict) -> dict:
        """
        Dedicated spam words analysis for email deliverability
        """
        prompt = self._build_spam_prompt(campaigns_data, templates_by_campaign)
        
        try:
            response = self.model.generate_content(prompt)
            return self._extract_json(response.text)
        except Exception as e:
            return {"error": str(e), "raw_response": None}
    
    def generate_ab_tests(self, campaigns_data: list[dict], templates_by_campaign: dict) -> dict:
        """
        Generate concrete A/B test suggestions with actual message examples
        """
        prompt = self._build_ab_test_prompt(campaigns_data, templates_by_campaign)
        
        try:
            response = self.model.generate_content(prompt)
            return self._extract_json(response.text)
        except Exception as e:
            return {"error": str(e), "raw_response": None}
    
    def chat(self, question: str, campaigns_data: list[dict], templates_by_campaign: dict) -> str:
        """
        Free-form chat about campaigns
        User can ask any question about their data
        """
        prompt = self._build_chat_prompt(question, campaigns_data, templates_by_campaign)
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _build_copywriting_prompt(self, campaigns_data: list[dict], templates_by_campaign: dict) -> str:
        """Build prompt for deep copywriting analysis"""
        data_str = json.dumps(campaigns_data, indent=2, default=str)
        templates_str = json.dumps(templates_by_campaign, indent=2, default=str) if templates_by_campaign else "No templates available"
        
        return f"""Analyze these B2B outreach campaigns. Respond ONLY with valid JSON, no other text.

{self._get_context_prompt()}

CAMPAIGN DATA:
{data_str}

MESSAGE TEMPLATES:
{templates_str}

IMPORTANT FOR MESSAGE IMPROVEMENTS:
When writing improved versions of messages, make sure to AVOID spam trigger words like:
- Urgency words: "Act now", "Limited time", "Urgent", "Immediately"
- Money words: "Free", "Discount", "Save", "Cheap", "$$"
- Promise words: "Guarantee", "No risk", "100%"
- Pressure words: "Click here", "Sign up free", "Order now"
- Hype words: "Amazing", "Incredible", "Revolutionary"
Write professional, conversational messages that won't trigger spam filters.

Respond with this exact JSON structure:
{{
    "executive_summary": {{
        "main_insight": "string",
        "biggest_opportunity": "string",
        "quick_win": "string"
    }},
    "hook_analysis": {{
        "best_hooks": [
            {{"hook": "string", "campaign": "string", "reply_rate": "string", "why_it_works": "string"}}
        ],
        "worst_hooks": [
            {{"hook": "string", "campaign": "string", "reply_rate": "string", "why_it_fails": "string"}}
        ],
        "hook_patterns": ["string"]
    }},
    "cta_analysis": {{
        "best_ctas": ["string"],
        "worst_ctas": ["string"],
        "recommendations": ["string"]
    }},
    "message_improvements": [
        {{
            "original_message": "string",
            "campaign": "string",
            "current_reply_rate": "string",
            "improved_version": "string (must be spam-free)",
            "changes_made": ["string"],
            "expected_improvement": "string"
        }}
    ]
}}

IMPORTANT: Output ONLY the JSON object. No markdown, no explanation, no code blocks. Just the raw JSON."""

    def _build_strategic_prompt(self, campaigns_data: list[dict], templates_by_campaign: dict) -> str:
        """Build prompt for strategic recommendations"""
        data_str = json.dumps(campaigns_data, indent=2, default=str)
        templates_str = json.dumps(templates_by_campaign, indent=2, default=str) if templates_by_campaign else "No templates available"
        
        return f"""Provide strategic recommendations for these B2B campaigns. Respond ONLY with valid JSON.

{self._get_context_prompt()}

CAMPAIGN DATA:
{data_str}

MESSAGE TEMPLATES:
{templates_str}

Respond with this exact JSON structure:
{{
    "funnel_analysis": {{
        "connection_to_reply": {{
            "current_rate": "string",
            "benchmark": "string",
            "gap_analysis": "string",
            "priority": "high/medium/low"
        }}
    }},
    "channel_strategy": {{
        "primary_channel": "string",
        "reasoning": "string",
        "channel_mix": "string",
        "sequence_recommendation": "string"
    }},
    "quick_wins": [
        {{
            "action": "string",
            "effort": "Low/Medium/High",
            "impact": "Low/Medium/High",
            "timeline": "string"
        }}
    ],
    "campaigns_to_scale": ["string"],
    "campaigns_to_pause": ["string"],
    "final_recommendation": "string"
}}

IMPORTANT: Output ONLY the JSON object. No markdown, no explanation, no code blocks. Just the raw JSON."""

    def _build_spam_prompt(self, campaigns_data: list[dict], templates_by_campaign: dict) -> str:
        """Build prompt for spam words analysis"""
        data_str = json.dumps(campaigns_data, indent=2, default=str)
        templates_str = json.dumps(templates_by_campaign, indent=2, default=str) if templates_by_campaign else "No templates available"
        
        return f"""Analyze these email campaigns for spam trigger words and deliverability issues. Respond ONLY with valid JSON.

CAMPAIGN DATA:
{data_str}

MESSAGE TEMPLATES (subjects and bodies to analyze):
{templates_str}

SPAM TRIGGER WORDS TO CHECK FOR (with better alternatives):
- Urgency: "Act now" → "When you have a moment", "Limited time" → "Currently available", "Urgent" → "Timely", "Immediately" → "At your earliest convenience"
- Money: "Free" → "Complimentary" or "At no cost", "Discount" → "Reduced rate", "Save" → "Keep more of your budget", "Cheap" → "Cost-effective"
- Promises: "Guarantee" → "We're confident that", "No risk" → "Low commitment", "100%" → "Fully", "Risk-free" → "You can always change your mind"
- Pressure: "Click here" → "Learn more at", "Sign up free" → "Get started", "Buy now" → "Explore options", "Order now" → "See how it works"
- Hype: "Amazing" → "Impressive", "Incredible" → "Notable", "Revolutionary" → "Innovative", "Breakthrough" → "Advancement"
- Sales-y: "Deal" → "Opportunity", "Offer" → "Option", "Promotion" → "Program", "Exclusive" → "Selected"
- ALL CAPS words → Use normal case
- Excessive punctuation (!!!, ???) → Use single punctuation

IMPORTANT: For every spam word you find, provide a CONCRETE replacement showing exactly how to rewrite it in context.

Respond with this exact JSON structure:
{{
    "overall_spam_risk": "Low/Medium/High",
    "deliverability_score": "X/10",
    "spam_words_found": [
        {{
            "campaign": "campaign name",
            "word_or_phrase": "the exact spam word/phrase found",
            "location": "subject/body/linkedin message",
            "risk_level": "Low/Medium/High",
            "why_its_risky": "brief explanation",
            "original_sentence": "The full sentence containing the spam word",
            "suggested_replacement": "The same sentence rewritten without the spam word"
        }}
    ],
    "subject_line_analysis": [
        {{
            "campaign": "campaign name",
            "original_subject": "the current subject line",
            "spam_score": "Low/Medium/High",
            "issues": ["issue 1", "issue 2"],
            "improved_subject": "complete rewritten subject line"
        }}
    ],
    "body_analysis": [
        {{
            "campaign": "campaign name",
            "spam_score": "Low/Medium/High",
            "issues_found": ["issue 1 with concrete example from the email", "issue 2"],
            "fix_examples": [
                {{
                    "original": "Original problematic sentence",
                    "fixed": "Rewritten sentence without spam triggers"
                }}
            ]
        }}
    ],
    "safe_patterns": ["patterns in your emails that are good for deliverability"],
    "top_recommendations": [
        {{
            "priority": 1,
            "issue": "description of the issue",
            "example_before": "Current problematic text",
            "example_after": "Suggested replacement text",
            "impact": "High/Medium/Low"
        }}
    ],
    "overall_summary": "string summarizing the spam analysis"
}}

IMPORTANT: Output ONLY the JSON object. No markdown, no explanation, no code blocks. Just the raw JSON."""

    def _build_ab_test_prompt(self, campaigns_data: list[dict], templates_by_campaign: dict) -> str:
        """Build prompt for A/B test suggestions with concrete examples"""
        data_str = json.dumps(campaigns_data, indent=2, default=str)
        templates_str = json.dumps(templates_by_campaign, indent=2, default=str) if templates_by_campaign else "No templates available"
        
        return f"""Generate A/B test suggestions for these campaigns. Respond ONLY with valid JSON.

{self._get_context_prompt()}

CAMPAIGN DATA:
{data_str}

MESSAGE TEMPLATES:
{templates_str}

CRITICAL - SPAM WORDS TO AVOID IN ALL GENERATED MESSAGES:
When writing test variants, NEVER use these spam trigger words:
- Urgency: "Act now", "Limited time", "Urgent", "Immediately", "Don't miss", "Hurry" 
  → Use instead: "When you have a moment", "Currently available", "Timely"
- Money: "Free", "Discount", "Save", "Cheap", "$$"
  → Use instead: "Complimentary", "At no cost", "Cost-effective"
- Promises: "Guarantee", "No risk", "100%", "Risk-free"
  → Use instead: "We're confident", "Low commitment"
- Pressure: "Click here", "Sign up free", "Buy now", "Order now"
  → Use instead: "Learn more", "Get started", "Explore"
- Hype: "Amazing", "Incredible", "Revolutionary", "Breakthrough"
  → Use instead: "Impressive", "Notable", "Innovative"
- Sales-y: "Deal", "Offer", "Promotion", "Exclusive"
  → Use instead: "Opportunity", "Option", "Program"
- NO ALL CAPS, NO excessive punctuation (!!!)

All messages you generate MUST be spam-free and professional.

Respond with this exact JSON structure:
{{
    "priority_test": {{
        "test_name": "string",
        "hypothesis": "string",
        "variant_a": {{
            "name": "Control",
            "full_message": "Complete spam-free message text for variant A",
            "channel": "LinkedIn or Email"
        }},
        "variant_b": {{
            "name": "Challenger", 
            "full_message": "Complete spam-free message text for variant B",
            "channel": "LinkedIn or Email"
        }},
        "what_changed": "string",
        "success_metric": "string",
        "sample_size": "string",
        "expected_lift": "string"
    }},
    "subject_line_tests": [
        {{
            "current_best": "string",
            "variant_a": "spam-free subject line option A",
            "variant_b": "spam-free subject line option B",
            "variant_c": "spam-free subject line option C",
            "rationale": "string"
        }}
    ],
    "testing_calendar": {{
        "week_1": "string",
        "week_2": "string",
        "week_3": "string",
        "week_4": "string"
    }}
}}

IMPORTANT: Output ONLY the JSON object. No markdown, no explanation, no code blocks. Just the raw JSON."""

    def _build_chat_prompt(self, question: str, campaigns_data: list[dict], templates_by_campaign: dict) -> str:
        """Build prompt for free-form chat"""
        data_str = json.dumps(campaigns_data, indent=2, default=str)
        templates_str = json.dumps(templates_by_campaign, indent=2, default=str)
        
        return f"""You are an expert growth marketing consultant. Answer the user's question about their campaigns.

{self._get_context_prompt()}

## CAMPAIGN PERFORMANCE DATA:
{data_str}

## MESSAGE TEMPLATES:
{templates_str}

## USER'S QUESTION:
{question}

## YOUR TASK:
Answer the question directly and specifically. Use data from the campaigns to support your answer.
Be helpful, specific, and actionable. If you're writing new copy, make it complete and ready to use.
Respond in English."""

    # Keep legacy methods for backward compatibility
    def analyze_campaigns(self, campaigns_data: list[dict], campaign_content: dict = None) -> dict:
        """Legacy method - redirects to analyze_copywriting"""
        templates = {}
        if campaign_content:
            for name, content in campaign_content.items():
                templates[name] = [content]
        return self.analyze_copywriting(campaigns_data, templates)
    
    def compare_campaigns(self, campaigns_data: list[dict], campaign_content: dict = None) -> dict:
        """Legacy method - now part of strategic recommendations"""
        templates = {}
        if campaign_content:
            for name, content in campaign_content.items():
                templates[name] = [content]
        return self.get_strategic_recommendations(campaigns_data, templates)
    
    def suggest_next_tests(self, campaigns_data: list[dict], campaign_content: dict = None) -> dict:
        """Legacy method - redirects to generate_ab_tests"""
        templates = {}
        if campaign_content:
            for name, content in campaign_content.items():
                templates[name] = [content]
        return self.generate_ab_tests(campaigns_data, templates)
    
    def generate_variants(self, winning_content: dict, num_variants: int = 3) -> dict:
        """Legacy method for generating variants"""
        prompt = f"""You are an expert B2B copywriter. Generate {num_variants} variants of this winning content.

IMPORTANT: Respond ENTIRELY in English.

## WINNING CONTENT:
{json.dumps(winning_content, indent=2, default=str)}

Generate complete message variants in JSON:

{{
    "subject_variants": [
        {{"subject": "New subject", "angle": "Different angle", "rationale": "Why"}}
    ],
    "email_body_variants": [
        {{"version": "A", "body": "Complete email", "main_change": "What changed"}}
    ],
    "linkedin_variants": [
        {{"version": "A", "message": "Complete message", "main_change": "What changed"}}
    ]
}}"""
        
        try:
            response = self.model.generate_content(prompt)
            return self._extract_json(response.text)
        except Exception as e:
            return {"error": str(e)}
    
    def _extract_json(self, text: str) -> dict:
        """Extract JSON from response text"""
        original_text = text  # Keep original for error reporting
        text = text.strip()
        
        # Remove markdown code blocks if present
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            if end > start:
                text = text[start:end]
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            if end > start:
                text = text[start:end]
        
        text = text.strip()
        
        # Try direct parsing
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Try to find JSON object in the text
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # Try to fix common issues
        try:
            # Remove trailing commas before } or ]
            fixed = re.sub(r',(\s*[}\]])', r'\1', text)
            return json.loads(fixed)
        except json.JSONDecodeError:
            pass
        
        return {
            "error": "Could not parse JSON response",
            "raw_response": original_text[:2000] if len(original_text) > 2000 else original_text
        }


class MockGeminiAnalyzer:
    """Mock analyzer for testing without API key"""
    
    def __init__(self, business_context: dict = None):
        self.business_context = business_context or {}
    
    def set_business_context(self, context: dict):
        self.business_context = context
    
    def analyze_copywriting(self, campaigns_data: list[dict], templates_by_campaign: dict) -> dict:
        return {
            "executive_summary": {
                "main_insight": "Messages with specific pain points get 3x more replies than generic intros",
                "biggest_opportunity": "LinkedIn connection messages are too long - shorter = better acceptance",
                "quick_win": "Add a specific number or stat in the first line of emails"
            },
            "hook_analysis": {
                "best_hooks": [
                    {
                        "hook": "Noticed {{companyName}} just raised Series A...",
                        "campaign": "Demo Campaign A",
                        "reply_rate": "18%",
                        "why_it_works": "Specific, timely, shows research"
                    }
                ],
                "worst_hooks": [
                    {
                        "hook": "Hi, I wanted to reach out...",
                        "campaign": "Demo Campaign C",
                        "reply_rate": "2%",
                        "why_it_fails": "Generic, no value proposition, sounds like spam"
                    }
                ],
                "hook_patterns": ["Specific company research", "Pain point in first line", "Numbers/stats"]
            },
            "message_improvements": [
                {
                    "original_message": "Hi {{firstName}}, I wanted to connect...",
                    "campaign": "Demo Campaign C",
                    "current_reply_rate": "2%",
                    "improved_version": "{{firstName}}, saw {{companyName}} is scaling the sales team. When manual processes break at 50+ reps, teams usually lose 10+ hours/week. Worth a quick chat?",
                    "changes_made": ["Added specific pain point", "Added social proof number", "Clear micro-CTA"],
                    "expected_improvement": "Should see 3-5x improvement based on pattern analysis"
                }
            ],
            "_note": "⚠️ Demo analysis. Connect Gemini API for real insights."
        }
    
    def get_strategic_recommendations(self, campaigns_data: list[dict], templates_by_campaign: dict) -> dict:
        return {
            "funnel_analysis": {
                "connection_to_reply": {
                    "current_rate": "12%",
                    "benchmark": "15-20% for B2B SaaS",
                    "gap_analysis": "Messages are too focused on product, not enough on prospect's pain",
                    "priority": "high"
                }
            },
            "channel_strategy": {
                "primary_channel": "LinkedIn",
                "reasoning": "Higher reply rates, decision makers more active",
                "channel_mix": "70% LinkedIn, 30% Email",
                "sequence_recommendation": "LinkedIn connection → DM → Email follow-up"
            },
            "quick_wins": [
                {
                    "action": "Shorten LinkedIn connection messages to <300 chars",
                    "effort": "Low",
                    "impact": "High",
                    "timeline": "This week"
                }
            ],
            "final_recommendation": "Focus on LinkedIn first. Your best campaign proves the channel works. Scale that approach to other audiences.",
            "_note": "⚠️ Demo recommendations."
        }
    
    def analyze_spam(self, campaigns_data: list[dict], templates_by_campaign: dict) -> dict:
        return {
            "overall_spam_risk": "Medium",
            "deliverability_score": "7/10",
            "spam_words_found": [
                {
                    "campaign": "Demo Campaign A",
                    "word_or_phrase": "Free",
                    "location": "subject",
                    "risk_level": "High",
                    "why_its_risky": "One of the most common spam triggers",
                    "suggested_alternative": "Complimentary or 'at no cost'"
                },
                {
                    "campaign": "Demo Campaign B",
                    "word_or_phrase": "Act now",
                    "location": "body",
                    "risk_level": "Medium",
                    "why_its_risky": "Creates artificial urgency",
                    "suggested_alternative": "When you have a moment"
                }
            ],
            "subject_line_analysis": [
                {
                    "campaign": "Demo Campaign A",
                    "subject": "Free guide for {{companyName}}",
                    "spam_score": "High",
                    "issues": ["Contains 'Free'", "Too promotional"],
                    "improved_subject": "Quick resource for {{companyName}}'s growth"
                }
            ],
            "body_analysis": [
                {
                    "campaign": "Demo Campaign A",
                    "spam_score": "Medium",
                    "issues_found": ["Contains urgency language", "Multiple CTAs"],
                    "recommendations": ["Remove 'Act now'", "Use single clear CTA"]
                }
            ],
            "safe_patterns": ["Personalization with {{firstName}}", "Short paragraphs", "Conversational tone"],
            "top_recommendations": [
                {
                    "priority": 1,
                    "issue": "Subject line contains 'Free'",
                    "fix": "Replace with 'Complimentary' or remove entirely",
                    "impact": "High"
                }
            ],
            "overall_summary": "Your emails have moderate spam risk. Main issues are urgency words and promotional language in subjects.",
            "_note": "⚠️ Demo spam analysis."
        }
    
    def generate_ab_tests(self, campaigns_data: list[dict], templates_by_campaign: dict) -> dict:
        return {
            "priority_test": {
                "test_name": "Pain Point Hook Test",
                "hypothesis": "Starting with a specific pain point will increase reply rate by 50%",
                "variant_a": {
                    "name": "Control",
                    "full_message": "Hi {{firstName}}, I noticed {{companyName}} is growing fast. I'd love to connect and share how we help similar companies with AI automation.",
                    "channel": "LinkedIn"
                },
                "variant_b": {
                    "name": "Pain Point Lead",
                    "full_message": "{{firstName}}, scaling teams usually means 10+ hours/week lost to manual processes. We built an AI agent that handles the busywork. Worth exploring?",
                    "channel": "LinkedIn"
                },
                "what_changed": "Opening with pain point vs. generic intro",
                "success_metric": "Reply rate",
                "sample_size": "100 leads per variant",
                "expected_lift": "40-60% improvement"
            },
            "subject_line_tests": [
                {
                    "current_best": "Quick question about {{companyName}}",
                    "variant_a": "{{firstName}}, 10 hours/week back?",
                    "variant_b": "AI agents for {{companyName}}",
                    "variant_c": "Your ops team + AI = ?",
                    "rationale": "Testing: number-based, direct product mention, curiosity gap"
                }
            ],
            "_note": "⚠️ Demo A/B tests."
        }
    
    def chat(self, question: str, campaigns_data: list[dict], templates_by_campaign: dict) -> str:
        return f"""Based on your campaigns, here's my analysis:

**Your question:** {question}

**Demo Response:** This is a demo response. Connect your Gemini API key to get real AI-powered answers about your campaigns.

Your current data shows promising results on LinkedIn with an average reply rate that could be improved by:
1. Shortening messages
2. Leading with pain points
3. Adding specific numbers/stats

Would you like me to rewrite any specific message for you?

⚠️ *This is demo mode. Real analysis requires a Gemini API key.*"""
    
    # Legacy methods
    def analyze_campaigns(self, campaigns_data: list[dict], campaign_content: dict = None) -> dict:
        return self.analyze_copywriting(campaigns_data, campaign_content or {})
    
    def compare_campaigns(self, campaigns_data: list[dict], campaign_content: dict = None) -> dict:
        return self.get_strategic_recommendations(campaigns_data, campaign_content or {})
    
    def suggest_next_tests(self, campaigns_data: list[dict], campaign_content: dict = None) -> dict:
        return self.generate_ab_tests(campaigns_data, campaign_content or {})
    
    def generate_variants(self, winning_content: dict, num_variants: int = 3) -> dict:
        return {
            "subject_variants": [
                {"subject": "{{firstName}}, quick question about {{companyName}}", "angle": "Double personalization"},
                {"subject": "10 hours/week back for {{companyName}}", "angle": "Specific benefit"},
            ],
            "_note": "⚠️ Demo variants"
        }