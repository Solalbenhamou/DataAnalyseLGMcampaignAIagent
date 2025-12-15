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
            "product": "AI Agent",
            "goal": "Connect with leads → Book meetings → Close deals",
            "target": "Decision makers (CEOs, CTOs, Founders)",
            "industry": "B2B SaaS"
        }
    
    def set_business_context(self, context: dict):
        """Update the business context"""
        self.business_context = context
    
    def _get_context_prompt(self) -> str:
        """Build the business context section for prompts"""
        return f"""## BUSINESS CONTEXT:
- Product/Service: {self.business_context.get('product', 'AI Agent')}
- Goal: {self.business_context.get('goal', 'Connect → Meeting → Close')}
- Target ICP: {self.business_context.get('target', 'Decision makers')}
- Industry: {self.business_context.get('industry', 'B2B SaaS')}
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
        templates_str = json.dumps(templates_by_campaign, indent=2, default=str)
        
        return f"""You are a world-class B2B copywriter and growth expert. Analyze the MESSAGE CONTENT of these outreach campaigns.

IMPORTANT: Respond ENTIRELY in English. Focus on ACTIONABLE copywriting insights, not just stats.

{self._get_context_prompt()}

## CAMPAIGN PERFORMANCE DATA:
{data_str}

## MESSAGE TEMPLATES (the actual copy used):
{templates_str}

## YOUR TASK:
Analyze the COPYWRITING - not the stats. I can see the stats myself. 
Tell me WHY certain messages work and others don't. Be specific and actionable.

Provide a JSON response:

{{
    "executive_summary": {{
        "main_insight": "The #1 copywriting insight from this data",
        "biggest_opportunity": "The biggest improvement opportunity",
        "quick_win": "One change that could improve results immediately"
    }},
    "hook_analysis": {{
        "best_hooks": [
            {{
                "hook": "The exact opening line that works",
                "campaign": "campaign name",
                "reply_rate": "X%",
                "why_it_works": "Psychological reason it works"
            }}
        ],
        "worst_hooks": [
            {{
                "hook": "Opening line that doesn't work",
                "campaign": "campaign name", 
                "reply_rate": "X%",
                "why_it_fails": "Why this doesn't resonate"
            }}
        ],
        "hook_patterns": ["Pattern 1 that correlates with high replies", "Pattern 2"]
    }},
    "cta_analysis": {{
        "best_ctas": ["CTA that gets replies"],
        "worst_ctas": ["CTA that doesn't work"],
        "recommendations": ["Specific CTA improvements"]
    }},
    "tone_and_style": {{
        "winning_tone": "Description of tone that works (casual, professional, etc.)",
        "optimal_length": "Short/Medium/Long with specific word count",
        "personalization_impact": "How personalization affects results"
    }},
    "channel_specific": {{
        "linkedin": {{
            "what_works": ["LinkedIn-specific insight"],
            "what_to_avoid": ["What doesn't work on LinkedIn"],
            "ideal_structure": "Recommended message structure"
        }},
        "email": {{
            "subject_line_insights": ["What makes subjects work"],
            "body_insights": ["What makes bodies work"],
            "ideal_structure": "Recommended email structure"
        }}
    }},
    "message_improvements": [
        {{
            "original_message": "Current message that underperforms",
            "campaign": "campaign name",
            "current_reply_rate": "X%",
            "improved_version": "Your rewritten version",
            "changes_made": ["Change 1", "Change 2"],
            "expected_improvement": "Why this should perform better"
        }}
    ]
}}

Be SPECIFIC. Quote actual messages. Give concrete examples. No generic advice."""

    def _build_strategic_prompt(self, campaigns_data: list[dict], templates_by_campaign: dict) -> str:
        """Build prompt for strategic recommendations"""
        data_str = json.dumps(campaigns_data, indent=2, default=str)
        templates_str = json.dumps(templates_by_campaign, indent=2, default=str)
        
        return f"""You are a strategic growth consultant. Based on these campaign results, provide strategic recommendations.

IMPORTANT: Respond ENTIRELY in English. Focus on STRATEGY, not tactics.

{self._get_context_prompt()}

## CAMPAIGN DATA:
{data_str}

## MESSAGE TEMPLATES:
{templates_str}

## YOUR TASK:
Provide strategic recommendations to optimize the funnel: Connect → Meeting → Close

Provide a JSON response:

{{
    "funnel_analysis": {{
        "connection_to_reply": {{
            "current_rate": "X%",
            "benchmark": "Industry benchmark",
            "gap_analysis": "Where we're losing people",
            "priority": "high/medium/low"
        }},
        "reply_to_meeting": {{
            "estimated_rate": "X%",
            "bottleneck": "What's preventing conversions",
            "recommendation": "How to improve"
        }}
    }},
    "channel_strategy": {{
        "primary_channel": "LinkedIn or Email",
        "reasoning": "Why this channel should be primary",
        "channel_mix": "Recommended % split",
        "sequence_recommendation": "LinkedIn first then Email, or vice versa"
    }},
    "audience_insights": {{
        "best_performing_segment": "Which audience/campaign type works best",
        "underperforming_segment": "Which to pause or fix",
        "expansion_opportunity": "New segments to test"
    }},
    "90_day_roadmap": {{
        "month_1": {{
            "focus": "Main focus area",
            "actions": ["Action 1", "Action 2", "Action 3"],
            "expected_outcome": "What success looks like"
        }},
        "month_2": {{
            "focus": "Main focus area",
            "actions": ["Action 1", "Action 2"],
            "expected_outcome": "What success looks like"
        }},
        "month_3": {{
            "focus": "Main focus area",
            "actions": ["Action 1", "Action 2"],
            "expected_outcome": "What success looks like"
        }}
    }},
    "quick_wins": [
        {{
            "action": "Specific action to take",
            "effort": "Low/Medium/High",
            "impact": "Low/Medium/High",
            "timeline": "This week / This month"
        }}
    ],
    "campaigns_to_scale": ["Campaign names to increase volume"],
    "campaigns_to_pause": ["Campaign names to stop or rework"],
    "final_recommendation": "Your #1 recommendation in 2-3 sentences"
}}

Be strategic. Think about the business goal: selling AI Agents to decision makers."""

    def _build_ab_test_prompt(self, campaigns_data: list[dict], templates_by_campaign: dict) -> str:
        """Build prompt for A/B test suggestions with concrete examples"""
        data_str = json.dumps(campaigns_data, indent=2, default=str)
        templates_str = json.dumps(templates_by_campaign, indent=2, default=str)
        
        return f"""You are an A/B testing expert and B2B copywriter. Generate CONCRETE test suggestions with actual message copy.

IMPORTANT: Respond ENTIRELY in English. Provide ACTUAL MESSAGES to test, not just ideas.

{self._get_context_prompt()}

## CURRENT CAMPAIGN DATA:
{data_str}

## CURRENT MESSAGES:
{templates_str}

## YOUR TASK:
Generate specific A/B tests with COMPLETE messages ready to use.
Don't just say "test personalization" - write the actual personalized message.

Provide a JSON response:

{{
    "priority_test": {{
        "test_name": "Name of the test",
        "hypothesis": "If we change X, then Y will improve because Z",
        "variant_a": {{
            "name": "Control",
            "full_message": "Complete message copy for variant A",
            "channel": "LinkedIn or Email"
        }},
        "variant_b": {{
            "name": "Challenger",
            "full_message": "Complete message copy for variant B",
            "channel": "LinkedIn or Email"
        }},
        "what_changed": "Specific element being tested",
        "success_metric": "Reply rate / Acceptance rate / Meeting booked",
        "sample_size": "X leads per variant",
        "expected_lift": "X% improvement expected"
    }},
    "subject_line_tests": [
        {{
            "current_best": "Current best performing subject",
            "variant_a": "New subject line option A",
            "variant_b": "New subject line option B", 
            "variant_c": "New subject line option C",
            "rationale": "Why these variants could outperform"
        }}
    ],
    "linkedin_message_tests": [
        {{
            "test_name": "What we're testing",
            "control": {{
                "message": "Current LinkedIn message",
                "reply_rate": "X%"
            }},
            "variant": {{
                "message": "New LinkedIn message to test",
                "change": "What's different"
            }}
        }}
    ],
    "email_body_tests": [
        {{
            "test_name": "What we're testing",
            "control": {{
                "body": "Current email body",
                "reply_rate": "X%"
            }},
            "variant": {{
                "body": "New email body to test",
                "change": "What's different"
            }}
        }}
    ],
    "sequence_tests": [
        {{
            "test_name": "Sequence structure test",
            "current_sequence": "Email → LinkedIn → Follow-up",
            "proposed_sequence": "LinkedIn → Email → Voice note",
            "rationale": "Why this sequence might work better"
        }}
    ],
    "testing_calendar": {{
        "week_1": "Test to run",
        "week_2": "Test to run",
        "week_3": "Test to run",
        "week_4": "Analyze and iterate"
    }}
}}

Write COMPLETE messages. Be specific. Use the same tone and personalization variables as the current messages."""

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
        text = text.strip()
        
        # Remove markdown code blocks if present
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        
        text = text.strip()
        
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON object in the text
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
            
            return {
                "error": "Could not parse JSON response",
                "raw_response": text
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