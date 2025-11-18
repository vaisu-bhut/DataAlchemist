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
    
    async def get_agent_specialization(self, agent_id: str) -> Dict[str, Any]:
        """Get what issues a specific agent handles most"""
        try:
            query = """
            MATCH (a:Agent {id: $agent_id})<-[:HANDLED_BY]-(c:Conversation)-[:CONTAINS_ISSUE]->(i:Issue)
            WITH i, count(c) as handled_count,
                 sum(CASE WHEN c.resolved_at IS NOT NULL THEN 1 ELSE 0 END) as resolved_count
            RETURN 
                i.id as issue_id,
                i.one_liner as issue_description,
                handled_count,
                resolved_count,
                toFloat(resolved_count) / handled_count * 100 as success_rate
            ORDER BY handled_count DESC
            LIMIT 10
            """
            
            results = await self.db.execute_query(query, {"agent_id": agent_id})
            
            return {
                "agent_id": agent_id,
                "specializations": [
                    {
                        "issue_id": r['issue_id'],
                        "issue_description": r['issue_description'],
                        "handled_count": r['handled_count'],
                        "resolved_count": r['resolved_count'],
                        "success_rate": round(r['success_rate'], 2)
                    }
                    for r in results
                ]
            }
            
        except Exception as e:
            logger.error("Failed to get agent specialization", error=str(e), agent_id=agent_id)
            raise
    
    async def get_trending_issues(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get issues trending in the last N days"""
        try:
            query = """
            MATCH (c:Conversation)-[:CONTAINS_ISSUE]->(i:Issue)
            WHERE c.created_at >= datetime() - duration({days: $days})
            WITH i, count(c) as recent_count,
                 max(c.created_at) as last_seen
            RETURN 
                i.id as issue_id,
                i.one_liner as issue_description,
                recent_count,
                last_seen
            ORDER BY recent_count DESC
            LIMIT 10
            """
            
            results = await self.db.execute_query(query, {"days": days})
            
            return [
                {
                    "issue_id": r['issue_id'],
                    "issue_description": r['issue_description'],
                    "count_last_n_days": r['recent_count'],
                    "last_seen": r['last_seen'],
                    "days": days
                }
                for r in results
            ]
            
        except Exception as e:
            logger.error("Failed to get trending issues", error=str(e))
            raise
