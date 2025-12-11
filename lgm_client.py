"""
LGM (La Growth Machine) API Client
Handles all interactions with the LGM API
"""

import requests
from typing import Optional
from dataclasses import dataclass


@dataclass
class CampaignStats:
    """Campaign statistics from LGM"""
    campaign_id: str
    campaign_name: str
    total_leads: int = 0
    emails_sent: int = 0
    emails_opened: int = 0
    emails_clicked: int = 0
    emails_replied: int = 0
    linkedin_sent: int = 0
    linkedin_accepted: int = 0
    linkedin_replied: int = 0
    total_replies: int = 0
    total_conversions: int = 0
    
    @property
    def open_rate(self) -> float:
        if self.emails_sent == 0:
            return 0.0
        return round((self.emails_opened / self.emails_sent) * 100, 2)
    
    @property
    def click_rate(self) -> float:
        if self.emails_sent == 0:
            return 0.0
        return round((self.emails_clicked / self.emails_sent) * 100, 2)
    
    @property
    def email_reply_rate(self) -> float:
        if self.emails_sent == 0:
            return 0.0
        return round((self.emails_replied / self.emails_sent) * 100, 2)
    
    @property
    def linkedin_acceptance_rate(self) -> float:
        if self.linkedin_sent == 0:
            return 0.0
        return round((self.linkedin_accepted / self.linkedin_sent) * 100, 2)
    
    @property
    def linkedin_reply_rate(self) -> float:
        if self.linkedin_sent == 0:
            return 0.0
        return round((self.linkedin_replied / self.linkedin_sent) * 100, 2)
    
    @property
    def overall_reply_rate(self) -> float:
        total_sent = self.emails_sent + self.linkedin_sent
        if total_sent == 0:
            return 0.0
        return round((self.total_replies / total_sent) * 100, 2)
    
    @property
    def conversion_rate(self) -> float:
        if self.total_leads == 0:
            return 0.0
        return round((self.total_conversions / self.total_leads) * 100, 2)


class LGMClient:
    """Client for La Growth Machine API"""
    
    BASE_URL = "https://apiv2.lagrowthmachine.com/flow"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def _make_request(self, endpoint: str, method: str = "GET", data: dict = None) -> dict:
        """Make authenticated request to LGM API"""
        url = f"{self.BASE_URL}/{endpoint}"
        params = {"apikey": self.api_key}
        
        try:
            if method == "GET":
                response = requests.get(url, params=params, timeout=30)
            elif method == "POST":
                response = requests.post(url, params=params, json=data, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise LGMAPIError(f"API request failed: {str(e)}")
    
    def test_connection(self) -> bool:
        """Test if API connection is working"""
        try:
            self.get_members()
            return True
        except LGMAPIError:
            return False
    
    def get_members(self) -> list:
        """Get all team members"""
        return self._make_request("members")
    
    def get_audiences(self) -> list:
        """Get all audiences"""
        return self._make_request("audiences")
    
    def get_campaigns(self) -> list:
        """Get all campaigns"""
        return self._make_request("campaigns")
    
    def get_campaign_stats(self, campaign_id: str) -> dict:
        """Get statistics for a specific campaign"""
        return self._make_request(f"campaigns/{campaign_id}/stats")
    
    def get_campaign_details(self, campaign_id: str) -> dict:
        """Get details for a specific campaign"""
        return self._make_request(f"campaigns/{campaign_id}")
    
    def get_all_campaigns_with_stats(self) -> list[CampaignStats]:
        """Get all campaigns with their statistics"""
        campaigns = self.get_campaigns()
        results = []
        
        for campaign in campaigns:
            campaign_id = campaign.get("id") or campaign.get("_id")
            campaign_name = campaign.get("name", "Unknown")
            
            try:
                stats = self.get_campaign_stats(campaign_id)
                campaign_stats = self._parse_campaign_stats(campaign_id, campaign_name, stats)
                results.append(campaign_stats)
            except LGMAPIError:
                # If stats fail, add campaign with zero stats
                results.append(CampaignStats(
                    campaign_id=campaign_id,
                    campaign_name=campaign_name
                ))
        
        return results
    
    def get_selected_campaigns_stats(self, campaign_ids: list[str]) -> list[CampaignStats]:
        """Get statistics for selected campaigns only"""
        campaigns = self.get_campaigns()
        campaign_map = {
            (c.get("id") or c.get("_id")): c.get("name", "Unknown") 
            for c in campaigns
        }
        
        results = []
        for campaign_id in campaign_ids:
            campaign_name = campaign_map.get(campaign_id, "Unknown")
            try:
                stats = self.get_campaign_stats(campaign_id)
                campaign_stats = self._parse_campaign_stats(campaign_id, campaign_name, stats)
                results.append(campaign_stats)
            except LGMAPIError:
                results.append(CampaignStats(
                    campaign_id=campaign_id,
                    campaign_name=campaign_name
                ))
        
        return results
    
    def _parse_campaign_stats(self, campaign_id: str, campaign_name: str, stats: dict) -> CampaignStats:
        """Parse raw API stats into CampaignStats object"""
        # LGM API returns nested stats - adapt based on actual response structure
        # This parsing may need adjustment based on actual API response
        
        email_stats = stats.get("email", {})
        linkedin_stats = stats.get("linkedin", {})
        global_stats = stats.get("global", stats)
        
        return CampaignStats(
            campaign_id=campaign_id,
            campaign_name=campaign_name,
            total_leads=global_stats.get("totalLeads", global_stats.get("leads", 0)),
            emails_sent=email_stats.get("sent", global_stats.get("emailsSent", 0)),
            emails_opened=email_stats.get("opened", global_stats.get("emailsOpened", 0)),
            emails_clicked=email_stats.get("clicked", global_stats.get("emailsClicked", 0)),
            emails_replied=email_stats.get("replied", global_stats.get("emailsReplied", 0)),
            linkedin_sent=linkedin_stats.get("sent", global_stats.get("linkedinSent", 0)),
            linkedin_accepted=linkedin_stats.get("accepted", global_stats.get("linkedinAccepted", 0)),
            linkedin_replied=linkedin_stats.get("replied", global_stats.get("linkedinReplied", 0)),
            total_replies=global_stats.get("totalReplies", global_stats.get("replied", 0)),
            total_conversions=global_stats.get("conversions", global_stats.get("converted", 0))
        )


class LGMAPIError(Exception):
    """Custom exception for LGM API errors"""
    pass
