"""
RAG Integration Infrastructure Module

Provides technical infrastructure for Retrieval-Augmented Generation,
including vector database operations, embedding models, and LLM integration.
"""

from .dialogue_rag_integration import DialogueRAGIntegration, initialize_dialogue_rag, populate_initial_knowledge

__all__ = [
    'DialogueRAGIntegration',
    'initialize_dialogue_rag', 
    'populate_initial_knowledge'
] 