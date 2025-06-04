"""
RAG Adapters Infrastructure

This module contains RAG (Retrieval-Augmented Generation) integration adapters
for various game systems, providing LLM and knowledge base connectivity.
"""

from .npc_rag_adapter import NPCRAGService, get_npc_rag_service

__all__ = [
    'NPCRAGService',
    'get_npc_rag_service'
] 