import streamlit as st
import requests
import json
from datetime import datetime

st.set_page_config(page_title="Chat Interface", page_icon="💬", layout="wide")

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
    auto_suggest = st.checkbox("Show Suggestions", value=True)
    
    if st.button("Clear Chat History"):
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
            with st.chat_message(message["role"]):
                st.write(message["content"])
                if "metadata" in message:
                    with st.expander("Details"):
                        st.json(message["metadata"])
    
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
        with st.spinner("AI is thinking..."):
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
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Add AI response to history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": data.get("response", "I couldn't generate a response."),
                        "metadata": {
                            "confidence": data.get("confidence", 0),
                            "sources": data.get("sources", []),
                            "suggested_actions": data.get("suggested_actions", [])
                        },
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": "I'm sorry, I encountered an error processing your request.",
                        "timestamp": datetime.now().isoformat()
                    })
                    
            except Exception as e:
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": f"Error: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                })
        
        # Rerun to update the display
        st.rerun()

with col2:
    st.subheader("Quick Actions")
    
    # Common queries
    st.write("**Common Questions:**")
    
    common_queries = [
        "I can't downgrade my account",
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
            with st.spinner("AI is thinking..."):
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
                        timeout=10  # Add timeout
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Debug: Check what the API actually returns
                        print("API Response:", data)  # This will show in your terminal
                        
                        # Get the actual response - adjust based on your API's response structure
                        ai_response = data.get("response") or data.get("message") or data.get("answer") or data.get("text")
                        
                        # Only use fallback if there's truly no response
                        if not ai_response:
                            ai_response = "I received your message but couldn't generate a proper response. Please try again."
                        
                        # Add AI response to history
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": ai_response,
                            "metadata": {
                                "confidence": data.get("confidence", 0),
                                "sources": data.get("sources", []),
                                "suggested_actions": data.get("suggested_actions", [])
                            },
                            "timestamp": datetime.now().isoformat()
                        })
                        
                    else:
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": f"API Error: Status {response.status_code} - {response.text}",
                            "timestamp": datetime.now().isoformat()
                        })
                        
                except requests.exceptions.Timeout:
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": "Request timed out. Please try again.",
                        "timestamp": datetime.now().isoformat()
                    })
                except Exception as e:
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": f"Error: {str(e)}",
                        "timestamp": datetime.now().isoformat()
                    })
            
            st.rerun()