from typing import List, Dict, Any, Optional
import structlog
from core.database import Neo4jConnection
from core.llm_service import GeminiService
from core.config import settings

logger = structlog.get_logger()


class RetrievalService:
    def __init__(self, neo4j_conn: Neo4jConnection):
        self.neo4j = neo4j_conn
        self.llm_service = GeminiService()

    async def retrieve_and_respond(
        self, query: str, customer_id: str, context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Main retrieval and response generation pipeline"""

        # 0. Check for greetings/simple chat (Bypass DB)
        simple_response = await self.llm_service.check_general_chat(query)
        if simple_response:
            return {
                "response": simple_response,
                "confidence": 1.0,
                "source_ids": [],
                "escalate_to_human": False,
                "reasoning": "Simple greeting/chit-chat",
            }

        # 1. Generate query embedding
        query_embedding = await self.llm_service.generate_embedding(query)

        # 2. Retrieve candidate issues and solutions
        candidates = await self._retrieve_candidates(query_embedding, customer_id)

        # 3. Rank and filter candidates
        ranked_candidates = await self._rank_candidates(candidates, query)

        # 4. Generate response using LLM
        if ranked_candidates:
            response_data = await self.llm_service.synthesize_response(
                query, ranked_candidates[:5], context
            )
            # Escalation logic handled by agent:
            # If confidence is low (< 0.55), set escalate_to_human = True
            try:
                confidence = float(response_data.get("confidence", 0.0))
            except (ValueError, TypeError):
                confidence = 0.0

            should_escalate = confidence < 0.55
            logger.info(
                f"Escalation check: Confidence={confidence}, Threshold=0.55, Escalate={should_escalate}"
            )

            response_data["escalate_to_human"] = should_escalate

            if response_data["escalate_to_human"]:
                response_data["response"] += (
                    "\n\n(Note: I am not fully confident in this answer, so I am connecting you with a human agent for further assistance.)"
                )
        else:
            response_data = {
                "response": "I don't have enough information to answer your question. Let me connect you with a human agent.",
                "confidence": 0.0,
                "source_ids": [],
                "escalate_to_human": True,
                "reasoning": "No relevant knowledge found in database",
            }

        # 5. Add source references
        response_data["sources"] = await self._build_source_references(
            ranked_candidates[:5], response_data.get("source_ids", [])
        )

        return response_data

    async def _retrieve_candidates(
        self, query_embedding: List[float], customer_id: str
    ) -> List[Dict]:
        """Retrieve candidate issues and solutions using vector similarity"""

        logger.info(
            f"Retrieving candidates for query embedding of length {len(query_embedding)}"
        )

        # Search for similar issues
        issue_query = """
        CALL db.index.vector.queryNodes('issue_embeddings', $k, $embedding)
        YIELD node as i, score
        MATCH (c:Conversation)-[:CONTAINS_ISSUE]->(i)
        OPTIONAL MATCH (c)-[:CONTAINS_SOLUTION]->(s:Solution)
        RETURN 
            i.id as issue_id,
            i.canonical_description as issue_description,
            i.one_liner as issue_summary,
            i.tags as tags,
            i.quality_score as issue_quality,
            i.human_reviewed as issue_reviewed,
            score as similarity_score,
            c.id as conversation_id,
            collect(DISTINCT {
                id: s.id,
                description: s.canonical_description,
                one_liner: s.one_liner,
                steps: s.steps,
                confidence: s.confidence,
                quality_score: s.quality_score,
                human_reviewed: s.human_reviewed
            }) as solutions
        ORDER BY score DESC
        LIMIT $limit
        """

        try:
            issue_results = await self.neo4j.execute_query(
                issue_query,
                {
                    "embedding": query_embedding,
                    "k": settings.max_retrieval_results,
                    "limit": settings.max_retrieval_results,
                },
            )
            logger.info(f"Issue search returned {len(issue_results)} results")
        except Exception as e:
            logger.error(f"Issue search failed: {e}")
            issue_results = []

        # Search for similar solutions directly
        solution_query = """
        CALL db.index.vector.queryNodes('solution_embeddings', $k, $embedding)
        YIELD node as s, score
        MATCH (c:Conversation)-[:CONTAINS_SOLUTION]->(s)
        OPTIONAL MATCH (c)-[:CONTAINS_ISSUE]->(i:Issue)
        RETURN 
            s.id as solution_id,
            s.canonical_description as solution_description,
            s.one_liner as solution_summary,
            s.steps as steps,
            s.confidence as solution_confidence,
            s.quality_score as solution_quality,
            s.human_reviewed as solution_reviewed,
            score as similarity_score,
            c.id as conversation_id,
            i.canonical_description as related_issue
        ORDER BY score DESC
        LIMIT $limit
        """

        solution_results = await self.neo4j.execute_query(
            solution_query,
            {
                "embedding": query_embedding,
                "k": settings.max_retrieval_results,
                "limit": settings.max_retrieval_results,
            },
        )

        # Combine and format results
        candidates = []

        # Process issue results
        for result in issue_results:
            for solution in result.get("solutions", []):
                if solution.get("id"):  # Only include if solution exists
                    candidates.append(
                        {
                            "type": "issue_solution_pair",
                            "issue_id": result["issue_id"],
                            "solution_id": solution["id"],
                            "issue": result["issue_description"],
                            "solution": solution["description"],
                            "steps": solution.get("steps", []),
                            "similarity_score": result["similarity_score"],
                            "quality_score": (
                                result["issue_quality"] + solution["quality_score"]
                            )
                            / 2,
                            "human_reviewed": result["issue_reviewed"]
                            and solution["human_reviewed"],
                            "conversation_id": result["conversation_id"],
                            "source_id": f"{result['issue_id']}_{solution['id']}",
                        }
                    )

        # Process direct solution results
        for result in solution_results:
            candidates.append(
                {
                    "type": "direct_solution",
                    "solution_id": result["solution_id"],
                    "issue": result.get("related_issue", "Related issue"),
                    "solution": result["solution_description"],
                    "steps": result.get("steps", []),
                    "similarity_score": result["similarity_score"],
                    "quality_score": result["solution_quality"],
                    "human_reviewed": result["solution_reviewed"],
                    "conversation_id": result["conversation_id"],
                    "source_id": result["solution_id"],
                }
            )

        return candidates

    async def _rank_candidates(self, candidates: List[Dict], query: str) -> List[Dict]:
        """Rank candidates using composite scoring"""

        for candidate in candidates:
            # Composite score: similarity + quality + human review bonus + recency
            base_score = candidate["similarity_score"] * 0.7
            quality_score = candidate["quality_score"] * 0.1
            human_bonus = 0.1 if candidate["human_reviewed"] else 0.0

            # Simple recency bonus (would need timestamps for proper implementation)
            recency_bonus = 0.1

            candidate["composite_score"] = (
                base_score + quality_score + human_bonus + recency_bonus
            )

        # Sort by composite score
        candidates.sort(key=lambda x: x["composite_score"], reverse=True)

        top_candidates = [
            f"{c.get('source_id')}: {c.get('composite_score'):.3f}"
            for c in candidates[:3]
        ]
        logger.info(f"Top 3 candidates before filtering: {top_candidates}")

        # Filter by minimum confidence threshold
        filtered_candidates = [
            c
            for c in candidates
            if c["composite_score"] >= settings.confidence_threshold
        ]

        logger.info(
            f"Candidates after filtering (threshold={settings.confidence_threshold}): {len(filtered_candidates)}"
        )

        return filtered_candidates

    async def _build_source_references(
        self, candidates: List[Dict], source_ids: List[str]
    ) -> List[Dict]:
        """Build source references for response"""
        sources = []

        for candidate in candidates:
            if candidate["source_id"] in source_ids:
                # Get conversation snippet
                snippet_query = """
                MATCH (c:Conversation {id: $conversation_id})
                RETURN c.raw_text as text
                LIMIT 1
                """

                snippet_result = await self.neo4j.execute_query(
                    snippet_query, {"conversation_id": candidate["conversation_id"]}
                )

                snippet = ""
                if snippet_result:
                    full_text = snippet_result[0].get("text", "")
                    # Extract relevant snippet (simplified)
                    snippet = (
                        full_text[:200] + "..." if len(full_text) > 200 else full_text
                    )

                sources.append(
                    {
                        "source_id": candidate["source_id"],
                        "conversation_id": candidate["conversation_id"],
                        "snippet": snippet,
                        "relevance_score": candidate["similarity_score"],
                    }
                )

        return sources
