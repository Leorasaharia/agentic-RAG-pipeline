from typing import Generator
from backend.agents.retriever_agent import RetrieverAgent
from backend.agents.verifier_agent import VerifierAgent
from backend.agents.refiner_agent import RefinerAgent
from backend.utils.logger import get_logger

logger = get_logger(__name__)

class RAGOrchestrator:
    """Manages the end-to-end RAG pipeline across multiple agents."""

    def __init__(self):
        self.retriever = RetrieverAgent()
        self.verifier = VerifierAgent()
        self.refiner = RefinerAgent()

    def process_query_stream(self, query: str) -> Generator[str, None, None]:
        logger.info(f"[Orchestrator] Starting processing pipeline for query: {query}")

        # Step 1: Retrieve context chunks
        chunks = self.retriever.run(query)

        # Step 2: Verify and filter chunks
        verified_chunks, issues = self.verifier.run(query, chunks)
        if issues:
            logger.info(f"[Orchestrator] Addressed {len(issues)} issues during verification.")

        # Step 3: Stream Refined Response
        response_stream = self.refiner.run(
            query=query, 
            context_chunks=verified_chunks, 
            stream=True
        )

        return response_stream

    def process_query_sync(self, query: str) -> str:
        """Non-streaming version for traditional REST calls if needed."""
        chunks = self.retriever.run(query)
        verified_chunks, _ = self.verifier.run(query, chunks)
        response = self.refiner.run(query, verified_chunks, stream=False)
        return response
