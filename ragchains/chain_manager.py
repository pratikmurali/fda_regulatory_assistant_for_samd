"""
RAG Chain Manager for FDA Regulatory Assistant.

This module provides a centralized manager for RAG chains that maintains
the singleton pattern while allowing access from tools and agents.
"""

import asyncio
from typing import Optional, Dict, Any
from ragchains.fda_cybersecurity_rag import fda_cybersecurity_rag
from ragchains.fda_regulatory_rag import fda_regulatory_rag
from loaders.load_pdf_from_s3 import load_pdf_from_public_s3


class RAGChainManager:
    """
    Centralized manager for RAG chains with singleton pattern and thread-safety.

    This class ensures that RAG chains are loaded only once and can be accessed
    from multiple contexts (Chainlit UI, LangGraph agents, tools, etc.).
    """

    _instance: Optional["RAGChainManager"] = None
    _lock = asyncio.Lock()

    def __new__(cls) -> "RAGChainManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Only initialize once
        if not hasattr(self, "_initialized"):
            self._cybersecurity_chain: Optional[object] = None
            self._regulatory_chain: Optional[object] = None
            self._initialization_lock = asyncio.Lock()
            self._initialized = True

    async def get_cybersecurity_chain(self):
        """Get or initialize the cybersecurity RAG chain (singleton pattern)"""
        if self._cybersecurity_chain is None:
            async with self._initialization_lock:
                # Double-check pattern to avoid race conditions
                if self._cybersecurity_chain is None:
                    print("🔄 Loading FDA cybersecurity documents from S3...")
                    docs = load_pdf_from_public_s3(
                        "s3://fda-samd-cybersecurity-guidance/"
                    )
                    print(f"✅ Loaded {len(docs)} cybersecurity documents")
                    print("🔄 Building cybersecurity RAG chain...")
                    self._cybersecurity_chain = fda_cybersecurity_rag(docs)
                    print("✅ Cybersecurity RAG chain ready!")

        return self._cybersecurity_chain

    async def get_regulatory_chain(self):
        """Get or initialize the regulatory RAG chain (singleton pattern)"""
        if self._regulatory_chain is None:
            async with self._initialization_lock:
                # Double-check pattern to avoid race conditions
                if self._regulatory_chain is None:
                    print("🔄 Loading FDA regulatory documents from S3...")
                    docs = load_pdf_from_public_s3("s3://fda-samd-regulatory-guidance/")
                    print(f"✅ Loaded {len(docs)} regulatory documents")
                    print("🔄 Building regulatory RAG chain...")
                    self._regulatory_chain = fda_regulatory_rag(docs)
                    print("✅ Regulatory RAG chain ready!")

        return self._regulatory_chain

    async def prewarm_chains(self):
        """Pre-warm both RAG chains at application startup"""
        print("🚀 Pre-warming RAG chains...")
        await asyncio.gather(
            self.get_cybersecurity_chain(), self.get_regulatory_chain()
        )
        print("🚀 All RAG chains pre-warmed and ready!")

    async def query_cybersecurity_chain(self, question: str) -> Dict[str, Any]:
        """
        Query the cybersecurity RAG chain with a question.

        Args:
            question: The question to ask the cybersecurity chain

        Returns:
            Dictionary containing the answer and sources
        """
        chain = await self.get_cybersecurity_chain()
        return chain.invoke(question)

    async def query_regulatory_chain(self, question: str) -> Dict[str, Any]:
        """
        Query the regulatory RAG chain with a question.

        Args:
            question: The question to ask the regulatory chain

        Returns:
            Dictionary containing the answer and sources
        """
        chain = await self.get_regulatory_chain()
        return chain.invoke(question)

    def get_cybersecurity_chain_sync(self):
        """
        Synchronous version of get_cybersecurity_chain for use in tools.

        Note: This assumes the chain has already been initialized.
        If not initialized, it will return None and log a warning.
        """
        if self._cybersecurity_chain is None:
            print(
                "⚠️  Warning: Cybersecurity chain not initialized. Call prewarm_chains() first."
            )
            return None
        return self._cybersecurity_chain

    def get_regulatory_chain_sync(self):
        """
        Synchronous version of get_regulatory_chain for use in tools.

        Note: This assumes the chain has already been initialized.
        If not initialized, it will return None and log a warning.
        """
        if self._regulatory_chain is None:
            print(
                "⚠️  Warning: Regulatory chain not initialized. Call prewarm_chains() first."
            )
            return None
        return self._regulatory_chain

    def query_cybersecurity_chain_sync(self, question: str) -> Optional[Dict[str, Any]]:
        """
        Synchronous version of query_cybersecurity_chain for use in tools.

        Args:
            question: The question to ask the cybersecurity chain

        Returns:
            Dictionary containing the answer and sources, or None if chain not initialized
        """
        chain = self.get_cybersecurity_chain_sync()
        if chain is None:
            return {
                "answer": "Cybersecurity chain not initialized. Please ensure the application is properly started.",
                "sources": [],
            }
        return chain.invoke(question)

    def query_regulatory_chain_sync(self, question: str) -> Optional[Dict[str, Any]]:
        """
        Synchronous version of query_regulatory_chain for use in tools.

        Args:
            question: The question to ask the regulatory chain

        Returns:
            Dictionary containing the answer and sources, or None if chain not initialized
        """
        chain = self.get_regulatory_chain_sync()
        if chain is None:
            return {
                "answer": "Regulatory chain not initialized. Please ensure the application is properly started.",
                "sources": [],
            }
        return chain.invoke(question)

    def is_initialized(self) -> Dict[str, bool]:
        """
        Check which chains are initialized.

        Returns:
            Dictionary with initialization status of each chain
        """
        return {
            "cybersecurity": self._cybersecurity_chain is not None,
            "regulatory": self._regulatory_chain is not None,
        }


# Global instance for easy access
_chain_manager: Optional[RAGChainManager] = None


def get_chain_manager() -> RAGChainManager:
    """Get the global RAG chain manager instance."""
    global _chain_manager
    if _chain_manager is None:
        _chain_manager = RAGChainManager()
    return _chain_manager
