"""
Gemini AI Analyzer
Analyzes campaign data and provides insights and recommendations
"""

import google.generativeai as genai
from typing import Optional
import json
import re


class GeminiAnalyzer:
    """AI-powered campaign analyzer using Google Gemini"""
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    def analyze_campaigns(self, campaigns_data: list[dict], campaign_content: dict = None) -> dict:
        """
        Analyze campaign performance and provide insights
        
        Args:
            campaigns_data: List of campaign stats dictionaries
            campaign_content: Optional dict mapping campaign names to their content (subject, body, etc.)
        
        Returns:
            Dictionary with analysis results
        """
        prompt = self._build_analysis_prompt(campaigns_data, campaign_content)
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_analysis_response(response.text)
        except Exception as e:
            return {
                "error": str(e),
                "raw_response": None
            }
    
    def compare_campaigns(self, campaigns_data: list[dict], campaign_content: dict = None) -> dict:
        """Compare multiple campaigns and identify winners"""
        prompt = self._build_comparison_prompt(campaigns_data, campaign_content)
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_comparison_response(response.text)
        except Exception as e:
            return {
                "error": str(e),
                "raw_response": None
            }
    
    def suggest_next_tests(self, campaigns_data: list[dict], campaign_content: dict = None) -> dict:
        """Suggest next A/B tests based on current results"""
        prompt = self._build_suggestions_prompt(campaigns_data, campaign_content)
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_suggestions_response(response.text)
        except Exception as e:
            return {
                "error": str(e),
                "raw_response": None
            }
    
    def generate_variants(self, winning_content: dict, num_variants: int = 3) -> dict:
        """Generate new content variants based on winning patterns"""
        prompt = self._build_variants_prompt(winning_content, num_variants)
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_variants_response(response.text)
        except Exception as e:
            return {
                "error": str(e),
                "raw_response": None
            }
    
    def _build_analysis_prompt(self, campaigns_data: list[dict], campaign_content: dict = None) -> str:
        """Build prompt for campaign analysis"""
        data_str = json.dumps(campaigns_data, indent=2, default=str)
        content_str = json.dumps(campaign_content, indent=2, default=str) if campaign_content else "Not provided"
        
        return f"""You are an expert in growth marketing and copywriting. Analyze the data from these outreach campaigns (email + LinkedIn).

IMPORTANT: Respond ENTIRELY in English. All text values must be in English.

## CAMPAIGN DATA:
{data_str}

## CAMPAIGN CONTENT (subjects, email body, LinkedIn messages):
{content_str}

## REQUESTED ANALYSIS:

Provide a structured JSON analysis with the following sections. ALL VALUES MUST BE IN ENGLISH:

{{
    "global_summary": {{
        "best_campaign": "campaign name",
        "worst_campaign": "campaign name",
        "general_trend": "short description IN ENGLISH"
    }},
    "open_rate_analysis": {{
        "average": "X%",
        "best_subject": "email subject",
        "winning_patterns": ["pattern 1 in English", "pattern 2 in English"],
        "losing_patterns": ["pattern 1 in English", "pattern 2 in English"]
    }},
    "reply_rate_analysis": {{
        "email_average": "X%",
        "linkedin_average": "X%",
        "success_factors": ["success factor in English", "factor 2"],
        "improvement_points": ["improvement point in English", "point 2"]
    }},
    "conversion_analysis": {{
        "average_rate": "X%",
        "top_conversion_campaign": "name",
        "hypotheses": ["hypothesis in English", "hypothesis 2"]
    }},
    "identified_patterns": {{
        "copywriting": ["pattern in English", "pattern 2"],
        "timing": ["observation in English"],
        "channel": ["email vs linkedin insight in English"]
    }},
    "global_score": {{
        "score": "X/10",
        "justification": "short explanation IN ENGLISH"
    }}
}}

Reply ONLY with the JSON, no text before or after. ALL TEXT VALUES MUST BE IN ENGLISH."""

    def _build_comparison_prompt(self, campaigns_data: list[dict], campaign_content: dict = None) -> str:
        """Build prompt for campaign comparison"""
        data_str = json.dumps(campaigns_data, indent=2, default=str)
        content_str = json.dumps(campaign_content, indent=2, default=str) if campaign_content else "Not provided"
        
        return f"""You are an expert in growth marketing. Compare these outreach campaigns and identify the winners.

IMPORTANT: Respond ENTIRELY in English. All text values must be in English.

## CAMPAIGN DATA:
{data_str}

## CAMPAIGN CONTENT:
{content_str}

## REQUESTED COMPARISON:

Provide a structured JSON comparison. ALL VALUES MUST BE IN ENGLISH:

{{
    "ranking": [
        {{
            "rank": 1,
            "campaign": "name",
            "global_score": "X/100",
            "strengths": ["strength 1 in English", "strength 2"],
            "weaknesses": ["weakness in English"]
        }}
    ],
    "best_email_subject": {{
        "subject": "the subject",
        "open_rate": "X%",
        "why_it_works": "explanation IN ENGLISH"
    }},
    "best_email_body": {{
        "campaign": "name",
        "reply_rate": "X%",
        "key_elements": ["element in English", "element 2"]
    }},
    "best_linkedin": {{
        "campaign": "name",
        "acceptance_rate": "X%",
        "reply_rate": "X%",
        "why_it_works": "explanation IN ENGLISH"
    }},
    "channel_comparison": {{
        "email_vs_linkedin": "which channel performs better and why IN ENGLISH",
        "recommendation": "recommendation IN ENGLISH"
    }},
    "conclusion": "summary in 2-3 sentences IN ENGLISH"
}}

Reply ONLY with the JSON. ALL TEXT VALUES MUST BE IN ENGLISH."""

    def _build_suggestions_prompt(self, campaigns_data: list[dict], campaign_content: dict = None) -> str:
        """Build prompt for A/B test suggestions"""
        data_str = json.dumps(campaigns_data, indent=2, default=str)
        content_str = json.dumps(campaign_content, indent=2, default=str) if campaign_content else "Not provided"
        
        return f"""You are an expert in growth marketing and A/B testing. Based on these campaign results, suggest the next tests to run.

IMPORTANT: Respond ENTIRELY in English. All text values must be in English.

## CURRENT DATA:
{data_str}

## CURRENT CONTENT:
{content_str}

## REQUESTED SUGGESTIONS:

Provide structured suggestions in JSON. ALL VALUES MUST BE IN ENGLISH:

{{
    "priority_tests": [
        {{
            "priority": 1,
            "test_type": "email subject / email body / linkedin message / sequence",
            "hypothesis": "what we want to test IN ENGLISH",
            "variant_A": "description or example IN ENGLISH",
            "variant_B": "description or example IN ENGLISH",
            "success_metric": "open rate / reply rate / etc",
            "recommended_sample_size": "X leads minimum",
            "potential_impact": "low / medium / high"
        }}
    ],
    "email_subject_tests": [
        {{
            "current_subject": "current best",
            "proposed_variants": ["variant 1 IN ENGLISH", "variant 2", "variant 3"],
            "rationale": "why these variants IN ENGLISH"
        }}
    ],
    "email_body_tests": [
        {{
            "element_to_test": "hook / CTA / length / personalization",
            "description": "what we change IN ENGLISH",
            "example": "concrete example IN ENGLISH"
        }}
    ],
    "linkedin_tests": [
        {{
            "element_to_test": "connection message / follow-up / voice note",
            "description": "what we change IN ENGLISH",
            "example": "concrete example IN ENGLISH"
        }}
    ],
    "testing_roadmap": {{
        "week_1": "test description IN ENGLISH",
        "week_2": "test description IN ENGLISH",
        "week_3": "test description IN ENGLISH",
        "week_4": "analysis and iteration IN ENGLISH"
    }},
    "strategic_advice": "general recommendation in 2-3 sentences IN ENGLISH"
}}

Reply ONLY with the JSON. ALL TEXT VALUES MUST BE IN ENGLISH."""

    def _build_variants_prompt(self, winning_content: dict, num_variants: int) -> str:
        """Build prompt for generating content variants"""
        content_str = json.dumps(winning_content, indent=2, default=str)
        
        return f"""You are an expert B2B copywriter. Generate {num_variants} variants of the following winning content, keeping the elements that work.

IMPORTANT: Respond ENTIRELY in English. All text values must be in English.

## WINNING CONTENT:
{content_str}

## REQUESTED VARIANTS:

Generate variants in JSON. ALL VALUES MUST BE IN ENGLISH:

{{
    "winning_content_analysis": {{
        "key_elements": ["key element IN ENGLISH", "element 2"],
        "tone": "tone description IN ENGLISH",
        "structure": "structure description IN ENGLISH",
        "effective_hooks": ["effective hook IN ENGLISH", "hook 2"]
    }},
    "subject_variants": [
        {{
            "subject": "new subject IN ENGLISH",
            "angle": "different angle IN ENGLISH",
            "rationale": "justification IN ENGLISH"
        }}
    ],
    "email_body_variants": [
        {{
            "version": "Version A",
            "body": "complete email body IN ENGLISH",
            "main_change": "what changes vs original IN ENGLISH"
        }}
    ],
    "linkedin_variants": [
        {{
            "version": "Version A",
            "message": "complete message IN ENGLISH",
            "main_change": "what changes IN ENGLISH"
        }}
    ],
    "test_recommendation": "which variant to test first and why IN ENGLISH"
}}

Reply ONLY with the JSON. ALL TEXT VALUES MUST BE IN ENGLISH."""

    def _parse_analysis_response(self, response_text: str) -> dict:
        """Parse the analysis response from Gemini"""
        return self._extract_json(response_text)
    
    def _parse_comparison_response(self, response_text: str) -> dict:
        """Parse the comparison response from Gemini"""
        return self._extract_json(response_text)
    
    def _parse_suggestions_response(self, response_text: str) -> dict:
        """Parse the suggestions response from Gemini"""
        return self._extract_json(response_text)
    
    def _parse_variants_response(self, response_text: str) -> dict:
        """Parse the variants response from Gemini"""
        return self._extract_json(response_text)
    
    def _extract_json(self, text: str) -> dict:
        """Extract JSON from response text"""
        # Try to find JSON in the response
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
    
    def analyze_campaigns(self, campaigns_data: list[dict], campaign_content: dict = None) -> dict:
        return {
            "global_summary": {
                "best_campaign": "Demo Campaign A",
                "worst_campaign": "Demo Campaign C",
                "general_trend": "Campaigns with personalization perform better"
            },
            "open_rate_analysis": {
                "average": "45%",
                "best_subject": "{{firstName}} - Quick question",
                "winning_patterns": ["First name personalization", "Curiosity", "Short (<50 chars)"],
                "losing_patterns": ["Too promotional", "Excessive caps"]
            },
            "reply_rate_analysis": {
                "email_average": "8%",
                "linkedin_average": "12%",
                "success_factors": ["Open question", "Immediate value", "Social proof"],
                "improvement_points": ["Clearer CTA", "Reduce length"]
            },
            "identified_patterns": {
                "copywriting": ["Precise numbers increase credibility", "Questions engage more"],
                "timing": ["Tuesday-Thursday perform better"],
                "channel": ["LinkedIn > Email for C-level decision makers"]
            },
            "global_score": {
                "score": "7/10",
                "justification": "Good foundation but optimization possible on follow-ups"
            },
            "_note": "⚠️ This is a demo analysis. Connect your Gemini API key for real analysis."
        }
    
    def compare_campaigns(self, campaigns_data: list[dict], campaign_content: dict = None) -> dict:
        return {
            "ranking": [
                {"rank": 1, "campaign": "Demo A", "global_score": "85/100", "strengths": ["Good open rate", "Clear CTA"]},
                {"rank": 2, "campaign": "Demo B", "global_score": "72/100", "strengths": ["Personalization"]},
            ],
            "conclusion": "Campaign A outperforms thanks to its catchy subject line.",
            "_note": "⚠️ Demo analysis"
        }
    
    def suggest_next_tests(self, campaigns_data: list[dict], campaign_content: dict = None) -> dict:
        return {
            "priority_tests": [
                {
                    "priority": 1,
                    "test_type": "email subject",
                    "hypothesis": "A subject with precise number increases open rate",
                    "variant_A": "Current subject",
                    "variant_B": "{{firstName}}, 3 min to double your replies",
                    "potential_impact": "high"
                }
            ],
            "strategic_advice": "Focus on open rate first before optimizing the body.",
            "_note": "⚠️ Demo suggestions"
        }
    
    def generate_variants(self, winning_content: dict, num_variants: int = 3) -> dict:
        return {
            "subject_variants": [
                {"subject": "{{firstName}}, quick question about {{companyName}}", "angle": "Double personalization"},
                {"subject": "2 min - idea for {{companyName}}", "angle": "Short time + value"},
            ],
            "_note": "⚠️ Demo variants"
        }