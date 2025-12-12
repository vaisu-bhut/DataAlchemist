import google.generativeai as genai
import numpy as np
from typing import List, Dict, Any, Optional
import structlog
import json
from core.config import settings

logger = structlog.get_logger()


class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model_name)
        self.embedding_model = settings.gemini_embedding_model

    async def check_general_chat(self, query: str) -> Optional[str]:
        """
        Check if the query is a simple greeting/pleasantry.
        Returns the response string if it is a greeting, or None if search is required.
        """
        prompt = f"""
        You are a helpful customer support AI.
        Analyze this user message: "{query}"
        
        Is this a simple greeting, pleasantry, expression of gratitude, or closing (e.g. 'hello', 'hi', 'hii', 'hey', 'thanks', 'good morning', 'bye', 'ok') that does NOT require searching a knowledge base?
        
        - If YES (it's just chat): Reply with a polite, friendly, and brief response suitable for a support agent.
        - If NO (it's a question or issue): Respond with exactly "SEARCH_REQUIRED".
        
        Do not provide any other text, just the response or "SEARCH_REQUIRED".
        """

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()

            if "SEARCH_REQUIRED" in text:
                return None
            return text
        except Exception as e:
            logger.error(f"General chat check failed: {e}")
            return None

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using Gemini"""
        try:
            result = genai.embed_content(
                model=self.embedding_model, content=text, task_type="retrieval_document"
            )
            return result["embedding"]
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise

    async def extract_canonical_data(self, conversation_text: str) -> Dict[str, Any]:
        """Extract canonical issues and solutions from conversation"""
        prompt = f"""
        Analyze this customer support conversation and extract:
        1. Primary issue(s) - canonical description of the problem
        2. Solution(s) - step-by-step resolution 
        3. One-line summary of the resolution
        4. Confidence score (0-1) for solution quality
        5. Tags/categories
        6. Intent classification
        
        Return as JSON with this structure:
        {{
            "issues": [
                {{
                    "canonical_description": "Clear problem statement",
                    "one_liner": "Brief issue summary",
                    "tags": ["tag1", "tag2"],
                    "intent": "intent_category"
                }}
            ],
            "solutions": [
                {{
                    "canonical_description": "Step-by-step solution",
                    "one_liner": "Brief resolution summary", 
                    "steps": ["step1", "step2"],
                    "confidence": 0.85
                }}
            ],
            "overall_confidence": 0.8,
            "conversation_summary": "Brief conversation summary"
        }}
        
        Conversation:
        {conversation_text}
        """

        try:
            response = self.model.generate_content(prompt)
            # Extract JSON from response
            json_start = response.text.find("{")
            json_end = response.text.rfind("}") + 1
            json_str = response.text[json_start:json_end]
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"Canonical data extraction failed: {e}")
            raise

    async def synthesize_response(
        self,
        query: str,
        candidates: List[Dict],
        customer_context: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Synthesize response from retrieved candidates"""
        candidates_text = "\n\n".join(
            [
                f"Source {i + 1} (ID: {c.get('source_id', 'unknown')}):\n"
                f"Issue: {c.get('issue', '')}\n"
                f"Solution: {c.get('solution', '')}\n"
                f"Quality Score: {c.get('quality_score', 0)}"
                for i, c in enumerate(candidates)
            ]
        )

        prompt = f"""
        You are a customer support AI. Based on the retrieved knowledge below, provide a helpful response to the customer query.
        
        REQUIREMENTS:
        1. STRUCTURE THE RESPONSE AS DETAILED STEP-BY-STEP INSTRUCTIONS if relevant context exists. If the retrieved steps are brief, present them clearly as steps.
        2. Always cite sources using [Source X] format.
        3. Provide a confidence score (0-1).
        4. Never hallucinate - only use provided information.
        5. Be concise but complete.
        
        Customer Query: {query}
        
        Retrieved Knowledge:
        {candidates_text}
        
        Return JSON response:
        {{
            "response": "Detailed step-by-step instructions with [Source X] citations",
            "confidence": 0.85,
            "source_ids": ["id1", "id2"],
            "reasoning": "Brief explanation of confidence level"
        }}
        """

        try:
            response = self.model.generate_content(prompt)
            json_start = response.text.find("{")
            json_end = response.text.rfind("}") + 1
            json_str = response.text[json_start:json_end]
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"Response synthesis failed: {e}")
            raise

    def cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        a_np = np.array(a)
        b_np = np.array(b)
        return np.dot(a_np, b_np) / (np.linalg.norm(a_np) * np.linalg.norm(b_np))
