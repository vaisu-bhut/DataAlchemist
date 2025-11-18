from neo4j import AsyncGraphDatabase
import structlog
import asyncio
from typing import List, Dict, Any, Optional
from core.config import settings

logger = structlog.get_logger()

class Neo4jConnection:
    def __init__(self):
        self.driver = None
        
    async def connect(self, max_retries: int = 5, retry_delay: int = 5):
        """Connect to Neo4j with retry logic"""
        for attempt in range(max_retries):
            try:
                self.driver = AsyncGraphDatabase.driver(
                    settings.neo4j_uri,
                    auth=(settings.neo4j_user, settings.neo4j_password),
                    max_connection_lifetime=3600,
                    max_connection_pool_size=50,
                    connection_acquisition_timeout=60
                )
                # Test connection
                await self.driver.verify_connectivity()
                logger.info("Connected to Neo4j database")
                return
            except Exception as e:
                logger.warning(f"Connection attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                else:
                    logger.error(f"Failed to connect to Neo4j after {max_retries} attempts")
                    raise
    
    async def close(self):
        if self.driver:
            await self.driver.close()
            logger.info("Neo4j connection closed")
    
    async def initialize_schema(self):
        """Initialize database schema and indexes"""
        if not self.driver:
            raise RuntimeError("Database connection not established")
            
        async with self.driver.session(database="neo4j") as session:
            # Wait for Neo4j to be fully ready
            await self._wait_for_database_ready(session)
            
            logger.info("Initializing database schema...")
            
            # Create constraints
            constraints = [
                "CREATE CONSTRAINT conversation_id IF NOT EXISTS FOR (c:Conversation) REQUIRE c.id IS UNIQUE",
                "CREATE CONSTRAINT issue_id IF NOT EXISTS FOR (i:Issue) REQUIRE i.id IS UNIQUE", 
                "CREATE CONSTRAINT solution_id IF NOT EXISTS FOR (s:Solution) REQUIRE s.id IS UNIQUE",
                "CREATE CONSTRAINT customer_id IF NOT EXISTS FOR (c:Customer) REQUIRE c.id IS UNIQUE",
                "CREATE CONSTRAINT agent_id IF NOT EXISTS FOR (a:Agent) REQUIRE a.id IS UNIQUE"
            ]
            
            constraints_created = 0
            for constraint in constraints:
                try:
                    await session.run(constraint)
                    constraints_created += 1
                    logger.info(f"✅ Created constraint: {constraint.split('FOR')[1].split('REQUIRE')[0].strip()}")
                except Exception as e:
                    # Check if it's because constraint already exists
                    if "already exists" in str(e).lower() or "equivalent" in str(e).lower():
                        logger.debug(f"Constraint already exists (OK)")
                    else:
                        logger.warning(f"Constraint creation failed: {e}")
            
            logger.info(f"Constraints ready: {constraints_created} created/verified")
            
            # Create vector indexes for embeddings
            vector_indexes = [
                ("issue_embeddings", """
                CREATE VECTOR INDEX issue_embeddings IF NOT EXISTS
                FOR (i:Issue) ON (i.embedding)
                OPTIONS {indexConfig: {
                    `vector.dimensions`: 768,
                    `vector.similarity_function`: 'cosine'
                }}
                """),
                ("solution_embeddings", """
                CREATE VECTOR INDEX solution_embeddings IF NOT EXISTS  
                FOR (s:Solution) ON (s.embedding)
                OPTIONS {indexConfig: {
                    `vector.dimensions`: 768,
                    `vector.similarity_function`: 'cosine'
                }}
                """)
            ]
            
            vector_indexes_created = 0
            vector_indexes_supported = True
            
            for index_name, index_query in vector_indexes:
                try:
                    await session.run(index_query)
                    vector_indexes_created += 1
                    logger.info(f"✅ Created vector index: {index_name}")
                except Exception as e:
                    error_str = str(e).lower()
                    if "already exists" in error_str or "equivalent" in error_str:
                        logger.debug(f"Vector index {index_name} already exists (OK)")
                        vector_indexes_created += 1
                    elif "unknown command" in error_str or "no procedure" in error_str:
                        vector_indexes_supported = False
                        logger.warning(f"⚠️  Vector indexes not supported by this Neo4j version")
                        logger.warning(f"   Ingestion will work but without similarity deduplication")
                        break
                    else:
                        logger.error(f"❌ Vector index creation failed for {index_name}: {e}")
            
            if vector_indexes_supported:
                logger.info(f"✅ Vector indexes ready: {vector_indexes_created}/2")
            else:
                logger.warning("⚠️  Vector indexes not available - requires Neo4j 5.11+")
                logger.warning("   System will work but without vector similarity search")
            
            logger.info("✅ Database schema initialization complete")
    
    async def _wait_for_database_ready(self, session, max_retries: int = 10):
        """Wait for Neo4j database to be fully ready"""
        for attempt in range(max_retries):
            try:
                await session.run("RETURN 1")
                logger.info("Database is ready")
                return
            except Exception as e:
                logger.warning(f"Database not ready, attempt {attempt + 1}/{max_retries}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)
                else:
                    raise RuntimeError("Database failed to become ready")
    
    async def execute_query(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict]:
        """Execute a Cypher query and return results"""
        if not self.driver:
            raise RuntimeError("Database connection not established")
            
        async with self.driver.session(database="neo4j") as session:
            try:
                result = await session.run(query, parameters or {})
                records = []
                async for record in result:
                    records.append(record.data())
                return records
            except Exception as e:
                logger.error(f"Query execution failed: {e}")
                raise
    
    async def execute_write(self, query: str, parameters: Dict[str, Any] = None) -> Dict:
        """Execute a write query and return summary"""
        if not self.driver:
            raise RuntimeError("Database connection not established")
            
        async with self.driver.session(database="neo4j") as session:
            try:
                result = await session.run(query, parameters or {})
                summary = await result.consume()
                return {
                    "nodes_created": summary.counters.nodes_created,
                    "relationships_created": summary.counters.relationships_created,
                    "properties_set": summary.counters.properties_set
                }
            except Exception as e:
                logger.error(f"Write query execution failed: {e}")
                raise
    
    async def health_check(self) -> bool:
        """Check if the database connection is healthy"""
        try:
            if not self.driver:
                return False
            await self.driver.verify_connectivity()
            return True
        except Exception:
            return False