"""
Helper functions for the Streamlit app
"""
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict, Any
import json

def format_timestamp(timestamp: str) -> str:
    """
    Format ISO timestamp to readable format
    """
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return timestamp

def calculate_metrics(data: List[Dict]) -> Dict[str, Any]:
    """
    Calculate summary metrics from conversation data
    """
    if not data:
        return {}
    
    df = pd.DataFrame(data)
    
    metrics = {
        'total_count': len(df),
        'unique_customers': df['customer_id'].nunique() if 'customer_id' in df else 0,
        'avg_resolution_time': df['resolution_time'].mean() if 'resolution_time' in df else 0,
        'resolution_rate': (df['resolved'].sum() / len(df) * 100) if 'resolved' in df else 0
    }
    
    return metrics

def validate_json_structure(data: Dict) -> tuple[bool, List[str]]:
    """
    Validate the structure of ingestion JSON
    Returns: (is_valid, list_of_errors)
    """
    errors = []
    
    if 'conversations' not in data:
        errors.append("Missing 'conversations' key")
        return False, errors
    
    if not isinstance(data['conversations'], list):
        errors.append("'conversations' must be a list")
        return False, errors
    
    for i, conv in enumerate(data['conversations']):
        if 'conversation_id' not in conv:
            errors.append(f"Conversation {i}: missing 'conversation_id'")
        
        if 'customer_id' not in conv:
            errors.append(f"Conversation {i}: missing 'customer_id'")
        
        if 'messages' not in conv or not isinstance(conv.get('messages'), list):
            errors.append(f"Conversation {i}: missing or invalid 'messages'")
        
        for j, msg in enumerate(conv.get('messages', [])):
            if 'role' not in msg:
                errors.append(f"Conversation {i}, Message {j}: missing 'role'")
            
            if 'content' not in msg:
                errors.append(f"Conversation {i}, Message {j}: missing 'content'")
    
    return len(errors) == 0, errors

def generate_sample_data(num_conversations: int = 5) -> Dict:
    """
    Generate sample conversation data for testing
    """
    sample_data = {"conversations": []}
    
    issue_types = ["billing", "technical", "account", "feature", "support"]
    
    for i in range(num_conversations):
        conversation = {
            "conversation_id": f"sample_{i+1}",
            "customer_id": f"customer_{(i % 3) + 1:03d}",
            "timestamp": (datetime.now() - timedelta(days=i)).isoformat(),
            "messages": [
                {
                    "role": "customer",
                    "content": f"I'm having an issue with {issue_types[i % 5]}",
                    "timestamp": (datetime.now() - timedelta(days=i, hours=1)).isoformat()
                },
                {
                    "role": "agent",
                    "content": "I'd be happy to help you with that. Let me look into it.",
                    "timestamp": (datetime.now() - timedelta(days=i, minutes=55)).isoformat()
                },
                {
                    "role": "customer",
                    "content": "Thank you for your assistance.",
                    "timestamp": (datetime.now() - timedelta(days=i, minutes=30)).isoformat()
                },
                {
                    "role": "agent",
                    "content": "You're welcome! The issue has been resolved.",
                    "timestamp": (datetime.now() - timedelta(days=i, minutes=25)).isoformat()
                }
            ],
            "metadata": {
                "resolved": i % 3 != 0,
                "issue_type": issue_types[i % 5],
                "satisfaction_score": 3 + (i % 3),
                "escalated": i % 4 == 0
            }
        }
        sample_data["conversations"].append(conversation)
    
    return sample_data