"""
Analytics Service - Provides metrics and statistics from Neo4j
"""
import structlog
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from core.database import Neo4jConnection
from models.schemas import IssueStats, AgentPerformance, MetricsSummary

logger = structlog.get_logger()


class AnalyticsService:
    def __init__(self, neo4j_conn: Neo4jConnection):
        self.db = neo4j_conn
    
    async def get_summary_metrics(self) -> MetricsSummary:
        """Get high-level summary metrics"""
        try:
            # Use simple separate counts instead of complex joins
            query = """
            CALL {
                MATCH (c:Conversation) RETURN count(c) as total_conversations
            }
            CALL {
                MATCH (i:Issue) RETURN count(i) as total_issues
            }
            CALL {
                MATCH (s:Solution) RETURN count(s) as total_solutions
            }
            CALL {
                MATCH (a:Agent) RETURN count(a) as total_agents
            }
            CALL {
                MATCH (cust:Customer) RETURN count(cust) as total_customers
            }
            CALL {
                MATCH (c:Conversation)
                WHERE c.created_at IS NOT NULL AND c.resolved_at IS NOT NULL
                WITH duration.inSeconds(c.created_at, c.resolved_at).minutes as minutes
                WHERE minutes IS NOT NULL
                RETURN avg(minutes) as avg_resolution_minutes
            }
            RETURN 
                total_conversations,
                total_issues,
                total_solutions,
                total_agents,
                total_customers,
                avg_resolution_minutes
            """
            
            results = await self.db.execute_query(query)
            
            if results:
                data = results[0]
                return MetricsSummary(
                    total_conversations=data.get('total_conversations', 0),
                    total_issues=data.get('total_issues', 0),
                    total_solutions=data.get('total_solutions', 0),
                    total_agents=data.get('total_agents', 0),
                    total_customers=data.get('total_customers', 0),
                    avg_resolution_time_minutes=data.get('avg_resolution_minutes'),
                    top_issues=[],
                    top_agents=[]
                )
            
            return MetricsSummary(
                total_conversations=0,
                total_issues=0,
                total_solutions=0,
                total_agents=0,
                total_customers=0
            )
            
        except Exception as e:
            logger.error("Failed to get summary metrics", error=str(e))
            raise
    
    async def get_issue_distribution(self, limit: int = 10) -> List[IssueStats]:
        """Get top issues by occurrence"""
        try:
            query = """
            MATCH (c:Conversation)-[:CONTAINS_ISSUE]->(i:Issue)
            WITH i, count(c) as occurrences, 
                 collect(c) as conversations
            WITH i, occurrences, conversations,
                 [conv IN conversations WHERE conv.resolved_at IS NOT NULL] as resolved_convs,
                 [conv IN conversations | conv.created_at] as created_dates
            RETURN 
                i.id as issue_id,
                i.one_liner as issue_description,
                occurrences as total_occurrences,
                size(resolved_convs) as resolved_count,
                reduce(latest = created_dates[0], date IN created_dates | 
                    CASE WHEN date > latest THEN date ELSE latest END) as last_occurrence
            ORDER BY occurrences DESC
            LIMIT $limit
            """
            
            results = await self.db.execute_query(query, {"limit": limit})
            
            issue_stats = []
            for record in results:
                # Convert Neo4j DateTime to Python datetime
                last_occ = record.get('last_occurrence')
                if last_occ and hasattr(last_occ, 'to_native'):
                    last_occ = last_occ.to_native()
                
                issue_stats.append(IssueStats(
                    issue_id=record['issue_id'],
                    issue_description=record['issue_description'],
                    total_occurrences=record['total_occurrences'],
                    resolved_count=record['resolved_count'],
                    last_occurrence=last_occ
                ))
            
            return issue_stats
            
        except Exception as e:
            logger.error("Failed to get issue distribution", error=str(e))
            raise
    
    async def get_customers_list(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get list of customers with their conversation counts"""
        try:
            query = """
            MATCH (c:Conversation)-[:BELONGS_TO]->(cust:Customer)
            WITH cust, count(c) as total_conversations,
                 sum(CASE WHEN c.resolved_at IS NOT NULL THEN 1 ELSE 0 END) as resolved_conversations
            RETURN 
                cust.id as customer_id,
                total_conversations,
                resolved_conversations
            ORDER BY total_conversations DESC
            LIMIT $limit
            """
            
            results = await self.db.execute_query(query, {"limit": limit})
            
            return [
                {
                    "customer_id": r['customer_id'],
                    "total_conversations": r['total_conversations'],
                    "resolved_conversations": r['resolved_conversations']
                }
                for r in results
            ]
            
        except Exception as e:
            logger.error("Failed to get customers list", error=str(e))
            raise
    
    async def get_customer_issue_history(self, customer_id: str) -> Dict[str, Any]:
        """Get all issues a specific customer has encountered"""
        try:
            query = """
            MATCH (c:Conversation)-[:BELONGS_TO]->(cust:Customer {id: $customer_id})
            MATCH (c)-[:CONTAINS_ISSUE]->(i:Issue)
            OPTIONAL MATCH (c)-[:HANDLED_BY]->(a:Agent)
            RETURN 
                i.id as issue_id,
                i.one_liner as issue_description,
                c.id as conversation_id,
                c.created_at as occurred_at,
                c.resolved_at as resolved_at,
                a.id as handled_by_agent
            ORDER BY c.created_at DESC
            """
            
            results = await self.db.execute_query(query, {"customer_id": customer_id})
            
            issues = []
            for r in results:
                occurred = r.get('occurred_at')
                if occurred and hasattr(occurred, 'to_native'):
                    occurred = occurred.to_native()
                
                resolved = r.get('resolved_at')
                if resolved and hasattr(resolved, 'to_native'):
                    resolved = resolved.to_native()
                
                issues.append({
                    "issue_id": r['issue_id'],
                    "issue_description": r['issue_description'],
                    "conversation_id": r['conversation_id'],
                    "occurred_at": occurred,
                    "resolved_at": resolved,
                    "handled_by_agent": r.get('handled_by_agent'),
                    "status": "resolved" if resolved else "open"
                })
            
            return {
                "customer_id": customer_id,
                "total_issues": len(issues),
                "issues": issues
            }
            
        except Exception as e:
            logger.error("Failed to get customer issue history", error=str(e), customer_id=customer_id)
            raise
    
    async def get_resolution_time_stats(self) -> Dict[str, Any]:
        """Get resolution time statistics by issue type"""
        try:
            query = """
            MATCH (c:Conversation)-[:CONTAINS_ISSUE]->(i:Issue)
            WHERE c.created_at IS NOT NULL AND c.resolved_at IS NOT NULL
            WITH i, c,
                 duration.inSeconds(c.created_at, c.resolved_at).minutes as resolution_minutes
            WHERE resolution_minutes IS NOT NULL
            WITH i.one_liner as issue_description,
                 count(c) as occurrences,
                 avg(resolution_minutes) as avg_minutes,
                 min(resolution_minutes) as min_minutes,
                 max(resolution_minutes) as max_minutes
            RETURN 
                issue_description,
                occurrences,
                round(avg_minutes, 2) as avg_resolution_minutes,
                round(min_minutes, 2) as min_resolution_minutes,
                round(max_minutes, 2) as max_resolution_minutes
            ORDER BY avg_minutes DESC
            """
            
            results = await self.db.execute_query(query)
            
            stats = []
            for r in results:
                stats.append({
                    "issue_description": r['issue_description'],
                    "occurrences": r['occurrences'],
                    "avg_resolution_minutes": r['avg_resolution_minutes'],
                    "min_resolution_minutes": r['min_resolution_minutes'],
                    "max_resolution_minutes": r['max_resolution_minutes']
                })
            
            # Calculate overall stats
            overall_query = """
            MATCH (c:Conversation)
            WHERE c.created_at IS NOT NULL AND c.resolved_at IS NOT NULL
            WITH duration.inSeconds(c.created_at, c.resolved_at).minutes as resolution_minutes
            WHERE resolution_minutes IS NOT NULL
            RETURN 
                count(*) as total_resolved,
                round(avg(resolution_minutes), 2) as overall_avg_minutes,
                round(min(resolution_minutes), 2) as overall_min_minutes,
                round(max(resolution_minutes), 2) as overall_max_minutes
            """
            
            overall_results = await self.db.execute_query(overall_query)
            overall = overall_results[0] if overall_results else {}
            
            return {
                "overall_stats": {
                    "total_resolved_conversations": overall.get('total_resolved', 0),
                    "avg_resolution_minutes": overall.get('overall_avg_minutes', 0),
                    "min_resolution_minutes": overall.get('overall_min_minutes', 0),
                    "max_resolution_minutes": overall.get('overall_max_minutes', 0)
                },
                "by_issue_type": stats
            }
            
        except Exception as e:
            logger.error("Failed to get resolution time stats", error=str(e))
            raise
    
    async def get_escalation_analytics(self) -> Dict[str, Any]:
        """Get analytics on human escalation vs AI resolution"""
        try:
            # Overall escalation stats
            # Since escalated_to_human field doesn't exist, we assume:
            # - Conversations with agent_id are handled by AI agents
            # - Conversations without agent_id or with resolved_at = null might need human intervention
            overall_query = """
            MATCH (c:Conversation)
            WITH count(c) as total_conversations,
                 sum(CASE WHEN c.resolved_at IS NOT NULL THEN 1 ELSE 0 END) as resolved_conversations,
                 sum(CASE WHEN c.agent_id IS NOT NULL AND c.resolved_at IS NOT NULL THEN 1 ELSE 0 END) as ai_resolved_conversations,
                 sum(CASE WHEN c.resolved_at IS NULL THEN 1 ELSE 0 END) as unresolved_conversations
            RETURN 
                total_conversations,
                resolved_conversations,
                ai_resolved_conversations,
                unresolved_conversations,
                round(toFloat(ai_resolved_conversations) / total_conversations * 100, 2) as ai_resolution_rate,
                round(toFloat(unresolved_conversations) / total_conversations * 100, 2) as unresolved_rate
            """
            
            overall_results = await self.db.execute_query(overall_query)
            overall = overall_results[0] if overall_results else {}
            
            # Resolution by issue type
            by_issue_query = """
            MATCH (c:Conversation)-[:CONTAINS_ISSUE]->(i:Issue)
            WITH i.one_liner as issue_description,
                 count(c) as total_occurrences,
                 sum(CASE WHEN c.resolved_at IS NOT NULL THEN 1 ELSE 0 END) as resolved_count,
                 sum(CASE WHEN c.resolved_at IS NULL THEN 1 ELSE 0 END) as unresolved_count
            RETURN 
                issue_description,
                total_occurrences,
                resolved_count,
                unresolved_count,
                round(toFloat(resolved_count) / total_occurrences * 100, 2) as resolution_rate
            ORDER BY total_occurrences DESC
            LIMIT 10
            """
            
            by_issue_results = await self.db.execute_query(by_issue_query)
            
            by_issue = []
            for r in by_issue_results:
                by_issue.append({
                    "issue_description": r['issue_description'],
                    "total_occurrences": r['total_occurrences'],
                    "resolved": r['resolved_count'],
                    "unresolved": r['unresolved_count'],
                    "resolution_rate_percent": r['resolution_rate']
                })
            
            # Calculate human effort saved
            total_convs = overall.get('total_conversations', 0)
            ai_resolved = overall.get('ai_resolved_conversations', 0)
            
            # Assume average human handling time is 15 minutes per conversation
            avg_human_time_minutes = 15
            time_saved_minutes = ai_resolved * avg_human_time_minutes
            time_saved_hours = round(time_saved_minutes / 60, 2)
            
            return {
                "summary": {
                    "total_conversations": total_convs,
                    "resolved_by_ai_agents": ai_resolved,
                    "unresolved": overall.get('unresolved_conversations', 0),
                    "ai_resolution_rate_percent": overall.get('ai_resolution_rate', 0),
                    "unresolved_rate_percent": overall.get('unresolved_rate', 0)
                },
                "human_effort_saved": {
                    "conversations_handled_by_ai": ai_resolved,
                    "estimated_time_saved_hours": time_saved_hours,
                    "estimated_time_saved_days": round(time_saved_hours / 8, 2),
                    "assumption": f"Based on {avg_human_time_minutes} minutes average human handling time per conversation"
                },
                "by_issue_type": by_issue
            }
            
        except Exception as e:
            logger.error("Failed to get escalation analytics", error=str(e))
            raise
    
    async def get_agent_performance(self, limit: int = 10) -> List[AgentPerformance]:
        """Get agent performance metrics"""
        try:
            query = """
            MATCH (a:Agent)<-[:HANDLED_BY]-(c:Conversation)
            WITH a, count(c) as total_chats,
                 collect(c) as conversations
            WITH a, total_chats, conversations,
                 [conv IN conversations WHERE conv.resolved_at IS NOT NULL] as resolved_convs
            OPTIONAL MATCH (a)<-[:HANDLED_BY]-(c2:Conversation)-[:CONTAINS_ISSUE]->(i:Issue)
            WITH a, total_chats, resolved_convs,
                 i.one_liner as issue_desc, count(c2) as issue_count
            ORDER BY issue_count DESC
            WITH a, total_chats, size(resolved_convs) as resolved_count,
                 collect({issue: issue_desc, count: issue_count})[..3] as top_issues
            RETURN 
                a.id as agent_id,
                total_chats,
                resolved_count,
                top_issues
            ORDER BY total_chats DESC
            LIMIT $limit
            """
            
            results = await self.db.execute_query(query, {"limit": limit})
            
            agent_performances = []
            for record in results:
                total = record['total_chats']
                resolved = record['resolved_count']
                resolution_rate = (resolved / total * 100) if total > 0 else 0.0
                
                agent_performances.append(AgentPerformance(
                    agent_id=record['agent_id'],
                    total_chats=total,
                    resolved_chats=resolved,
                    resolution_rate=round(resolution_rate, 2),
                    top_issues=record.get('top_issues', [])
                ))
            
            return agent_performances
            
        except Exception as e:
            logger.error("Failed to get agent performance", error=str(e))
            raise
    

