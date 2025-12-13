import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Data Ingestion", page_icon="📤", layout="wide")

st.title("📤 Data Ingestion Portal")

# API Base URL from session state
api_base = st.session_state.get('api_base_url', 'https://agentic-system-512754882743.us-east1.run.app')

st.header("📁 Upload Chat Logs")

st.info("""
**Supported Format**: JSON

**Expected Structure**:
```json
{
    "conversations": [
        {
            "conversation_id": "unique_id",
            "customer_id": "customer_xxx",
            "timestamp": "2024-01-01T10:00:00Z",
            "messages": [
                {
                    "role": "customer",
                    "content": "message text",
                    "timestamp": "2024-01-01T10:00:00Z"
                },
                {
                    "role": "agent",
                    "content": "response text",
                    "timestamp": "2024-01-01T10:01:00Z"
                }
            ],
            "metadata": {
                "resolved": true,
                "issue_type": "billing",
                "satisfaction_score": 4
            }
        }
    ]
}
```
""")

uploaded_file = st.file_uploader("Choose a JSON file", type=['json'])

if uploaded_file is not None:
    # Display file details
    file_details = {
        "Filename": uploaded_file.name,
        "FileType": uploaded_file.type,
        "FileSize": f"{uploaded_file.size / 1024:.2f} KB"
    }
    st.write("**File Details:**")
    st.json(file_details)
    
    # Parse and preview
    try:
        content = json.load(uploaded_file)
        
        st.subheader("Preview")
        
        # Show statistics
        if 'conversations' in content:
            num_conversations = len(content['conversations'])
            st.success(f"Found {num_conversations} conversations")
            
            # Preview first conversation
            if num_conversations > 0:
                with st.expander("Preview First Conversation"):
                    st.json(content['conversations'][0])
            
            # Validation options
            col1, col2 = st.columns(2)
            with col1:
                validate_pii = st.checkbox("Auto-redact PII", value=True)
            with col2:
                validate_structure = st.checkbox("Validate structure", value=True)
            
            # Upload button
            if st.button("🚀 Upload to System", type="primary"):
                with st.spinner("Processing and ingesting data..."):
                    # Placeholder for actual ingestion API call
                    # You'll need to add your ingestion API endpoint here
                    st.info("Note: Add your ingestion API endpoint in the code")
                    
                    # Simulated response
                    progress_bar = st.progress(0)
                    for i in range(100):
                        progress_bar.progress(i + 1)
                    
                    st.success(f"Successfully ingested {num_conversations} conversations!")
                    
                    # Show processing results
                    results = {
                        "conversations_processed": num_conversations,
                        "issues_extracted": num_conversations * 2,
                        "solutions_identified": num_conversations * 1.5,
                        "pii_redacted": validate_pii,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    st.subheader("Processing Results")
                    st.json(results)
                    
    except Exception as e:
        st.error(f"Error parsing file: {str(e)}")

# Ingestion API placeholder
st.divider()
st.info("""
**📝 Note for Developer**: 
Add your ingestion API endpoint in the code. The ingestion API should be called here:
```python
# Your ingestion API call
response = requests.post(
    f"{api_base}/api/v1/ingest",
    headers={"Content-Type": "application/json"},
    json=conversation_data
)
```
""")