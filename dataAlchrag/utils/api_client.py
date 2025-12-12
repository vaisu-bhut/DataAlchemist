"""
API Client utilities for the Customer Support RAG System
"""
import requests
from typing import Dict, List, Optional, Any
import json
from datetime import datetime

class APIClient:
    """
    Centralized API client for all endpoints
    """
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """
        Generic request handler with error handling
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "status_code": getattr(e.response, 'status_code', None)}
    
    # Analytics endpoints
    def get_summary(self) -> Dict:
        return self._make_request("GET", "/api/v1/analytics/summary")
    
    def get_agent_performance(self) -> Dict:
        return self._make_request("GET", "/api/v1/analytics/agents/performance")
    
    def get_customers(self) -> Dict:
        return self._make_request("GET", "/api/v1/analytics/customers")
    
    def get_customer_issues(self, customer_id: str) -> Dict:
        return self._make_request("GET", f"/api/v1/analytics/customers/{customer_id}/issues")
    
    def get_resolution_time(self) -> Dict:
        return self._make_request("GET", "/api/v1/analytics/resolution-time")
    
    def get_issue_distribution(self, limit: int = 10) -> Dict:
        return self._make_request("GET", f"/api/v1/analytics/issues/distribution?limit={limit}")
    
    def get_escalation_analytics(self) -> Dict:
        return self._make_request("GET", "/api/v1/analytics/escalation")
    
    # Chat endpoint
    def send_chat(self, query: str, customer_id: str, use_context: bool = True) -> Dict:
        payload = {
            "query": query,
            "customer_id": customer_id,
            "use_context": use_context
        }
        return self._make_request("POST", "/api/v1/chat", json=payload)
    
    # Ingestion endpoint (placeholder - add your actual endpoint)
    def ingest_conversations(self, conversations: List[Dict]) -> Dict:
        """
        Ingest conversations into the RAG system
        Note: Update this with your actual ingestion endpoint
        """
        payload = {"conversations": conversations}
        # Update with your actual ingestion endpoint
        return self._make_request("POST", "/api/v1/ingest", json=payload)