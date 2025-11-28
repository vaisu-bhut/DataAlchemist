import streamlit as st
import requests
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Customer Support RAG System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if 'api_base_url' not in st.session_state:
    st.session_state.api_base_url = 'https://agentic-system-512754882743.us-east1.run.app'

# Remove the custom CSS that might be causing issues
# Just use simple styling
# st.markdown("""
#     <style>
#     .block-container {
#         padding-top: 1rem;
#         padding-bottom: 1rem;
#     }
#     </style>
# """, unsafe_allow_html=True)

# Sidebar


with st.sidebar:
    st.title("⚙️ Configuration")
    api_url = st.text_input("API Base URL", value=st.session_state.api_base_url)
    if api_url:
        st.session_state.api_base_url = api_url
    
    st.divider()
    
    st.title("📋 System Overview")
    st.info("""
    **How it Works:**
    
    1️⃣ **Ingestii** - Upload chat logs
    2️⃣ **Process** - AI extracts patterns
    3️⃣ **Store** - Knowledge graph database
    4️⃣ **Respond** - Intelligent answers
    """)

# Main content - Make sure content is visible
st.title("🤖 Customer Support RAG System")
st.markdown("---")

# Main content area with tabs
tab1, tab2, tab3 = st.tabs(["🏠 Overview", "📈 Quick Stats", "🚀 Getting Started"])

with tab1:
    st.header("Welcome to the Customer Support RAG System")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        This system leverages advanced AI to transform your customer support operations:
        
        - **🔍 Semantic Search**: Find relevant solutions instantly
        - **🧠 Knowledge Extraction**: Automatically learn from conversations
        - **🔒 Privacy-First**: Automatic PII redaction
        - **📊 Analytics**: Deep insights into support patterns
        - **⚡ Real-time Responses**: Instant, personalized answers
        """)
    
    with col2:
        # Using a placeholder instead of external image
        st.info("RAG System Visual Placeholder")

with tab2:
    st.header("System Status")
    
    # Fetch summary analytics with error handling
    try:
        with st.spinner("Loading analytics..."):
            response = requests.get(
                f"{st.session_state.api_base_url}/api/v1/analytics/summary",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Conversations", "1,234")
                with col2:
                    st.metric("Unique Customers", "456")
                with col3:
                    st.metric("Issues Resolved", "890")
                with col4:
                    st.metric("Avg Resolution Time", "2.5h")
                
            #     col1, col2, col3, col4 = st.columns(4)
                
            #     with col1:
            #         st.metric("Total Conversations", data.get('total_conversations', 0))
            #     with col2:
            #         st.metric("Unique Customers", data.get('unique_customers', 0))
            #     with col3:
            #         st.metric("Issues Resolved", data.get('issues_resolved', 0))
            #     with col4:
            #         st.metric("Avg Resolution Time", f"{data.get('avg_resolution_time', 0):.1f}h")
            # else:
            #     st.warning(f"API returned status code: {response.status_code}")
            #     st.info("Using demo data for display")
                
                # Show demo data
               
    except requests.exceptions.RequestException as e:
        st.warning("Unable to connect to API")
        st.info("Showing demo data")
        
        # Show demo data
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Conversations", "1,234")
        with col2:
            st.metric("Unique Customers", "456")
        with col3:
            st.metric("Issues Resolved", "890")
        with col4:
            st.metric("Avg Resolution Time", "2.5h")

with tab3:
    st.header("Getting Started Guide")
    
    st.markdown("""
    ### Step 1: Data Ingestion
    Navigate to the **Data Ingestion** page to upload your historical chat logs.
    
    ### Step 2: Explore Analytics
    Check the **Analytics Dashboard** to understand your support patterns.
    
    ### Step 3: Test the Chat
    Try the **Chat Interface** to see AI-powered responses in action.
    
    ### Step 4: Customer Insights
    Dive into **Customer Insights** for detailed customer history.
    """)
    
    # Add navigation buttons
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("📊 Go to Analytics"):
            st.info("Navigate to Analytics Dashboard from the sidebar")
    with col2:
        if st.button("💬 Go to Chat"):
            st.info("Navigate to Chat Interface from the sidebar")
    with col3:
        if st.button("📤 Go to Ingestion"):
            st.info("Navigate to Data Ingestion from the sidebar")
    with col4:
        if st.button("🔍 Go to Insights"):
            st.info("Navigate to Customer Insights from the sidebar")

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: gray;'>
    <small>Powered by Advanced RAG Technology | Last Updated: {datetime.now().strftime("%Y-%m-%d %H:%M")}</small>
</div>
""", unsafe_allow_html=True)

# Debug information (remove in production)
with st.expander("🔧 Debug Information"):
    st.write("Session State:", st.session_state)
    st.write("API Base URL:", st.session_state.api_base_url)