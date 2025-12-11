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
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
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
        content_str = json.dumps(campaign_content, indent=2, default=str) if campaign_content else "Non fourni"
        
        return f"""Tu es un expert en growth marketing et copywriting. Analyse les données de ces campagnes d'outreach (email + LinkedIn).

## DONNÉES DES CAMPAGNES:
{data_str}

## CONTENU DES CAMPAGNES (sujets, corps de mail, messages LinkedIn):
{content_str}

## ANALYSE DEMANDÉE:

Fournis une analyse structurée en JSON avec les sections suivantes:

{{
    "resume_global": {{
        "meilleure_campagne": "nom de la campagne",
        "pire_campagne": "nom de la campagne",
        "tendance_generale": "description courte"
    }},
    "analyse_open_rate": {{
        "moyenne": "X%",
        "meilleur_sujet": "sujet email",
        "patterns_gagnants": ["pattern 1", "pattern 2"],
        "patterns_perdants": ["pattern 1", "pattern 2"]
    }},
    "analyse_reply_rate": {{
        "moyenne_email": "X%",
        "moyenne_linkedin": "X%",
        "facteurs_succes": ["facteur 1", "facteur 2"],
        "points_amelioration": ["point 1", "point 2"]
    }},
    "analyse_conversion": {{
        "taux_moyen": "X%",
        "campagne_top_conversion": "nom",
        "hypotheses": ["hypothèse 1", "hypothèse 2"]
    }},
    "patterns_identifies": {{
        "copywriting": ["pattern 1", "pattern 2"],
        "timing": ["observation 1"],
        "canal": ["email vs linkedin insights"]
    }},
    "score_global": {{
        "note": "X/10",
        "justification": "explication courte"
    }}
}}

Réponds UNIQUEMENT avec le JSON, sans texte avant ou après."""

    def _build_comparison_prompt(self, campaigns_data: list[dict], campaign_content: dict = None) -> str:
        """Build prompt for campaign comparison"""
        data_str = json.dumps(campaigns_data, indent=2, default=str)
        content_str = json.dumps(campaign_content, indent=2, default=str) if campaign_content else "Non fourni"
        
        return f"""Tu es un expert en growth marketing. Compare ces campagnes d'outreach et identifie les gagnants.

## DONNÉES DES CAMPAGNES:
{data_str}

## CONTENU DES CAMPAGNES:
{content_str}

## COMPARAISON DEMANDÉE:

Fournis une comparaison structurée en JSON:

{{
    "classement": [
        {{
            "rang": 1,
            "campagne": "nom",
            "score_global": "X/100",
            "forces": ["force 1", "force 2"],
            "faiblesses": ["faiblesse 1"]
        }}
    ],
    "meilleur_sujet_email": {{
        "sujet": "le sujet",
        "open_rate": "X%",
        "pourquoi_ca_marche": "explication"
    }},
    "meilleur_corps_email": {{
        "campagne": "nom",
        "reply_rate": "X%",
        "elements_cles": ["élément 1", "élément 2"]
    }},
    "meilleur_linkedin": {{
        "campagne": "nom",
        "acceptance_rate": "X%",
        "reply_rate": "X%",
        "pourquoi_ca_marche": "explication"
    }},
    "comparaison_canal": {{
        "email_vs_linkedin": "quel canal performe mieux et pourquoi",
        "recommandation": "recommandation sur le mix canal"
    }},
    "conclusion": "synthèse en 2-3 phrases"
}}

Réponds UNIQUEMENT avec le JSON."""

    def _build_suggestions_prompt(self, campaigns_data: list[dict], campaign_content: dict = None) -> str:
        """Build prompt for A/B test suggestions"""
        data_str = json.dumps(campaigns_data, indent=2, default=str)
        content_str = json.dumps(campaign_content, indent=2, default=str) if campaign_content else "Non fourni"
        
        return f"""Tu es un expert en growth marketing et A/B testing. Basé sur ces résultats de campagnes, suggère les prochains tests à lancer.

## DONNÉES ACTUELLES:
{data_str}

## CONTENU ACTUEL:
{content_str}

## SUGGESTIONS DEMANDÉES:

Fournis des suggestions structurées en JSON:

{{
    "priorite_tests": [
        {{
            "priorite": 1,
            "type_test": "sujet email / corps email / message linkedin / séquence",
            "hypothese": "ce qu'on veut tester",
            "variante_A": "description ou exemple",
            "variante_B": "description ou exemple",
            "metrique_succes": "open rate / reply rate / etc",
            "taille_echantillon_recommandee": "X leads minimum",
            "impact_potentiel": "faible / moyen / élevé"
        }}
    ],
    "tests_sujet_email": [
        {{
            "sujet_actuel": "le meilleur actuel",
            "variantes_proposees": ["variante 1", "variante 2", "variante 3"],
            "logique": "pourquoi ces variantes"
        }}
    ],
    "tests_corps_email": [
        {{
            "element_a_tester": "hook / CTA / longueur / personnalisation",
            "description": "ce qu'on change",
            "exemple": "exemple concret"
        }}
    ],
    "tests_linkedin": [
        {{
            "element_a_tester": "message connexion / follow-up / voice note",
            "description": "ce qu'on change",
            "exemple": "exemple concret"
        }}
    ],
    "roadmap_testing": {{
        "semaine_1": "description du test",
        "semaine_2": "description du test",
        "semaine_3": "description du test",
        "semaine_4": "analyse et itération"
    }},
    "conseil_strategique": "recommandation générale en 2-3 phrases"
}}

Réponds UNIQUEMENT avec le JSON."""

    def _build_variants_prompt(self, winning_content: dict, num_variants: int) -> str:
        """Build prompt for generating content variants"""
        content_str = json.dumps(winning_content, indent=2, default=str)
        
        return f"""Tu es un expert copywriter B2B. Génère {num_variants} variantes du contenu gagnant suivant, en conservant les éléments qui fonctionnent.

## CONTENU GAGNANT:
{content_str}

## VARIANTES DEMANDÉES:

Génère des variantes en JSON:

{{
    "analyse_contenu_gagnant": {{
        "elements_cles": ["élément 1", "élément 2"],
        "ton": "description du ton",
        "structure": "description de la structure",
        "hooks_efficaces": ["hook 1", "hook 2"]
    }},
    "variantes_sujet": [
        {{
            "sujet": "nouveau sujet",
            "angle": "quel angle différent",
            "pourquoi": "justification"
        }}
    ],
    "variantes_corps_email": [
        {{
            "version": "Version A",
            "corps": "le corps complet de l'email",
            "modification_principale": "ce qui change vs l'original"
        }}
    ],
    "variantes_linkedin": [
        {{
            "version": "Version A",
            "message": "le message complet",
            "modification_principale": "ce qui change"
        }}
    ],
    "recommandation_test": "quelle variante tester en premier et pourquoi"
}}

Réponds UNIQUEMENT avec le JSON."""

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
                "tendance_generale": "Les campagnes avec personnalisation performent mieux"
            },
            "analyse_open_rate": {
                "moyenne": "45%",
                "meilleur_sujet": "{{firstName}} - Question rapide",
                "patterns_gagnants": ["Personnalisation prénom", "Curiosité", "Court (<50 chars)"],
                "patterns_perdants": ["Trop promotionnel", "Majuscules excessives"]
            },
            "analyse_reply_rate": {
                "moyenne_email": "8%",
                "moyenne_linkedin": "12%",
                "facteurs_succes": ["Question ouverte", "Valeur immédiate", "Social proof"],
                "points_amelioration": ["CTA plus clair", "Réduire longueur"]
            },
            "patterns_identifies": {
                "copywriting": ["Les chiffres précis augmentent la crédibilité", "Les questions engagent plus"],
                "timing": ["Mardi-Jeudi performent mieux"],
                "canal": ["LinkedIn > Email pour les décideurs C-level"]
            },
            "score_global": {
                "note": "7/10",
                "justification": "Bonnes bases mais optimisation possible sur les follow-ups"
            },
            "_note": "⚠️ Ceci est une analyse de démonstration. Connectez votre clé API Gemini pour une vraie analyse."
        }
    
    def compare_campaigns(self, campaigns_data: list[dict], campaign_content: dict = None) -> dict:
        return {
            "classement": [
                {"rang": 1, "campagne": "Demo A", "score_global": "85/100", "forces": ["Bon open rate", "CTA clair"]},
                {"rang": 2, "campagne": "Demo B", "score_global": "72/100", "forces": ["Personnalisation"]},
            ],
            "conclusion": "La campagne A surperforme grâce à son sujet accrocheur.",
            "_note": "⚠️ Analyse de démonstration"
        }
    
    def suggest_next_tests(self, campaigns_data: list[dict], campaign_content: dict = None) -> dict:
        return {
            "priorite_tests": [
                {
                    "priorite": 1,
                    "type_test": "sujet email",
                    "hypothese": "Un sujet avec chiffre précis augmente l'open rate",
                    "variante_A": "Sujet actuel",
                    "variante_B": "{{firstName}}, 3 min pour doubler vos réponses",
                    "impact_potentiel": "élevé"
                }
            ],
            "conseil_strategique": "Concentrez-vous d'abord sur l'open rate avant d'optimiser le corps.",
            "_note": "⚠️ Suggestions de démonstration"
        }
    
    def generate_variants(self, winning_content: dict, num_variants: int = 3) -> dict:
        return {
            "variantes_sujet": [
                {"sujet": "{{firstName}}, question rapide sur {{companyName}}", "angle": "Personnalisation double"},
                {"sujet": "2 min - idée pour {{companyName}}", "angle": "Temps court + valeur"},
            ],
            "_note": "⚠️ Variantes de démonstration"
        }
