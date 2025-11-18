"""
Generate large sample dataset for testing analytics
Creates 100 conversations with varied issues, agents, and customers
"""
import json
import random
from datetime import datetime, timedelta

# Issue types with descriptions
ISSUES = [
    ("password_reset", "Password reset not working", ["password", "reset", "login"]),
    ("payment_failed", "Payment failed but money deducted", ["payment", "billing", "charge"]),
    ("login_issue", "Cannot login to account", ["login", "access", "credentials"]),
    ("account_locked", "Account locked or suspended", ["locked", "suspended", "access"]),
    ("shipping_delay", "Order shipping delayed", ["shipping", "delivery", "tracking"]),
    ("refund_request", "Request refund for order", ["refund", "return", "money back"]),
    ("app_crash", "Mobile app crashing", ["crash", "freeze", "bug"]),
    ("email_not_received", "Confirmation email not received", ["email", "confirmation", "spam"]),
    ("subscription_cancel", "Cancel subscription", ["cancel", "subscription", "unsubscribe"]),
    ("product_defective", "Product arrived defective", ["defective", "broken", "damaged"]),
    ("slow_performance", "App running very slow", ["slow", "performance", "lag"]),
    ("data_sync_issue", "Data not syncing across devices", ["sync", "data", "devices"]),
    ("feature_request", "Request new feature", ["feature", "enhancement", "suggestion"]),
    ("billing_error", "Incorrect billing amount", ["billing", "charge", "incorrect"]),
    ("account_deletion", "Delete my account", ["delete", "remove", "gdpr"])
]

AGENTS = ["agent_alice", "agent_bob", "agent_charlie", "agent_diana", "agent_evan"]

# Customer message templates
CUSTOMER_MESSAGES = {
    "password_reset": [
        "I can't reset my password. The link doesn't work.",
        "Password reset email never arrived.",
        "Reset link says it's expired even though I just got it."
    ],
    "payment_failed": [
        "My payment failed but money was deducted!",
        "Card was charged but order shows as failed.",
        "Payment error but I see the charge on my bank statement."
    ],
    "login_issue": [
        "I can't login to my account.",
        "Getting 'invalid credentials' error when logging in.",
        "Login button doesn't work on mobile app."
    ],
    "account_locked": [
        "My account is locked and I can't access anything!",
        "Account suspended without any warning.",
        "Can't login - says account is locked."
    ],
    "shipping_delay": [
        "Where is my order? It's been 2 weeks!",
        "Tracking shows no movement for 5 days.",
        "Order was supposed to arrive yesterday."
    ]
}

AGENT_RESPONSES = [
    "I understand your concern. Let me help you with that.",
    "I apologize for the inconvenience. Let me check on this for you.",
    "I see the issue. Let me resolve this right away.",
    "Thank you for bringing this to our attention.",
    "I'm looking into this now. One moment please."
]

RESOLUTIONS = {
    "password_reset": "Sent new reset link",
    "payment_failed": "Refunded duplicate charge",
    "login_issue": "Reset credentials",
    "account_locked": "Unlocked account",
    "shipping_delay": "Expedited shipping",
    "refund_request": "Processed refund",
    "app_crash": "Suggested app update",
    "email_not_received": "Resent email",
    "subscription_cancel": "Cancelled subscription",
    "product_defective": "Replacement sent"
}

def generate_conversation(conv_id, customer_id, issue_type, issue_desc, tags, agent_id, base_date):
    """Generate a single conversation"""
    
    # Random time offset
    hours_ago = random.randint(0, 720)  # Up to 30 days ago
    created_at = base_date - timedelta(hours=hours_ago)
    
    # Resolution time: 5-60 minutes
    resolution_minutes = random.randint(5, 60)
    resolved_at = created_at + timedelta(minutes=resolution_minutes)
    
    # Get customer message
    if issue_type in CUSTOMER_MESSAGES:
        customer_msg = random.choice(CUSTOMER_MESSAGES[issue_type])
    else:
        customer_msg = f"I'm having an issue with {issue_desc.lower()}."
    
    # Build messages
    messages = [
        {
            "role": "customer",
            "content": customer_msg,
            "timestamp": created_at.isoformat() + "Z"
        },
        {
            "role": "agent",
            "content": random.choice(AGENT_RESPONSES),
            "timestamp": (created_at + timedelta(minutes=1)).isoformat() + "Z"
        },
        {
            "role": "customer",
            "content": "Please help me fix this quickly.",
            "timestamp": (created_at + timedelta(minutes=2)).isoformat() + "Z"
        },
        {
            "role": "agent",
            "content": f"I've {RESOLUTIONS.get(issue_type, 'resolved the issue')}. You should be all set now.",
            "timestamp": (created_at + timedelta(minutes=resolution_minutes-1)).isoformat() + "Z"
        },
        {
            "role": "customer",
            "content": random.choice(["Thank you!", "Thanks, that worked!", "Perfect, thanks!"]),
            "timestamp": resolved_at.isoformat() + "Z"
        }
    ]
    
    # Satisfaction score (weighted towards positive)
    satisfaction = random.choices([3, 4, 5], weights=[1, 3, 6])[0]
    
    return {
        "conversation_id": f"conv_{conv_id:03d}",
        "customer_id": customer_id,
        "agent_id": agent_id,
        "messages": messages,
        "metadata": {
            "issue_type": issue_type,
            "resolution": RESOLUTIONS.get(issue_type, "Issue resolved"),
            "satisfaction_score": satisfaction,
            "tags": tags
        },
        "created_at": created_at.isoformat() + "Z",
        "resolved_at": resolved_at.isoformat() + "Z"
    }

def generate_dataset(num_conversations=100):
    """Generate complete dataset"""
    
    conversations = []
    base_date = datetime.now()
    
    # Generate conversations
    for i in range(1, num_conversations + 1):
        # Pick random issue (weighted - some issues more common)
        issue_weights = [10, 8, 9, 7, 5, 6, 4, 5, 3, 4, 3, 3, 2, 4, 2]
        issue_type, issue_desc, tags = random.choices(ISSUES, weights=issue_weights)[0]
        
        # Pick random agent
        agent_id = random.choice(AGENTS)
        
        # Customer ID (some customers have multiple conversations)
        if random.random() < 0.3:  # 30% chance of repeat customer
            customer_id = f"customer_{random.randint(1, max(1, i-20)):03d}"
        else:
            customer_id = f"customer_{i:03d}"
        
        conv = generate_conversation(i, customer_id, issue_type, issue_desc, tags, agent_id, base_date)
        conversations.append(conv)
    
    return {
        "conversations": conversations,
        "batch_id": f"batch_large_sample_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    }

if __name__ == "__main__":
    print("🔄 Generating large sample dataset...")
    
    # Generate 100 conversations
    data = generate_dataset(100)
    
    # Save to file
    with open("large_sample_data.json", "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Generated {len(data['conversations'])} conversations")
    print(f"📁 Saved to: large_sample_data.json")
    print(f"📊 File size: {len(json.dumps(data)) / 1024:.1f} KB")
    
    # Statistics
    agents = {}
    issues = {}
    customers = set()
    
    for conv in data['conversations']:
        agents[conv['agent_id']] = agents.get(conv['agent_id'], 0) + 1
        issue_type = conv['metadata']['issue_type']
        issues[issue_type] = issues.get(issue_type, 0) + 1
        customers.add(conv['customer_id'])
    
    print(f"\n📈 Dataset Statistics:")
    print(f"  - Total conversations: {len(data['conversations'])}")
    print(f"  - Unique customers: {len(customers)}")
    print(f"  - Agents: {len(agents)}")
    for agent, count in sorted(agents.items()):
        print(f"    • {agent}: {count} chats")
    print(f"  - Issue types: {len(issues)}")
    for issue, count in sorted(issues.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"    • {issue}: {count} occurrences")
    
    print(f"\n🚀 Ready to ingest!")
    print(f"   Run: python ingest_sample_data.py")
    print(f"   (Update the script to use 'large_sample_data.json')")
