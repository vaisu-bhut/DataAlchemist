import uuid
from datetime import datetime
from typing import List, Dict, Any
import structlog
from core.database import Neo4jConnection
from core.llm_service import GeminiService
from services.pii_redactor import PIIRedactor
from models.schemas import ConversationData, IngestResponse

logger = structlog.get_logger()

class IngestionService:
    def __init__(self, neo4j_conn: Neo4jConnection):
        self.neo4j = neo4j_conn
        self.llm_service = GeminiService()
        self.pii_redactor = PIIRedactor()
    
    async def process_conversations(self, conversations: List[ConversationData], batch_id: str = None) -> IngestResponse:
        """Process and ingest conversations"""
        processed_count = 0
        failed_count = 0
        errors = []
        
        if not batch_id:
            batch_id = str(uuid.uuid4())
        
        for conversation in conversations:
            try:
                await self._process_single_conversation(conversation, batch_id)
                processed_count += 1
                logger.info(f"Processed conversation {conversation.conversation_id}")
            except Exception as e:
                failed_count += 1
                error_msg = f"Failed to process conversation {conversation.conversation_id}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        return IngestResponse(
            success=failed_count == 0,
            processed_count=processed_count,
            failed_count=failed_count,
            batch_id=batch_id,
            errors=errors
        )
    
    async def _process_single_conversation(self, conversation: ConversationData, batch_id: str):
        """Process a single conversation"""
        logger.info(f"Starting processing of conversation {conversation.conversation_id}")
        
        # 1. Redact PII
        conversation_dict = conversation.model_dump()
        redacted_conversation = self.pii_redactor.redact_conversation(conversation_dict)
        logger.info(f"PII redaction completed for {conversation.conversation_id}")
        
        # 2. Create conversation text
        conversation_text = self._create_conversation_text(redacted_conversation['messages'])
        logger.info(f"Conversation text created, length: {len(conversation_text)}")
        
        # 3. Chunk if necessary (simplified - just use full text for now)
        chunks = [conversation_text] if len(conversation_text) < 4000 else self._chunk_text(conversation_text)
        logger.info(f"Text chunking completed, {len(chunks)} chunks")
        
        # 4. Extract canonical data using LLM
        try:
            canonical_data = await self.llm_service.extract_canonical_data(conversation_text)
            logger.info(f"LLM extraction completed: {len(canonical_data.get('issues', []))} issues, {len(canonical_data.get('solutions', []))} solutions")
            logger.info(f"Canonical data: {canonical_data}")
        except Exception as e:
            logger.error(f"LLM extraction failed for {conversation.conversation_id}: {e}")
            # Create minimal canonical data to continue processing
            canonical_data = {
                'issues': [],
                'solutions': [],
                'conversation_summary': 'Processing failed - stored conversation only'
            }
        
        # 5. Generate embeddings and store in Neo4j
        await self._store_conversation_data(conversation, canonical_data, batch_id, conversation_text)
        logger.info(f"Data storage completed for {conversation.conversation_id}")
    
    def _create_conversation_text(self, messages: List[Dict]) -> str:
        """Convert messages to readable conversation text"""
        text_parts = []
        for msg in messages:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            text_parts.append(f"{role.title()}: {content}")
        return "\n\n".join(text_parts)
    
    def _chunk_text(self, text: str, chunk_size: int = 2000) -> List[str]:
        """Simple text chunking"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) > chunk_size and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
            else:
                current_chunk.append(word)
                current_length += len(word) + 1
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
    
    async def _store_conversation_data(self, conversation: ConversationData, canonical_data: Dict, batch_id: str, conversation_text: str):
        """Store processed data in Neo4j"""
        timestamp = datetime.utcnow()
        
        # Use a single transaction to create everything atomically
        async with self.neo4j.driver.session(database="neo4j") as session:
            # Single query that creates Customer, Agent, Conversation and all relationships
            query = """
            // Create Customer node
            MERGE (cust:Customer {id: $customer_id})
            
            // Create Agent node if agent_id provided
            WITH cust
            CALL {
                WITH cust
                WITH cust, $agent_id as aid
                WHERE aid IS NOT NULL
                MERGE (agent:Agent {id: aid})
                RETURN agent
            }
            
            // Create Conversation node
            WITH cust
            MERGE (conv:Conversation {id: $conversation_id})
            SET conv.customer_id = $customer_id,
                conv.agent_id = $agent_id,
                conv.raw_text = $raw_text,
                conv.summary = $summary,
                conv.batch_id = $batch_id,
                conv.created_at = CASE WHEN $created_at IS NOT NULL THEN datetime($created_at) ELSE datetime($timestamp) END,
                conv.resolved_at = CASE WHEN $resolved_at IS NOT NULL THEN datetime($resolved_at) ELSE null END,
                conv.updated_at = datetime($timestamp)
            
            // Create BELONGS_TO relationship
            MERGE (conv)-[:BELONGS_TO]->(cust)
            
            // Create HANDLED_BY relationship if agent exists
            WITH conv
            OPTIONAL MATCH (agent:Agent {id: $agent_id})
            WHERE $agent_id IS NOT NULL
            FOREACH (a IN CASE WHEN agent IS NOT NULL THEN [agent] ELSE [] END |
                MERGE (conv)-[:HANDLED_BY]->(a)
            )
            
            RETURN conv.id as conversation_id
            """
            
            result = await session.run(query, {
                'conversation_id': conversation.conversation_id,
                'customer_id': conversation.customer_id,
                'agent_id': conversation.agent_id,
                'raw_text': conversation_text,
                'summary': canonical_data.get('conversation_summary', ''),
                'batch_id': batch_id,
                'created_at': conversation.created_at.isoformat() if conversation.created_at else None,
                'resolved_at': conversation.resolved_at.isoformat() if conversation.resolved_at else None,
                'timestamp': timestamp.isoformat()
            })
            
            summary = await result.consume()
            result_data = {
                "nodes_created": summary.counters.nodes_created,
                "relationships_created": summary.counters.relationships_created,
                "properties_set": summary.counters.properties_set
            }
            
        logger.info(f"Conversation stored: {result_data}")
        
        # Process issues
        issues = canonical_data.get('issues', [])
        logger.info(f"Processing {len(issues)} issues")
        for issue_data in issues:
            await self._store_issue(issue_data, conversation.conversation_id, timestamp)
        
        # Process solutions
        solutions = canonical_data.get('solutions', [])
        logger.info(f"Processing {len(solutions)} solutions")
        for solution_data in solutions:
            await self._store_solution(solution_data, conversation.conversation_id, timestamp)
    
    async def _store_issue(self, issue_data: Dict, conversation_id: str, timestamp: datetime):
        """Store issue node with embedding"""
        issue_id = str(uuid.uuid4())
        
        # Generate embedding
        embedding_text = f"{issue_data['canonical_description']} {issue_data['one_liner']}"
        embedding = await self.llm_service.generate_embedding(embedding_text)
        
        # Check for similar existing issues
        similar_issues = await self._find_similar_issues(embedding)
        
        if similar_issues:
            # Merge with existing issue (simplified)
            existing_issue_id = similar_issues[0]['i']['id']
            logger.info(f"Merging issue with existing issue {existing_issue_id}")
            issue_id = existing_issue_id
        else:
            # Create new issue
            issue_query = """
            CREATE (i:Issue {
                id: $issue_id,
                canonical_description: $canonical_description,
                one_liner: $one_liner,
                tags: $tags,
                intent: $intent,
                embedding: $embedding,
                quality_score: 0.5,
                human_reviewed: false,
                created_at: $timestamp,
                updated_at: $timestamp
            })
            """
            
            # Use direct driver access
            async with self.neo4j.driver.session(database="neo4j") as session:
                result = await session.run(issue_query, {
                    'issue_id': issue_id,
                    'canonical_description': issue_data['canonical_description'],
                    'one_liner': issue_data['one_liner'],
                    'tags': issue_data.get('tags', []),
                    'intent': issue_data.get('intent', ''),
                    'embedding': embedding,
                    'timestamp': timestamp
                })
                summary = await result.consume()
                result_data = {
                    "nodes_created": summary.counters.nodes_created,
                    "relationships_created": summary.counters.relationships_created,
                    "properties_set": summary.counters.properties_set
                }
            logger.info(f"Issue node created: {result_data}")
        
        # Link to conversation
        link_query = """
        MATCH (i:Issue {id: $issue_id}), (c:Conversation {id: $conversation_id})
        MERGE (c)-[:CONTAINS_ISSUE]->(i)
        """
        
        # Use direct driver access for linking
        async with self.neo4j.driver.session(database="neo4j") as session:
            await session.run(link_query, {
                'issue_id': issue_id,
                'conversation_id': conversation_id
            })
    
    async def _store_solution(self, solution_data: Dict, conversation_id: str, timestamp: datetime):
        """Store solution node with embedding"""
        solution_id = str(uuid.uuid4())
        
        # Generate embedding
        embedding_text = f"{solution_data['canonical_description']} {solution_data['one_liner']}"
        embedding = await self.llm_service.generate_embedding(embedding_text)
        
        # Create solution
        solution_query = """
        CREATE (s:Solution {
            id: $solution_id,
            canonical_description: $canonical_description,
            one_liner: $one_liner,
            steps: $steps,
            confidence: $confidence,
            embedding: $embedding,
            quality_score: $confidence,
            human_reviewed: false,
            created_at: $timestamp,
            updated_at: $timestamp
        })
        """
        
        # Use direct driver access
        async with self.neo4j.driver.session(database="neo4j") as session:
            result = await session.run(solution_query, {
                'solution_id': solution_id,
                'canonical_description': solution_data['canonical_description'],
                'one_liner': solution_data['one_liner'],
                'steps': solution_data.get('steps', []),
                'confidence': solution_data.get('confidence', 0.5),
                'embedding': embedding,
                'timestamp': timestamp
            })
            summary = await result.consume()
            result_data = {
                "nodes_created": summary.counters.nodes_created,
                "relationships_created": summary.counters.relationships_created,
                "properties_set": summary.counters.properties_set
            }
        logger.info(f"Solution node created: {result_data}")
        
        # Link to conversation
        link_query = """
        MATCH (s:Solution {id: $solution_id}), (c:Conversation {id: $conversation_id})
        MERGE (c)-[:CONTAINS_SOLUTION]->(s)
        """
        
        # Use direct driver access for linking
        async with self.neo4j.driver.session(database="neo4j") as session:
            await session.run(link_query, {
                'solution_id': solution_id,
                'conversation_id': conversation_id
            })
    
    async def _find_similar_issues(self, embedding: List[float], threshold: float = 0.85) -> List[Dict]:
        """Find similar issues using vector similarity"""
        try:
            query = """
            CALL db.index.vector.queryNodes('issue_embeddings', $k, $embedding)
            YIELD node as i, score
            WHERE score >= $threshold
            RETURN i, score
            ORDER BY score DESC
            """
            
            # Use direct driver access
            async with self.neo4j.driver.session(database="neo4j") as session:
                result = await session.run(query, {
                    'embedding': embedding,
                    'k': 5,
                    'threshold': threshold
                })
                records = []
                async for record in result:
                    records.append(record.data())
                return records
        except Exception as e:
            # If vector index doesn't exist, log warning and return empty
            # This allows ingestion to continue without vector similarity
            logger.warning(f"Vector similarity search failed (index may not exist): {e}")
            logger.info("Continuing without similarity matching - each issue will be created as new")
            return []
