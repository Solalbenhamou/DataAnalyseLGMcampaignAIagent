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
        """Test if API connection is working using audiences endpoint"""
        try:
            self.get_audiences()
            return True
        except LGMAPIError:
            return False
    
    def get_members(self) -> list:
        """Get all team members"""
        return self._make_request("members")
    
    def get_audiences(self) -> list:
        """Get all audiences"""
        return self._make_request("audiences")
    
    def get_campaign_stats(self, campaign_id: str) -> dict:
        """Get statistics for a specific campaign"""
        return self._make_request(f"campaigns/{campaign_id}/stats")
    
    def get_campaigns_stats_by_ids(self, campaign_ids: list[str], campaign_names: dict = None) -> list[CampaignStats]:
        """
        Get statistics for multiple campaigns by their IDs
        
        Args:
            campaign_ids: List of campaign IDs
            campaign_names: Optional dict mapping campaign_id -> campaign_name
        """
        results = []
        campaign_names = campaign_names or {}
        
        for campaign_id in campaign_ids:
            campaign_name = campaign_names.get(campaign_id, f"Campaign {campaign_id[:8]}...")
            
            try:
                stats = self.get_campaign_stats(campaign_id)
                campaign_stats = self._parse_campaign_stats(campaign_id, campaign_name, stats)
                results.append(campaign_stats)
            except LGMAPIError as e:
                results.append(CampaignStats(
                    campaign_id=campaign_id,
                    campaign_name=f"{campaign_name} (erreur)"
                ))
        
        return results
    
    def _parse_campaign_stats(self, campaign_id: str, campaign_name: str, stats: dict) -> CampaignStats:
        """Parse raw API stats into CampaignStats object"""
        # LGM API response structure - adapt based on actual response
        email_stats = stats.get("email", stats.get("emails", {}))
        linkedin_stats = stats.get("linkedin", stats.get("linkedIn", {}))
        global_stats = stats.get("global", stats.get("summary", stats))
        
        def get_value(*keys, default=0):
            for key in keys:
                if key in stats:
                    return stats[key]
                if key in global_stats:
                    return global_stats[key]
                if key in email_stats:
                    return email_stats[key]
            return default
        
        return CampaignStats(
            campaign_id=campaign_id,
            campaign_name=campaign_name,
            total_leads=get_value("totalLeads", "leads", "leadsCount", "total_leads"),
            emails_sent=get_value("emailsSent", "sent", "emails_sent", "mailsSent"),
            emails_opened=get_value("emailsOpened", "opened", "emails_opened", "mailsOpened"),
            emails_clicked=get_value("emailsClicked", "clicked", "emails_clicked", "mailsClicked"),
            emails_replied=get_value("emailsReplied", "replied", "emails_replied", "mailsReplied"),
            linkedin_sent=get_value("linkedinSent", "invitesSent", "linkedin_sent", "connectionsSent"),
            linkedin_accepted=get_value("linkedinAccepted", "invitesAccepted", "linkedin_accepted", "connectionsAccepted"),
            linkedin_replied=get_value("linkedinReplied", "messagesReplied", "linkedin_replied"),
            total_replies=get_value("totalReplies", "replies", "total_replies", "replied"),
            total_conversions=get_value("conversions", "converted", "total_conversions", "deals")
        )


class LGMAPIError(Exception):
    """Custom exception for LGM API errors"""
    pass