import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Analytics Dashboard", page_icon="📊", layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .top-agent-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #4CAF50;
        margin-bottom: 10px;
    }
    .issue-card {
        background-color: white;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Analytics Dashboard")

# API Base URL from session state
api_base = st.session_state.get('api_base_url', 'https://agentic-system-512754882743.us-east1.run.app')

# Tabs for different analytics
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Summary", "Agent Performance", "Issues", "Resolution Time", "Escalations"])

with tab1:
    st.header("📈 Analytics Summary")
    
    try:
        response = requests.get(f"{api_base}/api/v1/analytics/summary")
        if response.status_code == 200:
            data = response.json()
            
            # Display main metrics with real data
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Conversations",
                    data.get('total_conversations', 0),
                    help="Total number of customer conversations"
                )
            
            with col2:
                st.metric(
                    "Unique Customers",
                    data.get('total_customers', 0),
                    help="Number of unique customers served"
                )
            
            with col3:
                # Calculate resolution rate from the data
                total_convs = data.get('total_conversations', 0)
                if total_convs > 0 and 'top_agents' in data:
                    total_resolved = sum(agent.get('resolved_chats', 0) for agent in data['top_agents'])
                    resolution_rate = (total_resolved / total_convs) * 100
                else:
                    resolution_rate = 0
                
                st.metric(
                    "Resolution Rate",
                    f"{resolution_rate:.1f}%",
                    help="Percentage of conversations resolved"
                )
            
            with col4:
                avg_time = data.get('avg_resolution_time_minutes', 0)
                st.metric(
                    "Avg Resolution Time",
                    f"{avg_time:.1f} min" if avg_time else "N/A",
                    help="Average time to resolve issues"
                )
            
            # Second row of metrics
            col5, col6, col7, col8 = st.columns(4)
            
            with col5:
                st.metric(
                    "Total Issues",
                    data.get('total_issues', 0),
                    help="Unique issues identified"
                )
            
            with col6:
                st.metric(
                    "Total Solutions",
                    data.get('total_solutions', 0),
                    help="Solutions available in knowledge base"
                )
            
            with col7:
                st.metric(
                    "Active Agents",
                    data.get('total_agents', 0),
                    help="Number of active support agents"
                )
            
            with col8:
                # Calculate average chats per agent
                if data.get('total_agents', 0) > 0:
                    avg_chats = data.get('total_conversations', 0) / data.get('total_agents', 1)
                else:
                    avg_chats = 0
                st.metric(
                    "Avg Chats/Agent",
                    f"{avg_chats:.1f}",
                    help="Average conversations per agent"
                )
            
            # Top Issues Section
            if 'top_issues' in data and data['top_issues']:
                st.subheader("🎯 Top Issues")
                
                issues_df = pd.DataFrame(data['top_issues'])
                
                # Create visualization for top issues
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Bar chart of issue occurrences
                    fig_issues = px.bar(
                        issues_df.head(5),
                        x='total_occurrences',
                        y='issue_description',
                        orientation='h',
                        title="Most Common Issues",
                        labels={'total_occurrences': 'Occurrences', 'issue_description': 'Issue'},
                        color='total_occurrences',
                        color_continuous_scale='Blues'
                    )
                    fig_issues.update_layout(height=300)
                    st.plotly_chart(fig_issues, use_container_width=True)
                
                with col2:
                    # Resolution metrics for top issues
                    st.markdown("**Resolution Stats**")
                    for idx, issue in enumerate(issues_df.head(3).itertuples(), 1):
                        resolution_rate = (issue.resolved_count / issue.total_occurrences * 100) if issue.total_occurrences > 0 else 0
                        st.markdown(f"""
                        **Issue {idx}:** {issue.issue_description[:30]}...
                        - Occurrences: {issue.total_occurrences}
                        - Resolved: {issue.resolved_count}
                        - Resolution Rate: {resolution_rate:.0f}%
                        ---
                        """)
            
            # Top Agents Performance Preview
            if 'top_agents' in data and data['top_agents']:
                st.subheader("👥 Top Performing Agents")
                
                agents_df = pd.DataFrame(data['top_agents'])
                
                # Create a performance matrix
                fig_agents = px.scatter(
                    agents_df,
                    x='total_chats',
                    y='resolution_rate',
                    size='resolved_chats',
                    hover_data=['agent_id'],
                    title="Agent Performance Matrix",
                    labels={'total_chats': 'Total Chats', 'resolution_rate': 'Resolution Rate (%)'},
                    color='resolution_rate',
                    color_continuous_scale='Greens'
                )
                fig_agents.update_layout(height=400)
                st.plotly_chart(fig_agents, use_container_width=True)
                
    except Exception as e:
        st.error(f"Error fetching summary data: {str(e)}")
        st.info("Please check your API connection and try again.")

with tab2:
    st.header("👥 Agent Performance")
    
    try:
        response = requests.get(f"{api_base}/api/v1/analytics/summary")  # Using summary endpoint as it has agent data
        if response.status_code == 200:
            data = response.json()
            
            if 'top_agents' in data and data['top_agents']:
                agents_df = pd.DataFrame(data['top_agents'])
                
                # Clean up the dataframe
                agents_df['agent_name'] = agents_df['agent_id'].str.replace('agent_', '').str.title()
                
                # Top metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    best_agent = agents_df.loc[agents_df['resolution_rate'].idxmax()]
                    st.metric("🏆 Best Resolution Rate", 
                             f"{best_agent['agent_name']}", 
                             f"{best_agent['resolution_rate']:.1f}%")
                
                with col2:
                    most_active = agents_df.loc[agents_df['total_chats'].idxmax()]
                    st.metric("🎯 Most Active Agent", 
                             f"{most_active['agent_name']}", 
                             f"{most_active['total_chats']} chats")
                
                with col3:
                    avg_resolution = agents_df['resolution_rate'].mean()
                    st.metric("📊 Avg Resolution Rate", 
                             f"{avg_resolution:.1f}%")
                
                with col4:
                    total_resolved = agents_df['resolved_chats'].sum()
                    st.metric("✅ Total Resolved", 
                             f"{total_resolved} chats")
                
                # Visualizations
                col1, col2 = st.columns(2)
                
                with col1:
                    # Bar chart for conversations handled
                    fig_bar = px.bar(
                        agents_df.sort_values('total_chats', ascending=True),
                        x='total_chats',
                        y='agent_name',
                        orientation='h',
                        title="Conversations per Agent",
                        color='resolution_rate',
                        color_continuous_scale='Blues',
                        hover_data=['resolved_chats', 'resolution_rate']
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
                
                with col2:
                    # Donut chart for workload distribution
                    fig_pie = px.pie(
                        agents_df,
                        values='total_chats',
                        names='agent_name',
                        title="Workload Distribution",
                        hole=0.4
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                # Resolution rate comparison
                fig_resolution = px.bar(
                    agents_df.sort_values('resolution_rate', ascending=False),
                    x='agent_name',
                    y=['resolved_chats', 'total_chats'],
                    title="Resolution Performance Comparison",
                    barmode='group',
                    labels={'value': 'Number of Chats', 'variable': 'Chat Type'}
                )
                st.plotly_chart(fig_resolution, use_container_width=True)
                
                # Detailed Agent Table
                st.subheader("📋 Detailed Agent Metrics")
                
                # Prepare display dataframe
                display_df = agents_df[['agent_name', 'total_chats', 'resolved_chats', 'resolution_rate']].copy()
                display_df.columns = ['Agent', 'Total Chats', 'Resolved', 'Resolution Rate (%)']
                
                # Add performance indicators
                display_df['Performance'] = display_df['Resolution Rate (%)'].apply(
                    lambda x: '🟢 Excellent' if x >= 95 else ('🟡 Good' if x >= 85 else '🔴 Needs Improvement')
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
                
                # Agent Issues Breakdown
                st.subheader("🎯 Issues Handled by Agents")
                for agent in agents_df.head(5).itertuples():
                    with st.expander(f"{agent.agent_name} - Top Issues"):
                        if agent.top_issues and any(issue.get('issue') for issue in agent.top_issues):
                            for issue in agent.top_issues:
                                if issue.get('issue'):
                                    st.write(f"• {issue['issue']} ({issue.get('count', 0)} times)")
                        else:
                            st.write("No specific issues recorded")
                
            else:
                st.warning("No agent performance data available")
                
    except Exception as e:
        st.error(f"Error fetching agent performance data: {str(e)}")

with tab3:
    st.header("🎯 Issue Distribution")
    
    # Limit selector
    limit = st.slider("Number of issues to display", 5, 100, 10)
    
    try:
        response = requests.get(f"{api_base}/api/v1/analytics/issues/distribution?limit={limit}")
        if response.status_code == 200:
            data = response.json()
            
            if 'issues' in data and data['issues']:
                issues_df = pd.DataFrame(data['issues'])
                
                # Convert last_occurrence to datetime for better display
                issues_df['last_occurrence'] = pd.to_datetime(issues_df['last_occurrence'])
                issues_df['days_since'] = (pd.Timestamp.now(tz='UTC') - issues_df['last_occurrence']).dt.days
                
                # Calculate resolution rate for each issue
                issues_df['resolution_rate'] = (issues_df['resolved_count'] / issues_df['total_occurrences'] * 100).fillna(0)
                
                # Top level metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Issue Types", data.get('total', len(issues_df)))
                
                with col2:
                    total_occurrences = issues_df['total_occurrences'].sum()
                    st.metric("Total Occurrences", total_occurrences)
                
                with col3:
                    total_resolved = issues_df['resolved_count'].sum()
                    st.metric("Total Resolved", total_resolved)
                
                with col4:
                    overall_resolution = (total_resolved / total_occurrences * 100) if total_occurrences > 0 else 0
                    st.metric("Overall Resolution Rate", f"{overall_resolution:.1f}%")
                
                # Visualizations
                col1, col2 = st.columns(2)
                
                with col1:
                    # Pie chart of issue distribution by occurrences
                    fig_pie = px.pie(
                        issues_df,
                        values='total_occurrences',
                        names='issue_description',
                        title="Issue Distribution by Frequency"
                    )
                    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                with col2:
                    # Stacked bar chart - Resolved vs Unresolved
                    issues_df['unresolved_count'] = issues_df['total_occurrences'] - issues_df['resolved_count']
                    
                    # Take top issues by occurrence for cleaner visualization
                    top_issues = issues_df.nlargest(7, 'total_occurrences')
                    
                    fig_bar = go.Figure()
                    fig_bar.add_trace(go.Bar(
                        name='Resolved',
                        x=top_issues['issue_description'],
                        y=top_issues['resolved_count'],
                        marker_color='#4CAF50',
                        text=top_issues['resolved_count'],
                        textposition='auto',
                    ))
                    fig_bar.add_trace(go.Bar(
                        name='Unresolved',
                        x=top_issues['issue_description'],
                        y=top_issues['unresolved_count'],
                        marker_color='#f44336',
                        text=top_issues['unresolved_count'],
                        textposition='auto',
                    ))
                    
                    fig_bar.update_layout(
                        title="Resolution Status (Top Issues)",
                        barmode='stack',
                        xaxis_tickangle=-45,
                        xaxis_title="Issue",
                        yaxis_title="Count",
                        height=400,
                        showlegend=True
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
                
                # Resolution Rate Analysis
                st.subheader("📊 Resolution Rate Analysis")
                
                # Sort by resolution rate for visualization
                issues_sorted = issues_df.sort_values('resolution_rate', ascending=True)
                
                fig_resolution = px.bar(
                    issues_sorted,
                    x='resolution_rate',
                    y='issue_description',
                    orientation='h',
                    title="Resolution Success Rate by Issue",
                    color='resolution_rate',
                    color_continuous_scale=['#f44336', '#FFC107', '#4CAF50'],
                    range_color=[0, 100],
                    labels={
                        'resolution_rate': 'Resolution Rate (%)',
                        'issue_description': 'Issue Type'
                    },
                    text='resolution_rate'
                )
                fig_resolution.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                fig_resolution.update_layout(height=max(400, len(issues_df) * 40))
                st.plotly_chart(fig_resolution, use_container_width=True)
                
                # Issue Timeline
                st.subheader("📅 Issue Timeline")
                
                # Create timeline chart
                fig_timeline = px.scatter(
                    issues_df,
                    x='last_occurrence',
                    y='issue_description',
                    size='total_occurrences',
                    color='resolution_rate',
                    color_continuous_scale='RdYlGn',
                    range_color=[0, 100],
                    title="Issue Occurrence Timeline",
                    labels={
                        'last_occurrence': 'Last Occurred',
                        'issue_description': 'Issue',
                        'resolution_rate': 'Resolution %'
                    },
                    hover_data=['total_occurrences', 'resolved_count', 'days_since']
                )
                fig_timeline.update_layout(height=max(400, len(issues_df) * 35))
                st.plotly_chart(fig_timeline, use_container_width=True)
                
                # Detailed Issue Table
                st.subheader("📋 Detailed Issue Metrics")
                
                # Prepare display dataframe
                display_df = issues_df[['issue_description', 'total_occurrences', 'resolved_count', 'unresolved_count', 'resolution_rate', 'days_since']].copy()
                display_df.columns = ['Issue Description', 'Total', 'Resolved', 'Unresolved', 'Resolution %', 'Days Since']
                
                # Add priority indicator based on unresolved count and recency
                def get_priority(row):
                    if row['Unresolved'] == 0:
                        return '✅ Resolved'
                    elif row['Days Since'] < 7 and row['Unresolved'] > 0:
                        return '🔴 High Priority'
                    elif row['Days Since'] < 30 and row['Unresolved'] > 0:
                        return '🟡 Medium Priority'
                    else:
                        return '🟢 Low Priority'
                
                display_df['Priority'] = display_df.apply(get_priority, axis=1)
                
                # Sort by priority and unresolved count
                display_df = display_df.sort_values(['Unresolved', 'Days Since'], ascending=[False, True])
                
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Resolution %": st.column_config.ProgressColumn(
                            "Resolution %",
                            format="%.1f%%",
                            min_value=0,
                            max_value=100,
                        ),
                        "Total": st.column_config.NumberColumn(format="%d"),
                        "Resolved": st.column_config.NumberColumn(format="%d"),
                        "Unresolved": st.column_config.NumberColumn(format="%d"),
                        "Days Since": st.column_config.NumberColumn(format="%d days"),
                    }
                )
                
                # Key Insights
                unresolved_issues = issues_df[issues_df['unresolved_count'] > 0]
                recent_issues = issues_df[issues_df['days_since'] < 7]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.info(f"""
                    **🔍 Key Insights:**
                    - **Active Issues**: {len(unresolved_issues)} issue types with unresolved cases
                    - **Recent Activity**: {len(recent_issues)} issues occurred in the last 7 days
                    - **Most Frequent**: {issues_df.loc[issues_df['total_occurrences'].idxmax(), 'issue_description']} ({issues_df['total_occurrences'].max()} times)
                    - **Best Resolution**: {issues_df[issues_df['resolution_rate'] == 100]['issue_description'].iloc[0] if any(issues_df['resolution_rate'] == 100) else 'None with 100% resolution'}
                    """)
                
                with col2:
                    st.warning(f"""
                    **⚠️ Needs Attention:**
                    - **Zero Resolution**: {len(issues_df[issues_df['resolved_count'] == 0])} issues never resolved
                    - **High Volume Unresolved**: {issues_df.loc[issues_df['unresolved_count'].idxmax(), 'issue_description'] if issues_df['unresolved_count'].max() > 0 else 'None'}
                    - **Oldest Unresolved**: {issues_df[issues_df['unresolved_count'] > 0].nlargest(1, 'days_since')['issue_description'].iloc[0] if len(issues_df[issues_df['unresolved_count'] > 0]) > 0 else 'None'}
                    """)
                
            else:
                st.info("No issue data available")
                
    except Exception as e:
        st.error(f"Error fetching issue distribution: {str(e)}")
        st.info("Please check the API endpoint and try again.")

with tab4:
    st.header("⏱️ Resolution Time Analysis")
    
    try:
        response = requests.get(f"{api_base}/api/v1/analytics/resolution-time")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if data contains the expected structure
            if data and 'overall_stats' in data:
                overall = data['overall_stats']
                
                # Main metrics from API
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    avg_minutes = overall.get('avg_resolution_minutes', 0)
                    st.metric(
                        "Average Resolution Time",
                        f"{avg_minutes:.1f} min",
                        help="Average time to resolve conversations"
                    )
                
                with col2:
                    min_minutes = overall.get('min_resolution_minutes', 0)
                    st.metric(
                        "Fastest Resolution",
                        f"{min_minutes:.1f} min",
                        help="Minimum resolution time recorded"
                    )
                
                with col3:
                    max_minutes = overall.get('max_resolution_minutes', 0)
                    st.metric(
                        "Longest Resolution",
                        f"{max_minutes:.1f} min",
                        help="Maximum resolution time recorded"
                    )
                
                with col4:
                    total_resolved = overall.get('total_resolved_conversations', 0)
                    st.metric(
                        "Total Resolved",
                        total_resolved,
                        help="Total number of resolved conversations"
                    )
                
                # Additional metrics row
                col5, col6, col7 = st.columns(3)
                
                with col5:
                    # Convert average to hours for better readability
                    avg_hours = avg_minutes / 60
                    st.metric("Average (Hours)", f"{avg_hours:.2f} hrs")
                
                with col6:
                    # Show range
                    st.metric("Time Range", f"{min_minutes:.0f} - {max_minutes:.0f} min")
                
                with col7:
                    # Calculate spread
                    spread = max_minutes - min_minutes
                    st.metric("Time Spread", f"{spread:.0f} min")
                
                # Resolution Time by Issue Type
                if 'by_issue_type' in data and data['by_issue_type']:
                    st.subheader("📊 Resolution Time by Issue Type")
                    
                    issues_df = pd.DataFrame(data['by_issue_type'])
                    
                    # Sort by average resolution time for better visualization
                    issues_df = issues_df.sort_values('avg_resolution_minutes', ascending=True)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Bar chart of average resolution times
                        fig_bar = px.bar(
                            issues_df,
                            x='avg_resolution_minutes',
                            y='issue_description',
                            orientation='h',
                            title="Average Resolution Time by Issue",
                            color='avg_resolution_minutes',
                            color_continuous_scale='RdYlGn_r',  # Reversed so red is slow
                            labels={
                                'avg_resolution_minutes': 'Avg Time (minutes)',
                                'issue_description': 'Issue Type'
                            },
                            text='avg_resolution_minutes'
                        )
                        fig_bar.update_traces(texttemplate='%{text:.1f} min', textposition='outside')
                        fig_bar.update_layout(height=400)
                        st.plotly_chart(fig_bar, use_container_width=True)
                    
                    with col2:
                        # Show a different visualization - pie chart for time distribution
                        fig_pie = px.pie(
                            issues_df,
                            values='avg_resolution_minutes',
                            names='issue_description',
                            title="Time Distribution Across Issues",
                            color_discrete_sequence=px.colors.sequential.RdBu
                        )
                        fig_pie.update_traces(
                            textposition='inside',
                            textinfo='percent+label',
                            hovertemplate='<b>%{label}</b><br>' +
                                        'Time: %{value:.1f} minutes<br>' +
                                        'Percentage: %{percent}<br>' +
                                        '<extra></extra>'
                        )
                        fig_pie.update_layout(
                            height=400,
                            showlegend=False
                        )
                        st.plotly_chart(fig_pie, use_container_width=True)
                        
                        # Performance summary
                        excellent_count = len(issues_df[issues_df['avg_resolution_minutes'] <= 15])
                        good_count = len(issues_df[(issues_df['avg_resolution_minutes'] > 15) & (issues_df['avg_resolution_minutes'] <= 30)])
                        needs_improvement = len(issues_df[issues_df['avg_resolution_minutes'] > 45])
                        
                        st.info(f"""
                        **Performance Summary:**
                        - 🟢 Excellent (≤15 min): {excellent_count} issues
                        - 🟡 Good (15-30 min): {good_count} issues  
                        - 🔴 Needs Improvement (>45 min): {needs_improvement} issues
                        """)
                    
                    # Detailed table
                    st.subheader("📋 Detailed Resolution Time Metrics")
                    
                    display_df = issues_df.copy()
                    display_df['time_range'] = display_df['max_resolution_minutes'] - display_df['min_resolution_minutes']
                    
                    # Format for display
                    display_df = display_df[['issue_description', 'occurrences', 'avg_resolution_minutes', 
                                             'min_resolution_minutes', 'max_resolution_minutes', 'time_range']]
                    display_df.columns = ['Issue Type', 'Occurrences', 'Avg Time (min)', 
                                          'Min Time (min)', 'Max Time (min)', 'Range (min)']
                    
                    # Add performance indicator
                    def get_performance(avg_time):
                        if avg_time <= 15:
                            return '🟢 Excellent'
                        elif avg_time <= 30:
                            return '🟡 Good'
                        elif avg_time <= 45:
                            return '🟠 Average'
                        else:
                            return '🔴 Needs Improvement'
                    
                    display_df['Performance'] = display_df['Avg Time (min)'].apply(get_performance)
                    
                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Avg Time (min)": st.column_config.NumberColumn(format="%.1f"),
                            "Min Time (min)": st.column_config.NumberColumn(format="%.1f"),
                            "Max Time (min)": st.column_config.NumberColumn(format="%.1f"),
                            "Range (min)": st.column_config.NumberColumn(format="%.1f"),
                        }
                    )
                    
                    # Summary insights
                    fastest_issue = issues_df.loc[issues_df['avg_resolution_minutes'].idxmin()]
                    slowest_issue = issues_df.loc[issues_df['avg_resolution_minutes'].idxmax()]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.success(f"""
                        **⚡ Fastest Resolution:**
                        - **Issue**: {fastest_issue['issue_description']}
                        - **Average Time**: {fastest_issue['avg_resolution_minutes']:.1f} minutes
                        - **Occurrences**: {fastest_issue['occurrences']}
                        """)
                    
                    with col2:
                        st.warning(f"""
                        **⏰ Slowest Resolution:**
                        - **Issue**: {slowest_issue['issue_description']}
                        - **Average Time**: {slowest_issue['avg_resolution_minutes']:.1f} minutes
                        - **Occurrences**: {slowest_issue['occurrences']}
                        """)
                
            else:
                st.error("Unexpected data format from resolution-time API")
                st.json(data)  # Show raw data for debugging
                
        else:
            st.warning(f"API returned status code: {response.status_code}")
            st.info("Unable to fetch resolution time data. Please check the API endpoint.")
            
    except Exception as e:
        st.error(f"Error fetching resolution time data: {str(e)}")
        st.info("Please ensure the resolution-time API endpoint is accessible.")
        
with tab5:
    st.header("🚨 Human Escalation Analysis")
    
    try:
        response = requests.get(f"{api_base}/api/v1/analytics/escalation")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if data contains the expected structure
            if data and 'summary' in data:
                summary = data['summary']
                
                # Main metrics row
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "AI-Only Resolution", 
                        f"{summary['ai_only_resolution_rate_percent']:.1f}%",
                        delta=f"{summary['resolved_by_ai_only']} conversations",
                        help="Conversations resolved without human intervention"
                    )
                
                with col2:
                    st.metric(
                        "Escalation Rate", 
                        f"{summary['escalation_rate_percent']:.1f}%",
                        delta=f"{summary['escalated_to_human']} escalated",
                        delta_color="inverse",
                        help="Percentage requiring human assistance"
                    )
                
                with col3:
                    st.metric(
                        "Unresolved Rate", 
                        f"{summary['unresolved_rate_percent']:.1f}%",
                        delta=f"{summary['unresolved']} unresolved",
                        delta_color="inverse"
                    )
                
                with col4:
                    st.metric(
                        "Total Conversations", 
                        summary['total_conversations'],
                        help="Total conversations analyzed"
                    )
                
                # Human Effort Saved Section
                if 'human_effort_saved' in data:
                    st.subheader("💪 Human Effort Saved by AI")
                    effort = data['human_effort_saved']
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            "Handled by AI Only",
                            effort['conversations_handled_by_ai_only'],
                            help="No human intervention needed"
                        )
                    
                    with col2:
                        st.metric(
                            "Time Saved",
                            f"{effort['estimated_time_saved_hours']:.1f} hours",
                            delta=f"~{effort['estimated_time_saved_days']:.1f} workdays",
                            help=effort.get('assumption', '')
                        )
                    
                    with col3:
                        # Calculate efficiency percentage
                        efficiency = (effort['conversations_handled_by_ai_only'] / summary['total_conversations'] * 100)
                        st.metric(
                            "AI Efficiency",
                            f"{efficiency:.1f}%",
                            help="Percentage handled completely by AI"
                        )
                    
                    # Visual representation of effort saved
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Fixed gauge chart with better text positioning
                        fig_gauge = go.Figure(go.Indicator(
                            mode = "gauge+number",
                            value = summary['ai_only_resolution_rate_percent'],
                            domain = {'x': [0, 1], 'y': [0, 1]},
                            title = {'text': "AI Automation Success Rate", 'font': {'size': 16}},
                            number = {'suffix': "%", 'font': {'size': 40}},
                            gauge = {
                                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkgray"},
                                'bar': {'color': "darkgreen", 'thickness': 0.75},
                                'bgcolor': "white",
                                'borderwidth': 2,
                                'bordercolor': "gray",
                                'steps': [
                                    {'range': [0, 50], 'color': '#ffebee'},
                                    {'range': [50, 70], 'color': '#fff3e0'},
                                    {'range': [70, 85], 'color': '#f1f8e9'},
                                    {'range': [85, 100], 'color': '#c8e6c9'}
                                ],
                                'threshold': {
                                    'line': {'color': "red", 'width': 4},
                                    'thickness': 0.75,
                                    'value': 95
                                }
                            }
                        ))
                        fig_gauge.update_layout(
                            height=350,
                            margin=dict(l=20, r=20, t=40, b=20),
                            font={'color': "darkblue", 'family': "Arial"}
                        )
                        st.plotly_chart(fig_gauge, use_container_width=True)
                    
                    with col2:
                        # Pie chart of conversation distribution
                        fig_pie = go.Figure(data=[go.Pie(
                            labels=['AI Only', 'Human Escalation', 'Unresolved'],
                            values=[summary['resolved_by_ai_only'], 
                                   summary['escalated_to_human'], 
                                   summary['unresolved']],
                            hole=.4,
                            marker=dict(colors=['#4CAF50', '#FFC107', '#f44336'])
                        )])
                        fig_pie.update_layout(
                            title="Conversation Distribution",
                            height=300,
                            showlegend=True
                        )
                        st.plotly_chart(fig_pie, use_container_width=True)
                
                # Issue Resolution Analysis
                if 'by_issue_type' in data and data['by_issue_type']:
                    st.subheader("📊 Resolution Analysis by Issue Type")
                    
                    issues_df = pd.DataFrame(data['by_issue_type'])
                    
                    # Sort by resolution rate for better visualization
                    issues_df = issues_df.sort_values('resolution_rate_percent', ascending=True)
                    
                    # Create horizontal bar chart
                    fig_issues = px.bar(
                        issues_df,
                        x='resolution_rate_percent',
                        y='issue_description',
                        orientation='h',
                        title="Resolution Success Rate by Issue Type",
                        color='resolution_rate_percent',
                        color_continuous_scale=['#f44336', '#FFC107', '#4CAF50'],
                        range_color=[0, 100],
                        labels={
                            'resolution_rate_percent': 'Resolution Rate (%)',
                            'issue_description': 'Issue Type'
                        }
                    )
                    fig_issues.update_layout(height=400)
                    fig_issues.update_traces(
                        text=issues_df['resolution_rate_percent'].round(1).astype(str) + '%',
                        textposition='outside'
                    )
                    st.plotly_chart(fig_issues, use_container_width=True)
                    
                    # Detailed table
                    st.subheader("📋 Detailed Issue Resolution Metrics")
                    
                    display_df = issues_df[['issue_description', 'total_occurrences', 'resolved', 'unresolved', 'resolution_rate_percent']].copy()
                    display_df.columns = ['Issue Type', 'Total', 'Resolved', 'Unresolved', 'Resolution Rate (%)']
                    
                    # Add status indicator
                    display_df['Status'] = display_df['Resolution Rate (%)'].apply(
                        lambda x: '🟢 Excellent' if x >= 80 else ('🟡 Moderate' if x >= 50 else '🔴 Needs Attention')
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
                            "Total": st.column_config.NumberColumn(format="%d"),
                            "Resolved": st.column_config.NumberColumn(format="%d"),
                            "Unresolved": st.column_config.NumberColumn(format="%d"),
                        }
                    )
                    
                    # Summary insights
                    st.info(f"""
                    **📈 Key Insights:**
                    - **Best Performing Issue**: {issues_df.iloc[-1]['issue_description']} ({issues_df.iloc[-1]['resolution_rate_percent']:.1f}% resolution rate)
                    - **Needs Attention**: {issues_df.iloc[0]['issue_description']} ({issues_df.iloc[0]['resolution_rate_percent']:.1f}% resolution rate)
                    - **Most Common Issue**: {issues_df.loc[issues_df['total_occurrences'].idxmax(), 'issue_description']} ({issues_df['total_occurrences'].max()} occurrences)
                    """)
                
            else:
                st.error("Unexpected data format from escalation API")
                st.json(data)  # Show raw data for debugging
                
        else:
            st.warning(f"API returned status code: {response.status_code}")
            st.info("Unable to fetch escalation data. Please check the API endpoint.")
            
    except Exception as e:
        st.error(f"Error fetching escalation data: {str(e)}")
        st.info("Please ensure the escalation API endpoint is accessible.")