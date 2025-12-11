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

## CAMPAIGN DATA:
{data_str}

## CAMPAIGN CONTENT (subjects, email body, LinkedIn messages):
{content_str}

## REQUESTED ANALYSIS:

Provide a structured JSON analysis with the following sections:

{{
    "resume_global": {{
        "meilleure_campagne": "campaign name",
        "pire_campagne": "campaign name",
        "tendance_generale": "short description"
    }},
    "analyse_open_rate": {{
        "moyenne": "X%",
        "meilleur_sujet": "email subject",
        "patterns_gagnants": ["pattern 1", "pattern 2"],
        "patterns_perdants": ["pattern 1", "pattern 2"]
    }},
    "analyse_reply_rate": {{
        "moyenne_email": "X%",
        "moyenne_linkedin": "X%",
        "facteurs_succes": ["factor 1", "factor 2"],
        "points_amelioration": ["point 1", "point 2"]
    }},
    "analyse_conversion": {{
        "taux_moyen": "X%",
        "campagne_top_conversion": "name",
        "hypotheses": ["hypothesis 1", "hypothesis 2"]
    }},
    "patterns_identifies": {{
        "copywriting": ["pattern 1", "pattern 2"],
        "timing": ["observation 1"],
        "canal": ["email vs linkedin insights"]
    }},
    "score_global": {{
        "note": "X/10",
        "justification": "short explanation"
    }}
}}

Reply ONLY with the JSON, no text before or after."""

    def _build_comparison_prompt(self, campaigns_data: list[dict], campaign_content: dict = None) -> str:
        """Build prompt for campaign comparison"""
        data_str = json.dumps(campaigns_data, indent=2, default=str)
        content_str = json.dumps(campaign_content, indent=2, default=str) if campaign_content else "Not provided"
        
        return f"""You are an expert in growth marketing. Compare these outreach campaigns and identify the winners.

## CAMPAIGN DATA:
{data_str}

## CAMPAIGN CONTENT:
{content_str}

## REQUESTED COMPARISON:

Provide a structured JSON comparison:

{{
    "classement": [
        {{
            "rang": 1,
            "campagne": "name",
            "score_global": "X/100",
            "forces": ["strength 1", "strength 2"],
            "faiblesses": ["weakness 1"]
        }}
    ],
    "meilleur_sujet_email": {{
        "sujet": "the subject",
        "open_rate": "X%",
        "pourquoi_ca_marche": "explanation"
    }},
    "meilleur_corps_email": {{
        "campagne": "name",
        "reply_rate": "X%",
        "elements_cles": ["element 1", "element 2"]
    }},
    "meilleur_linkedin": {{
        "campagne": "name",
        "acceptance_rate": "X%",
        "reply_rate": "X%",
        "pourquoi_ca_marche": "explanation"
    }},
    "comparaison_canal": {{
        "email_vs_linkedin": "which channel performs better and why",
        "recommandation": "recommendation on channel mix"
    }},
    "conclusion": "summary in 2-3 sentences"
}}

Reply ONLY with the JSON."""

    def _build_suggestions_prompt(self, campaigns_data: list[dict], campaign_content: dict = None) -> str:
        """Build prompt for A/B test suggestions"""
        data_str = json.dumps(campaigns_data, indent=2, default=str)
        content_str = json.dumps(campaign_content, indent=2, default=str) if campaign_content else "Not provided"
        
        return f"""You are an expert in growth marketing and A/B testing. Based on these campaign results, suggest the next tests to run.

## CURRENT DATA:
{data_str}

## CURRENT CONTENT:
{content_str}

## REQUESTED SUGGESTIONS:

Provide structured suggestions in JSON:

{{
    "priorite_tests": [
        {{
            "priorite": 1,
            "type_test": "email subject / email body / linkedin message / sequence",
            "hypothese": "what we want to test",
            "variante_A": "description or example",
            "variante_B": "description or example",
            "metrique_succes": "open rate / reply rate / etc",
            "taille_echantillon_recommandee": "X leads minimum",
            "impact_potentiel": "low / medium / high"
        }}
    ],
    "tests_sujet_email": [
        {{
            "sujet_actuel": "current best",
            "variantes_proposees": ["variant 1", "variant 2", "variant 3"],
            "logique": "why these variants"
        }}
    ],
    "tests_corps_email": [
        {{
            "element_a_tester": "hook / CTA / length / personalization",
            "description": "what we change",
            "exemple": "concrete example"
        }}
    ],
    "tests_linkedin": [
        {{
            "element_a_tester": "connection message / follow-up / voice note",
            "description": "what we change",
            "exemple": "concrete example"
        }}
    ],
    "roadmap_testing": {{
        "semaine_1": "test description",
        "semaine_2": "test description",
        "semaine_3": "test description",
        "semaine_4": "analysis and iteration"
    }},
    "conseil_strategique": "general recommendation in 2-3 sentences"
}}

Reply ONLY with the JSON."""

    def _build_variants_prompt(self, winning_content: dict, num_variants: int) -> str:
        """Build prompt for generating content variants"""
        content_str = json.dumps(winning_content, indent=2, default=str)
        
        return f"""You are an expert B2B copywriter. Generate {num_variants} variants of the following winning content, keeping the elements that work.

## WINNING CONTENT:
{content_str}

## REQUESTED VARIANTS:

Generate variants in JSON:

{{
    "analyse_contenu_gagnant": {{
        "elements_cles": ["element 1", "element 2"],
        "ton": "tone description",
        "structure": "structure description",
        "hooks_efficaces": ["hook 1", "hook 2"]
    }},
    "variantes_sujet": [
        {{
            "sujet": "new subject",
            "angle": "different angle",
            "pourquoi": "justification"
        }}
    ],
    "variantes_corps_email": [
        {{
            "version": "Version A",
            "corps": "complete email body",
            "modification_principale": "what changes vs original"
        }}
    ],
    "variantes_linkedin": [
        {{
            "version": "Version A",
            "message": "complete message",
            "modification_principale": "what changes"
        }}
    ],
    "recommandation_test": "which variant to test first and why"
}}

Reply ONLY with the JSON."""

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
            "resume_global": {
                "meilleure_campagne": "Demo Campaign A",
                "pire_campagne": "Demo Campaign C",
                "tendance_generale": "Campaigns with personalization perform better"
            },
            "analyse_open_rate": {
                "moyenne": "45%",
                "meilleur_sujet": "{{firstName}} - Quick question",
                "patterns_gagnants": ["First name personalization", "Curiosity", "Short (<50 chars)"],
                "patterns_perdants": ["Too promotional", "Excessive caps"]
            },
            "analyse_reply_rate": {
                "moyenne_email": "8%",
                "moyenne_linkedin": "12%",
                "facteurs_succes": ["Open question", "Immediate value", "Social proof"],
                "points_amelioration": ["Clearer CTA", "Reduce length"]
            },
            "patterns_identifies": {
                "copywriting": ["Precise numbers increase credibility", "Questions engage more"],
                "timing": ["Tuesday-Thursday perform better"],
                "canal": ["LinkedIn > Email for C-level decision makers"]
            },
            "score_global": {
                "note": "7/10",
                "justification": "Good foundation but optimization possible on follow-ups"
            },
            "_note": "⚠️ This is a demo analysis. Connect your Gemini API key for real analysis."
        }
    
    def compare_campaigns(self, campaigns_data: list[dict], campaign_content: dict = None) -> dict:
        return {
            "classement": [
                {"rang": 1, "campagne": "Demo A", "score_global": "85/100", "forces": ["Good open rate", "Clear CTA"]},
                {"rang": 2, "campagne": "Demo B", "score_global": "72/100", "forces": ["Personalization"]},
            ],
            "conclusion": "Campaign A outperforms thanks to its catchy subject line.",
            "_note": "⚠️ Demo analysis"
        }
    
    def suggest_next_tests(self, campaigns_data: list[dict], campaign_content: dict = None) -> dict:
        return {
            "priorite_tests": [
                {
                    "priorite": 1,
                    "type_test": "email subject",
                    "hypothese": "A subject with precise number increases open rate",
                    "variante_A": "Current subject",
                    "variante_B": "{{firstName}}, 3 min to double your replies",
                    "impact_potentiel": "high"
                }
            ],
            "conseil_strategique": "Focus on open rate first before optimizing the body.",
            "_note": "⚠️ Demo suggestions"
        }
    
    def generate_variants(self, winning_content: dict, num_variants: int = 3) -> dict:
        return {
            "variantes_sujet": [
                {"sujet": "{{firstName}}, quick question about {{companyName}}", "angle": "Double personalization"},
                {"sujet": "2 min - idea for {{companyName}}", "angle": "Short time + value"},
            ],
            "_note": "⚠️ Demo variants"
        }