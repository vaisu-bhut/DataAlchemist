import streamlit as st
import requests
import json
from datetime import datetime

st.set_page_config(page_title="Chat Interface", page_icon="💬", layout="wide")

# Custom CSS for better chat UI
st.markdown("""
<style>
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #E3F2FD;
        margin-left: 20%;
    }
    .assistant-message {
        background-color: #F5F5F5;
        margin-right: 20%;
    }
    .source-card {
        background-color: #FAFAFA;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        padding: 12px;
        margin-top: 8px;
        transition: all 0.3s ease;
    }
    .source-card:hover {
        background-color: #F5F5F5;
        border-color: #1976D2;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .source-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    .relevance-badge {
        background: linear-gradient(90deg, #4CAF50, #8BC34A);
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
    }
    .confidence-meter {
        background-color: #E0E0E0;
        height: 8px;
        border-radius: 4px;
        overflow: hidden;
        margin: 8px 0;
    }
    .confidence-fill {
        height: 100%;
        background: linear-gradient(90deg, #2196F3, #03A9F4);
        transition: width 0.3s ease;
    }
    .answer-section {
        background-color: white;
        border-left: 4px solid #2196F3;
        padding: 16px;
        margin: 12px 0;
        border-radius: 4px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

st.title("💬 AI Support Chat Interface")

# API Base URL from session state
api_base = st.session_state.get('api_base_url', 'https://agentic-system-512754882743.us-east1.run.app')

# Initialize chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Sidebar for customer context
with st.sidebar:
    st.header("Customer Context")
    customer_id = st.text_input("Customer ID", value="customer_001", key="customer_id")
    
    if st.button("Load Customer History"):
        try:
            response = requests.get(f"{api_base}/api/v1/analytics/customers/{customer_id}/issues")
            if response.status_code == 200:
                history = response.json()
                st.success("Customer history loaded!")
                
                if 'issues' in history:
                    st.subheader("Previous Issues")
                    for issue in history['issues'][:5]:  # Show last 5 issues
                        with st.expander(f"{issue.get('date', 'N/A')} - {issue.get('type', 'Unknown')}"):
                            st.write(f"**Status**: {issue.get('status', 'N/A')}")
                            st.write(f"**Resolution**: {issue.get('resolution', 'N/A')}")
            else:
                st.error("Failed to load customer history")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    st.divider()
    
    # Chat settings
    st.subheader("Chat Settings")
    context_enabled = st.checkbox("Enable Context", value=True)
    show_sources = st.checkbox("Show Source Details", value=True)
    show_confidence = st.checkbox("Show Confidence Score", value=True)
    
    if st.button("Clear Chat History", type="secondary"):
        st.session_state.chat_history = []
        st.rerun()

# Main chat interface
col1, col2 = st.columns([3, 1])

with col1:
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        # Display chat history
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.write(message["content"])
            else:  # assistant
                with st.chat_message("assistant", avatar="🤖"):
                    # Display main answer
                    if "error" in message:
                        st.error(message["content"])
                    else:
                        # Main answer in a highlighted box
                        st.markdown(f"""
                        <div class="answer-section">
                            <strong>Solution:</strong><br>
                            {message["content"]}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Confidence score if available
                        if show_confidence and "confidence" in message.get("metadata", {}):
                            confidence = message["metadata"]["confidence"]
                            confidence_percent = confidence * 100
                            
                            col_conf1, col_conf2 = st.columns([1, 3])
                            with col_conf1:
                                st.metric("Confidence", f"{confidence_percent:.0f}%")
                            with col_conf2:
                                st.progress(confidence)
                        
                        # Display sources if available and enabled
                        if show_sources and "sources" in message.get("metadata", {}) and message["metadata"]["sources"]:
                            with st.expander(f"📚 View {len(message['metadata']['sources'])} Supporting Sources", expanded=False):
                                sources = message["metadata"]["sources"]
                                
                                # Create a scrollable container for sources
                                sources_container = st.container(height=400)  # Fixed height for scrolling
                                
                                with sources_container:
                                    # Display ALL sources with index
                                    for idx, source in enumerate(sources, 1):
                                        conv_id = source.get("conversation_id", "Unknown")
                                        source_id = source.get("source_id", "")
                                        relevance = source.get("relevance_score", 0) * 100
                                        
                                        # Create a styled container for each source
                                        with st.container():
                                            # Header with source number and conversation ID
                                            col_header1, col_header2 = st.columns([3, 1])
                                            with col_header1:
                                                st.markdown(f"**Source {idx} - {conv_id}**")
                                            with col_header2:
                                                st.markdown(f"**Relevance: {relevance:.1f}%**")
                                            
                                            # Progress bar for relevance
                                            st.progress(relevance / 100)
                                            
                                            # Snippet content
                                            snippet = source.get("snippet", "No snippet available")
                                            
                                            # Use text_area for long snippets (allows scrolling within)
                                            if len(snippet) > 200:
                                                # For long snippets, use text_area with height control
                                                st.text_area(
                                                    "Snippet:",
                                                    value=snippet,
                                                    height=100,
                                                    disabled=True,
                                                    key=f"snippet_{message.get('timestamp', '')}_{idx}"
                                                )
                                            else:
                                                # For short snippets, just display as text
                                                st.text(snippet)
                                            
                                            # Show source ID in small text
                                            st.caption(f"Source ID: {source_id[:20]}..." if len(source_id) > 20 else f"Source ID: {source_id}")
                                            
                                            # Add divider between sources (except for last one)
                                            if idx < len(sources):
                                                st.divider()
                        
                        # Show escalation status if needed
                        if "escalate_to_human" in message.get("metadata", {}) and message["metadata"]["escalate_to_human"]:
                            st.warning("⚠️ This query has been flagged for human escalation")
    
    # Input area
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        # Make API call
        with st.spinner("AI is analyzing your query..."):
            try:
                payload = {
                    "query": user_input,
                    "customer_id": customer_id
                }
                
                if context_enabled:
                    payload["use_context"] = True
                
                response = requests.post(
                    f"{api_base}/api/v1/chat",
                    headers={"Content-Type": "application/json"},
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract the answer (handle both 'answer' and 'response' keys)
                    answer = data.get("answer", data.get("response", "I couldn't generate a response."))
                    
                    # Add AI response to history with proper metadata
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": answer,
                        "metadata": {
                            "confidence": data.get("confidence", 0),
                            "sources": data.get("sources", []),
                            "escalate_to_human": data.get("escalate_to_human", False),
                            "correlation_id": data.get("correlation_id", ""),
                            "reasoning": data.get("reasoning", "")
                        },
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": f"I apologize, but I encountered an issue processing your request. (Status: {response.status_code})",
                        "error": True,
                        "timestamp": datetime.now().isoformat()
                    })
                    
            except requests.exceptions.Timeout:
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": "The request took too long to process. Please try again.",
                    "error": True,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": f"An unexpected error occurred: {str(e)}",
                    "error": True,
                    "timestamp": datetime.now().isoformat()
                })
        
        # Rerun to update the display
        st.rerun()

with col2:
    st.subheader("Quick Actions")
    
    # Common queries
    st.write("**Common Questions:**")
    
    common_queries = [
        "How to cancel subscription on my account",
        "How do I reset my password?",
        "Billing issue with my subscription",
        "Can't access my dashboard",
        "Need help with integration"
    ]
    
    for query in common_queries:
        if st.button(query, key=f"quick_{query}", use_container_width=True):
            # Add user message to history
            st.session_state.chat_history.append({
                "role": "user",
                "content": query,
                "timestamp": datetime.now().isoformat()
            })
            
            # Make API call (same as regular chat)
            with st.spinner("Processing..."):
                try:
                    payload = {
                        "query": query,
                        "customer_id": customer_id
                    }
                    
                    if context_enabled:
                        payload["use_context"] = True
                    
                    response = requests.post(
                        f"{api_base}/api/v1/chat",
                        headers={"Content-Type": "application/json"},
                        json=payload,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Extract the answer (handle both 'answer' and 'response' keys)
                        answer = data.get("answer", data.get("response", "I couldn't generate a response."))
                        
                        # Add AI response to history
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": answer,
                            "metadata": {
                                "confidence": data.get("confidence", 0),
                                "sources": data.get("sources", []),
                                "escalate_to_human": data.get("escalate_to_human", False),
                                "correlation_id": data.get("correlation_id", ""),
                                "reasoning": data.get("reasoning", "")
                            },
                            "timestamp": datetime.now().isoformat()
                        })
                        
                    else:
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": f"API Error: Status {response.status_code}",
                            "error": True,
                            "timestamp": datetime.now().isoformat()
                        })
                        
                except Exception as e:
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": f"Error: {str(e)}",
                        "error": True,
                        "timestamp": datetime.now().isoformat()
                    })
            
            st.rerun()
    
    st.divider()
    
    # Session metrics
    if st.session_state.chat_history:
        st.subheader("📊 Session Stats")
        total_messages = len(st.session_state.chat_history)
        user_messages = sum(1 for m in st.session_state.chat_history if m["role"] == "user")
        ai_messages = sum(1 for m in st.session_state.chat_history if m["role"] == "assistant")
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric("Total", total_messages)
        with col_m2:
            st.metric("AI", ai_messages)
        
        # Export chat
        if st.button("💾 Export Chat", use_container_width=True):
            chat_export = json.dumps(st.session_state.chat_history, indent=2)
            st.download_button(
                label="Download JSON",
                data=chat_export,
                file_name=f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )