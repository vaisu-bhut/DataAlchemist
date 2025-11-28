import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Analytics Dashboard", page_icon="📊", layout="wide")

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
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Conversations",
                    data.get('total_conversations', 0),
                    delta=data.get('conversations_change', 0)
                )
            
            with col2:
                st.metric(
                    "Unique Customers",
                    data.get('unique_customers', 0),
                    delta=data.get('customers_change', 0)
                )
            
            with col3:
                st.metric(
                    "Resolution Rate",
                    f"{data.get('resolution_rate', 0):.1f}%",
                    delta=f"{data.get('resolution_change', 0):.1f}%"
                )
            
            with col4:
                st.metric(
                    "Satisfaction Score",
                    f"{data.get('satisfaction_score', 0):.2f}/5",
                    delta=f"{data.get('satisfaction_change', 0):.2f}"
                )
            
            # Trend chart
            if 'daily_stats' in data:
                df_trend = pd.DataFrame(data['daily_stats'])
                fig = px.line(df_trend, x='date', y=['conversations', 'resolutions'],
                            title="Daily Conversation Trends")
                st.plotly_chart(fig, use_container_width=True)
                
    except Exception as e:
        st.error(f"Error fetching summary data: {str(e)}")

with tab2:
    st.header("👥 Agent Performance")
    
    try:
        response = requests.get(f"{api_base}/api/v1/analytics/agents/performance")
        if response.status_code == 200:
            data = response.json()
            
            if 'agents' in data:
                df_agents = pd.DataFrame(data['agents'])
                
                # Performance metrics
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_bar = px.bar(df_agents, x='agent_name', y='conversations_handled',
                                    title="Conversations per Agent")
                    st.plotly_chart(fig_bar, use_container_width=True)
                
                with col2:
                    fig_scatter = px.scatter(df_agents, x='avg_resolution_time', y='satisfaction_score',
                                           size='conversations_handled', hover_data=['agent_name'],
                                           title="Performance Matrix")
                    st.plotly_chart(fig_scatter, use_container_width=True)
                
                # Detailed table
                st.subheader("Detailed Agent Metrics")
                st.dataframe(df_agents, use_container_width=True)
                
    except Exception as e:
        st.error(f"Error fetching agent performance data: {str(e)}")

with tab3:
    st.header("🎯 Issue Distribution")
    
    # Limit selector
    limit = st.slider("Number of top issues to display", 5, 20, 10)
    
    try:
        response = requests.get(f"{api_base}/api/v1/analytics/issues/distribution?limit={limit}")
        if response.status_code == 200:
            data = response.json()
            
            if 'issues' in data:
                df_issues = pd.DataFrame(data['issues'])
                
                # Pie chart
                fig_pie = px.pie(df_issues, values='count', names='issue_type',
                               title=f"Top {limit} Issue Types")
                st.plotly_chart(fig_pie, use_container_width=True)
                
                # Bar chart with resolution rates
                fig_bar = go.Figure(data=[
                    go.Bar(name='Total Issues', x=df_issues['issue_type'], y=df_issues['count']),
                    go.Bar(name='Resolved', x=df_issues['issue_type'], y=df_issues.get('resolved_count', 0))
                ])
                fig_bar.update_layout(barmode='group', title="Issues vs Resolutions")
                st.plotly_chart(fig_bar, use_container_width=True)
                
    except Exception as e:
        st.error(f"Error fetching issue distribution: {str(e)}")

with tab4:
    st.header("⏱️ Resolution Time Analysis")
    
    try:
        response = requests.get(f"{api_base}/api/v1/analytics/resolution-time")
        if response.status_code == 200:
            data = response.json()
            
            # Average resolution time by category
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Overall Avg", f"{data.get('overall_avg', 0):.1f} hours")
            
            with col2:
                st.metric("Median Time", f"{data.get('median_time', 0):.1f} hours")
            
            with col3:
                st.metric("90th Percentile", f"{data.get('p90_time', 0):.1f} hours")
            
            # Distribution histogram
            if 'distribution' in data:
                df_dist = pd.DataFrame(data['distribution'])
                fig_hist = px.histogram(df_dist, x='resolution_time', 
                                       title="Resolution Time Distribution")
                st.plotly_chart(fig_hist, use_container_width=True)
            
            # By issue type
            if 'by_issue_type' in data:
                df_by_type = pd.DataFrame(data['by_issue_type'])
                fig_bar = px.bar(df_by_type, x='issue_type', y='avg_resolution_time',
                               title="Average Resolution Time by Issue Type")
                st.plotly_chart(fig_bar, use_container_width=True)
                
    except Exception as e:
        st.error(f"Error fetching resolution time data: {str(e)}")

with tab5:
    st.header("🚨 Human Escalation Analysis")
    
    try:
        response = requests.get(f"{api_base}/api/v1/analytics/escalation")
        if response.status_code == 200:
            data = response.json()
            
            # Escalation metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Escalation Rate", f"{data.get('escalation_rate', 0):.1f}%")
            
            with col2:
                st.metric("Total Escalations", data.get('total_escalations', 0))
            
            with col3:
                st.metric("Avg Time to Escalate", f"{data.get('avg_time_to_escalate', 0):.1f}h")
            
            with col4:
                st.metric("Resolution After Escalation", f"{data.get('resolution_after_escalation', 0):.1f}%")
            
            # Escalation reasons
            if 'escalation_reasons' in data:
                df_reasons = pd.DataFrame(data['escalation_reasons'])
                fig_pie = px.pie(df_reasons, values='count', names='reason',
                               title="Escalation Reasons")
                st.plotly_chart(fig_pie, use_container_width=True)
            
            # Trend over time
            if 'daily_escalations' in data:
                df_trend = pd.DataFrame(data['daily_escalations'])
                fig_line = px.line(df_trend, x='date', y='escalations',
                                 title="Daily Escalation Trend")
                st.plotly_chart(fig_line, use_container_width=True)
                
    except Exception as e:
        st.error(f"Error fetching escalation data: {str(e)}")