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
    
    def get_campaigns(self, skip: int = 0, limit: int = 25) -> list[dict]:
        """
        Get all campaigns with their names and IDs
        
        Args:
            skip: Number of items to skip (for pagination)
            limit: Number of items to return (max 25)
        
        Returns:
            List of campaign dictionaries with id, name, status, etc.
        """
        endpoint = f"{self.base_url}/campaigns"
        params = {
            "apikey": self.api_key,
            "skip": skip,
            "limit": limit
        }
        
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        data = response.json()
        
        return data.get("campaigns", [])
    
    def get_all_campaigns(self) -> list[dict]:
        """
        Get all campaigns (handles pagination automatically)
        
        Returns:
            List of all campaign dictionaries
        """
        all_campaigns = []
        skip = 0
        limit = 25
        
        while True:
            campaigns = self.get_campaigns(skip=skip, limit=limit)
            if not campaigns:
                break
            all_campaigns.extend(campaigns)
            if len(campaigns) < limit:
                break
            skip += limit
        
        return all_campaigns

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
        # Get engagementStats from response
        engagement = stats.get("engagementStats", stats)
        
        # Get channel stats
        channel = engagement.get("channel", {})
        email_channel = channel.get("email", {})
        linkedin_channel = channel.get("linkedin", {})
        linkedin_message = linkedin_channel.get("message", {})
        linkedin_request = linkedin_channel.get("contactRequest", {})
        
        # Get relations stats (LinkedIn connections)
        relations = engagement.get("relations", {})
        
        # Get replies stats
        replies = engagement.get("replies", {})
        
        return CampaignStats(
            campaign_id=campaign_id,
            campaign_name=campaign_name,
            total_leads=engagement.get("audienceSize", 0),
            emails_sent=email_channel.get("sent", 0),
            emails_opened=email_channel.get("opened", 0),
            emails_clicked=email_channel.get("clicked", 0),
            emails_replied=email_channel.get("replied", 0),
            linkedin_sent=linkedin_request.get("sent", relations.get("requestSent", 0)),
            linkedin_accepted=relations.get("newRelations", 0) + relations.get("alreadyConnected", 0),
            linkedin_replied=replies.get("linkedinReplied", linkedin_message.get("replied", 0)),
            total_replies=replies.get("replied", engagement.get("replies", {}).get("replied", 0)),
            total_conversions=engagement.get("converted", 0)
        )


class LGMAPIError(Exception):
    """Custom exception for LGM API errors"""
    pass