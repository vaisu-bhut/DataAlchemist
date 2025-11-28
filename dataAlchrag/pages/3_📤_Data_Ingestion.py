import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Data Ingestion", page_icon="📤", layout="wide")

st.title("📤 Data Ingestion Portal")

# API Base URL from session state
api_base = st.session_state.get('api_base_url', 'https://agentic-system-512754882743.us-east1.run.app')

# Tabs for different ingestion methods
tab1, tab2, tab3 = st.tabs(["File Upload", "Manual Entry", "Batch Processing"])

with tab1:
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

with tab2:
    st.header("✍️ Manual Conversation Entry")
    
    with st.form("manual_entry_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            conversation_id = st.text_input("Conversation ID", value=f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            customer_id = st.text_input("Customer ID", value="customer_001")
            issue_type = st.selectbox("Issue Type", ["billing", "technical", "account", "general", "other"])
        
        with col2:
            resolved = st.checkbox("Resolved", value=False)
            satisfaction_score = st.slider("Satisfaction Score", 1, 5, 3)
            escalated = st.checkbox("Escalated to Human", value=False)
        
        st.subheader("Conversation Messages")
        
        # Dynamic message entry
        num_messages = st.number_input("Number of messages", min_value=2, max_value=20, value=2)
        
        messages = []
        for i in range(num_messages):
            col1, col2 = st.columns([1, 3])
            with col1:
                role = st.selectbox(f"Role {i+1}", ["customer", "agent"], key=f"role_{i}")
            with col2:
                content = st.text_area(f"Message {i+1}", key=f"msg_{i}")
            
            if content:
                messages.append({
                    "role": role,
                    "content": content,
                    "timestamp": datetime.now().isoformat()
                })
        
        submitted = st.form_submit_button("Submit Conversation")
        
        if submitted and messages:
            conversation_data = {
                "conversation_id": conversation_id,
                "customer_id": customer_id,
                "timestamp": datetime.now().isoformat(),
                "messages": messages,
                "metadata": {
                    "resolved": resolved,
                    "issue_type": issue_type,
                    "satisfaction_score": satisfaction_score,
                    "escalated": escalated
                }
            }
            
            st.success("Conversation prepared for ingestion!")
            st.json(conversation_data)
            
            # Add actual API call here
            if st.button("Confirm and Ingest"):
                st.info("Note: Add your ingestion API call here")

with tab3:
    st.header("📊 Batch Processing Status")
    
    # Simulated batch jobs
    batch_jobs = [
        {"id": "batch_001", "status": "completed", "files": 5, "conversations": 150, "progress": 100},
        {"id": "batch_002", "status": "processing", "files": 3, "conversations": 87, "progress": 65},
        {"id": "batch_003", "status": "queued", "files": 2, "conversations": 0, "progress": 0},
    ]
    
    df_batches = pd.DataFrame(batch_jobs)
    
    st.dataframe(
        df_batches,
        column_config={
            "progress": st.column_config.ProgressColumn(
                "Progress",
                help="Processing progress",
                format="%d%%",
                min_value=0,
                max_value=100,
            ),
        },
        hide_index=True,
        use_container_width=True
    )
    
    st.divider()
    
    # New batch upload
    st.subheader("Start New Batch")
    
    uploaded_files = st.file_uploader("Choose multiple JSON files", type=['json'], accept_multiple_files=True)
    
    if uploaded_files:
        st.write(f"Selected {len(uploaded_files)} files for batch processing")
        
        batch_config = st.expander("Batch Configuration")
        with batch_config:
            priority = st.select_slider("Priority", ["low", "medium", "high"])
            parallel_processing = st.checkbox("Enable parallel processing", value=True)
            notification_email = st.text_input("Notification email (optional)")
        
        if st.button("Start Batch Processing"):
            st.success(f"Batch job created with {len(uploaded_files)} files")
            st.balloons()

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