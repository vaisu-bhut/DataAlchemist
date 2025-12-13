import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="Customer Insights", page_icon="🔍", layout="wide")

st.title("🔍 Customer Insights")

# API Base URL from session state
api_base = st.session_state.get('api_base_url', 'https://agentic-system-512754882743.us-east1.run.app')

# Initialize session states
if 'show_customer_data' not in st.session_state:
    st.session_state.show_customer_data = False
if 'selected_customer' not in st.session_state:
    st.session_state.selected_customer = None
if 'view_all' not in st.session_state:
    st.session_state.view_all = False

# Fetch all customers for dropdown
all_customers = []
try:
    response = requests.get(f"{api_base}/api/v1/analytics/customers")
    if response.status_code == 200:
        customers_data = response.json()
        all_customers = [cust['customer_id'] for cust in customers_data.get('customers', [])]
except:
    all_customers = []

# Customer search with dropdown
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    if all_customers:
        # Use selectbox with all available customers
        customer_id = st.selectbox(
            "Select or Enter Customer ID",
            options=[''] + all_customers,
            index=0,
            help="Select from available customers or type to search"
        )
    else:
        # Fallback to text input if API fails
        customer_id = st.text_input("Enter Customer ID", value="")
        
with col2:
    st.write("")  # Spacing
    st.write("")  # Spacing
    if st.button("Search Customer", type="primary", disabled=not customer_id):
        if customer_id:
            st.session_state.show_customer_data = True
            st.session_state.selected_customer = customer_id
            st.session_state.view_all = False
            
with col3:
    st.write("")  # Spacing
    st.write("")  # Spacing
    if st.button("View All Customers"):
        st.session_state.view_all = True
        st.session_state.show_customer_data = False

# Only show customer data if search was clicked
if st.session_state.show_customer_data and st.session_state.selected_customer:
    customer_id = st.session_state.selected_customer
    
    # Fetch customer-specific issues data
    try:
        response_issues = requests.get(f"{api_base}/api/v1/analytics/customers/{customer_id}/issues")
        
        if response_issues.status_code == 200:
            issues_data = response_issues.json()
            
            # Display customer profile header
            st.header(f"Customer Profile: {customer_id}")
            
            # Calculate metrics from the issues data
            total_issues = issues_data.get('total_issues', 0)
            issues_list = issues_data.get('issues', [])
            
            # Count resolved vs open issues
            resolved_count = sum(1 for issue in issues_list if issue.get('status') == 'resolved')
            open_count = sum(1 for issue in issues_list if issue.get('status') == 'open')
            
            # Calculate resolution rate
            resolution_rate = (resolved_count / total_issues * 100) if total_issues > 0 else 0
            
            # Get unique conversation count
            unique_conversations = len(set(issue.get('conversation_id', '') for issue in issues_list))
            
            # Display main metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Conversations", unique_conversations)
            
            with col2:
                st.metric("Issues Reported", total_issues)
            
            with col3:
                st.metric("Resolution Rate", f"{resolution_rate:.1f}%")
            
            with col4:
                st.metric("Open Issues", open_count, delta=f"-{resolved_count} resolved" if resolved_count > 0 else None)
            
            # Tabs for detailed information
            tab1, tab2, tab3, tab4 = st.tabs(["Issue History", "Conversation Timeline", "Patterns", "Recommendations"])
            
            with tab1:
                st.subheader("📋 Issue History")
                
                if issues_list:
                    # Convert to DataFrame for easier manipulation
                    df_issues = pd.DataFrame(issues_list)
                    
                    # Parse timestamps
                    df_issues['occurred_at'] = pd.to_datetime(df_issues['occurred_at'])
                    if 'resolved_at' in df_issues.columns:
                        df_issues['resolved_at'] = pd.to_datetime(df_issues['resolved_at'])
                    
                    # Issue status distribution
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Status distribution pie chart
                        status_counts = df_issues['status'].value_counts()
                        fig_status = px.pie(
                            values=status_counts.values,
                            names=status_counts.index,
                            title="Issue Status Distribution",
                            color_discrete_map={'open': '#FF6B6B', 'resolved': '#4ECDC4', 'pending': '#FFE66D'}
                        )
                        st.plotly_chart(fig_status, use_container_width=True)
                    
                    with col2:
                        # Issues by type
                        issue_types = df_issues['issue_description'].value_counts()
                        fig_types = px.bar(
                            x=issue_types.values,
                            y=issue_types.index,
                            orientation='h',
                            title="Issues by Type",
                            labels={'x': 'Count', 'y': 'Issue Type'}
                        )
                        st.plotly_chart(fig_types, use_container_width=True)
                    
                    # Detailed issue table
                    st.subheader("Detailed Issues")
                    
                    # Prepare display dataframe
                    display_df = df_issues[['issue_description', 'conversation_id', 'occurred_at', 'status', 'handled_by_agent']].copy()
                    display_df['occurred_at'] = display_df['occurred_at'].dt.strftime('%Y-%m-%d %H:%M')
                    display_df.columns = ['Issue', 'Conversation ID', 'Occurred At', 'Status', 'Agent']
                    
                    # Add status indicator
                    display_df['Status'] = display_df['Status'].apply(
                        lambda x: f"🔴 {x.title()}" if x == 'open' else f"🟢 {x.title()}"
                    )
                    
                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Issue summary
                    unique_issues = df_issues.groupby('issue_description').agg({
                        'issue_id': 'count',
                        'status': lambda x: (x == 'open').sum()
                    }).rename(columns={'issue_id': 'total_count', 'status': 'open_count'})
                    
                    st.subheader("📊 Issue Summary")
                    for issue_desc, row in unique_issues.iterrows():
                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            st.write(f"**{issue_desc}**")
                        with col2:
                            st.write(f"Total: {row['total_count']}")
                        with col3:
                            if row['open_count'] > 0:
                                st.write(f"🔴 Open: {row['open_count']}")
                            else:
                                st.write("✅ All Resolved")
                else:
                    st.info("No issues found for this customer")
            
            with tab2:
                st.subheader("📅 Conversation Timeline")
                
                if issues_list:
                    # Create timeline visualization
                    timeline_data = []
                    for issue in issues_list:
                        timeline_data.append({
                            'date': pd.to_datetime(issue['occurred_at']).strftime('%Y-%m-%d'),
                            'time': pd.to_datetime(issue['occurred_at']).strftime('%H:%M'),
                            'type': issue['issue_description'],
                            'conversation': issue['conversation_id'],
                            'agent': issue['handled_by_agent'],
                            'status': issue['status']
                        })
                    
                    df_timeline = pd.DataFrame(timeline_data)
                    
                    # Timeline visualization
                    fig_timeline = px.scatter(
                        df_timeline, 
                        x='date', 
                        y='agent',
                        color='status',
                        hover_data=['type', 'conversation', 'time'],
                        title="Customer Interaction Timeline",
                        color_discrete_map={'open': '#FF6B6B', 'resolved': '#4ECDC4'}
                    )
                    fig_timeline.update_traces(marker=dict(size=15))
                    st.plotly_chart(fig_timeline, use_container_width=True)
                    
                    # Conversation details
                    for _, row in df_timeline.iterrows():
                        status_icon = "🔴" if row['status'] == 'open' else "🟢"
                        with st.expander(f"{row['date']} {row['time']} - {row['type']} {status_icon}"):
                            st.write(f"**Conversation**: {row['conversation']}")
                            st.write(f"**Handled by**: {row['agent']}")
                            st.write(f"**Status**: {row['status'].title()}")
                else:
                    st.info("No conversation history available")
            
            with tab3:
                st.subheader("🔍 Customer Patterns")
                
                if issues_list:
                    df_analysis = pd.DataFrame(issues_list)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Agent interaction pattern
                        agent_counts = df_analysis['handled_by_agent'].value_counts()
                        st.info(f"""
                        **Agent Interactions:**
                        - Primary Agent: {agent_counts.index[0] if len(agent_counts) > 0 else 'N/A'}
                        - Total Agents Involved: {len(agent_counts)}
                        - Most Issues Handled: {agent_counts.values[0] if len(agent_counts) > 0 else 0} issues
                        """)
                    
                    with col2:
                        # Issue patterns
                        issue_patterns = df_analysis['issue_description'].value_counts()
                        st.warning(f"""
                        **Issue Patterns:**
                        - Most Common Issue: {issue_patterns.index[0] if len(issue_patterns) > 0 else 'N/A'}
                        - Unique Issue Types: {len(issue_patterns)}
                        - Unresolved Issues: {open_count}
                        """)
                    
                    # Issue recurrence
                    st.subheader("Issue Recurrence Analysis")
                    recurrence_data = df_analysis.groupby('issue_description').size().reset_index(name='occurrences')
                    
                    fig_recurrence = px.bar(
                        recurrence_data,
                        x='issue_description',
                        y='occurrences',
                        title="Issue Frequency",
                        color='occurrences',
                        color_continuous_scale='Reds'
                    )
                    st.plotly_chart(fig_recurrence, use_container_width=True)
                else:
                    st.info("No data available for pattern analysis")
            
            with tab4:
                st.subheader("💡 AI Recommendations")
                
                if open_count > 0:
                    st.warning(f"""
                    **⚠️ Immediate Actions Required:**
                    
                    1. **Open Issues**: Customer has {open_count} unresolved issues that need attention
                    
                    2. **Priority Issues**: Focus on resolving the following:
                    """)
                    
                    # List open issues
                    open_issues = [issue for issue in issues_list if issue['status'] == 'open']
                    for i, issue in enumerate(open_issues[:3], 1):  # Show top 3
                        st.write(f"   - {issue['issue_description']} (Conv: {issue['conversation_id']})")
                    
                    st.info("""
                    **📈 Recommended Actions:**
                    
                    3. **Escalation**: Consider escalating to senior support for faster resolution
                    
                    4. **Follow-up**: Schedule immediate follow-up with customer
                    
                    5. **Compensation**: Consider offering service credit for multiple unresolved issues
                    """)
                else:
                    st.success("""
                    **✅ Customer Status: Good Standing**
                    
                    All previous issues have been resolved. Recommended actions:
                    
                    1. **Preventive Care**: Monitor for similar issues in the future
                    
                    2. **Satisfaction Check**: Send satisfaction survey
                    
                    3. **Retention**: Consider loyalty rewards for resolved issues
                    """)
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.button("Schedule Follow-up", use_container_width=True)
                with col2:
                    st.button("Escalate Issues", use_container_width=True, disabled=(open_count == 0))
                with col3:
                    st.button("Send Survey", use_container_width=True)
                    
        elif response_issues.status_code == 404:
            st.warning(f"No data found for customer: {customer_id}")
            st.info("This customer may not have any recorded interactions yet.")
        else:
            st.error(f"Error fetching customer data: API returned status {response_issues.status_code}")
            
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        st.info("Please check your connection and try again.")

# View all customers section
elif st.session_state.view_all:
    st.header("All Customers")
    
    try:
        response = requests.get(f"{api_base}/api/v1/analytics/customers")
        if response.status_code == 200:
            data = response.json()
            
            if 'customers' in data:
                df_customers = pd.DataFrame(data['customers'])
                
                # Calculate resolution rate
                df_customers['resolution_rate'] = (df_customers['resolved_conversations'] / df_customers['total_conversations'] * 100).round(1)
                
                # Add filters
                st.subheader("🔍 Filter Customers")
                col1, col2, col3 = st.columns(3)
                with col1:
                    min_conversations = st.number_input("Min Conversations", min_value=0, value=0)
                with col2:
                    min_resolved = st.number_input("Min Resolved", min_value=0, value=0)
                with col3:
                    resolution_threshold = st.slider("Min Resolution Rate (%)", 0, 100, 0)
                
                # Apply filters
                filtered_df = df_customers[
                    (df_customers['total_conversations'] >= min_conversations) &
                    (df_customers['resolved_conversations'] >= min_resolved) &
                    (df_customers['resolution_rate'] >= resolution_threshold)
                ]
                
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Customers", data.get('total', len(df_customers)))
                with col2:
                    st.metric("Showing", len(filtered_df))
                with col3:
                    avg_resolution = filtered_df['resolution_rate'].mean()
                    st.metric("Avg Resolution Rate", f"{avg_resolution:.1f}%")
                with col4:
                    total_conversations = filtered_df['total_conversations'].sum()
                    st.metric("Total Conversations", total_conversations)
                
                # Display filtered results
                st.subheader("📊 Customer List")
                
                # Add action column for viewing details
                filtered_df['Actions'] = filtered_df['customer_id'].apply(
                    lambda x: f'View {x}'
                )
                
                # Display table with better formatting
                display_df = filtered_df[['customer_id', 'total_conversations', 'resolved_conversations', 'resolution_rate']].copy()
                display_df.columns = ['Customer ID', 'Total Conversations', 'Resolved', 'Resolution Rate (%)']
                
                # Add status indicator
                display_df['Status'] = display_df['Resolution Rate (%)'].apply(
                    lambda x: '🟢 Good' if x >= 80 else ('🟡 Fair' if x >= 50 else '🔴 Needs Attention')
                )
                
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Resolution Rate (%)": st.column_config.ProgressColumn(
                            "Resolution Rate (%)",
                            format="%.1f%%",
                            min_value=0,
                            max_value=100,
                        ),
                    }
                )
                
                # Quick view section
                st.subheader("🎯 Quick Actions")
                selected_customer = st.selectbox("Select customer to view details:", 
                                                options=[''] + filtered_df['customer_id'].tolist())
                if selected_customer and st.button("View Selected Customer"):
                    st.session_state.show_customer_data = True
                    st.session_state.selected_customer = selected_customer
                    st.session_state.view_all = False
                    st.rerun()
                
                # Export option
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Customer Data (CSV)",
                    data=csv,
                    file_name=f"customers_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
    except Exception as e:
        st.error(f"Error fetching customers: {str(e)}")
else:
    # Initial state - show instructions
    st.info("👆 Please select a customer from the dropdown and click 'Search Customer' to view their profile, or click 'View All Customers' to see the complete list.")
    
    # Show available customers preview
    if all_customers:
        with st.expander("📋 Available Customers Preview"):
            st.write(f"Total customers in system: {len(all_customers)}")
            st.write("Sample customer IDs:", ', '.join(all_customers[:10]))
            if len(all_customers) > 10:
                st.write(f"... and {len(all_customers) - 10} more")