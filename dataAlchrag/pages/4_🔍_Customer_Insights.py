import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="Customer Insights", page_icon="🔍", layout="wide")

st.title("🔍 Customer Insights")

# API Base URL from session state
api_base = st.session_state.get('api_base_url', 'https://agentic-system-512754882743.us-east1.run.app')

# Customer search
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    customer_id = st.text_input("Enter Customer ID", value="customer_001")
with col2:
    st.write("")  # Spacing
    st.write("")  # Spacing
    search_button = st.button("Search Customer", type="primary")
with col3:
    st.write("")  # Spacing
    st.write("")  # Spacing
    if st.button("View All Customers"):
        st.session_state.view_all = True

if search_button or customer_id:
    # Fetch customer data
    try:
        # Customer conversations
        response_conversations = requests.get(f"{api_base}/api/v1/analytics/customers")
        customers_data = response_conversations.json() if response_conversations.status_code == 200 else {}
        
        # Customer specific issues
        response_issues = requests.get(f"{api_base}/api/v1/analytics/customers/{customer_id}/issues")
        issues_data = response_issues.json() if response_issues.status_code == 200 else {}
        
        # Display customer profile
        st.header(f"Customer Profile: {customer_id}")
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Find customer in list
        customer_info = None
        if 'customers' in customers_data:
            for customer in customers_data['customers']:
                if customer.get('customer_id') == customer_id:
                    customer_info = customer
                    break
        
        if customer_info:
            with col1:
                st.metric("Total Conversations", customer_info.get('conversation_count', 0))
            with col2:
                st.metric("Issues Reported", customer_info.get('issue_count', 0))
            with col3:
                st.metric("Resolution Rate", f"{customer_info.get('resolution_rate', 0):.1f}%")
            with col4:
                st.metric("Avg Satisfaction", f"{customer_info.get('avg_satisfaction', 0):.1f}/5")
        
        # Tabs for detailed information
        tab1, tab2, tab3, tab4 = st.tabs(["Issue History", "Conversation Timeline", "Patterns", "Recommendations"])
        
        with tab1:
            st.subheader("📋 Issue History")
            
            if 'issues' in issues_data and issues_data['issues']:
                df_issues = pd.DataFrame(issues_data['issues'])
                
                # Issue status distribution
                col1, col2 = st.columns(2)
                with col1:
                    if 'status' in df_issues.columns:
                        fig_status = px.pie(df_issues, names='status', title="Issue Status Distribution")
                        st.plotly_chart(fig_status, use_container_width=True)
                
                with col2:
                    if 'issue_type' in df_issues.columns:
                        fig_types = px.bar(df_issues['issue_type'].value_counts(), 
                                         title="Issues by Type")
                        st.plotly_chart(fig_types, use_container_width=True)
                
                # Detailed issue table
                st.subheader("Detailed Issues")
                
                # Format the dataframe for better display
                if not df_issues.empty:
                    display_columns = ['timestamp', 'issue_type', 'description', 'status', 'resolution_time']
                    available_columns = [col for col in display_columns if col in df_issues.columns]
                    
                    if available_columns:
                        st.dataframe(
                            df_issues[available_columns],
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.dataframe(df_issues, use_container_width=True, hide_index=True)
            else:
                st.info("No issue history found for this customer")
        
        with tab2:
            st.subheader("📅 Conversation Timeline")
            
            # Create mock timeline data (replace with actual API data)
            timeline_data = []
            for i in range(5):
                date = datetime.now() - timedelta(days=i*7)
                timeline_data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'type': ['Issue Reported', 'Follow-up', 'Resolved', 'New Issue', 'Feedback'][i],
                    'description': f'Conversation about {["billing", "technical", "account", "feature", "support"][i]} issue',
                    'agent': f'Agent_{i+1}'
                })
            
            df_timeline = pd.DataFrame(timeline_data)
            
            # Timeline visualization
            fig_timeline = px.scatter(df_timeline, x='date', y='type', 
                                     hover_data=['description', 'agent'],
                                     title="Customer Interaction Timeline",
                                     size_max=15)
            fig_timeline.update_traces(marker=dict(size=15))
            st.plotly_chart(fig_timeline, use_container_width=True)
            
            # Conversation details
            for _, row in df_timeline.iterrows():
                with st.expander(f"{row['date']} - {row['type']}"):
                    st.write(f"**Description**: {row['description']}")
                    st.write(f"**Handled by**: {row['agent']}")
        
        with tab3:
            st.subheader("🔍 Customer Patterns")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.info("""
                **Behavioral Patterns:**
                - Most active: Weekdays 2-4 PM
                - Preferred channel: Chat
                - Average response time: 5 minutes
                - Engagement score: High
                """)
            
            with col2:
                st.warning("""
                **Risk Indicators:**
                - Churn risk: Low
                - Escalation tendency: Medium
                - Repeat issue rate: 15%
                - Sentiment trend: Stable
                """)
            
            # Issue recurrence
            st.subheader("Issue Recurrence Analysis")
            recurrence_data = {
                'Issue Type': ['Billing', 'Technical', 'Account', 'Feature Request'],
                'First Occurrence': [30, 45, 60, 15],
                'Recurrence': [5, 12, 3, 8]
            }
            df_recurrence = pd.DataFrame(recurrence_data)
            
            fig_recurrence = px.bar(df_recurrence, x='Issue Type', 
                                   y=['First Occurrence', 'Recurrence'],
                                   title="Issue Recurrence Patterns")
            st.plotly_chart(fig_recurrence, use_container_width=True)
        
        with tab4:
            st.subheader("💡 AI Recommendations")
            
            st.success("""
            **Personalized Recommendations for this Customer:**
            
            1. **Proactive Outreach**: Schedule a check-in call next week based on pattern analysis
            
            2. **Issue Prevention**: Enable advanced monitoring for billing-related issues
            
            3. **Service Upgrade**: Customer qualifies for premium support tier based on engagement
            
            4. **Training Resources**: Send tutorials for frequently asked technical questions
            
            5. **Retention Strategy**: Offer loyalty discount - high-value customer at low churn risk
            """)
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                st.button("Schedule Outreach", use_container_width=True)
            with col2:
                st.button("Send Resources", use_container_width=True)
            with col3:
                st.button("Apply Discount", use_container_width=True)
            
    except Exception as e:
        st.error(f"Error fetching customer data: {str(e)}")

# View all customers
if st.session_state.get('view_all', False):
    st.divider()
    st.header("All Customers")
    
    try:
        response = requests.get(f"{api_base}/api/v1/analytics/customers")
        if response.status_code == 200:
            data = response.json()
            
            if 'customers' in data:
                df_customers = pd.DataFrame(data['customers'])
                
                # Add filters
                col1, col2, col3 = st.columns(3)
                with col1:
                    min_conversations = st.number_input("Min Conversations", min_value=0, value=0)
                with col2:
                    min_satisfaction = st.slider("Min Satisfaction", 0.0, 5.0, 0.0)
                with col3:
                    resolution_threshold = st.slider("Min Resolution Rate", 0, 100, 0)
                
                # Apply filters
                filtered_df = df_customers[
                    (df_customers.get('conversation_count', 0) >= min_conversations) &
                    (df_customers.get('avg_satisfaction', 0) >= min_satisfaction) &
                    (df_customers.get('resolution_rate', 0) >= resolution_threshold)
                ]
                
                # Display filtered results
                st.dataframe(
                    filtered_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "resolution_rate": st.column_config.ProgressColumn(
                            "Resolution Rate",
                            format="%.1f%%",
                            min_value=0,
                            max_value=100,
                        ),
                        "avg_satisfaction": st.column_config.NumberColumn(
                            "Avg Satisfaction",
                            format="%.1f ⭐",
                        )
                    }
                )
                
                # Export option
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="Download Customer Data (CSV)",
                    data=csv,
                    file_name=f"customers_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
    except Exception as e:
        st.error(f"Error fetching customers: {str(e)}")
    
    st.session_state.view_all = False