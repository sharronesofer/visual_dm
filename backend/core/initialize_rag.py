"""
Cross-System RAG Initialization
Sets up the complete RAG infrastructure and loads initial knowledge
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from pathlib import Path

from .rag_service import initialize_rag_service, RAGConfiguration
from .knowledge_loader import initialize_game_knowledge
from .rag_client import create_rag_client

async def initialize_cross_system_rag(
    config: Optional[RAGConfiguration] = None,
    load_sample_data: bool = True,
    load_documentation: bool = True
) -> Dict[str, Any]:
    """
    Initialize the complete cross-system RAG infrastructure
    
    Args:
        config: Optional custom RAG configuration
        load_sample_data: Whether to load sample knowledge entries
        load_documentation: Whether to load system documentation
        
    Returns:
        Dictionary with initialization results and statistics
    """
    logger = logging.getLogger(__name__)
    results = {
        'success': False,
        'rag_service_initialized': False,
        'knowledge_loaded': False,
        'systems_initialized': [],
        'errors': [],
        'statistics': {}
    }
    
    try:
        # 1. Initialize core RAG service
        logger.info("Initializing core RAG service...")
        rag_service = await initialize_rag_service(config)
        
        if rag_service.is_initialized:
            results['rag_service_initialized'] = True
            logger.info("Core RAG service initialized successfully")
        else:
            results['errors'].append("Failed to initialize core RAG service")
            return results
        
        # 2. Load initial knowledge
        if load_sample_data or load_documentation:
            logger.info("Loading initial knowledge...")
            try:
                knowledge_results = await initialize_game_knowledge()
                results['knowledge_loaded'] = True
                results['knowledge_results'] = knowledge_results
                logger.info(f"Knowledge loading completed: {knowledge_results}")
            except Exception as e:
                results['errors'].append(f"Failed to load knowledge: {e}")
                logger.error(f"Knowledge loading failed: {e}")
        
        # 3. Initialize system-specific RAG clients
        systems_to_initialize = [
            'dialogue', 'quest', 'npc', 'faction', 'memory', 
            'rumor', 'magic', 'world_generation', 'motif'
        ]
        
        logger.info("Initializing system-specific RAG clients...")
        for system in systems_to_initialize:
            try:
                client = await create_rag_client(system)
                if client:
                    results['systems_initialized'].append(system)
                    logger.debug(f"Initialized RAG client for {system}")
            except Exception as e:
                results['errors'].append(f"Failed to initialize {system} RAG client: {e}")
                logger.error(f"Failed to initialize {system} RAG client: {e}")
        
        # 4. Get statistics
        try:
            stats = await rag_service.get_statistics()
            results['statistics'] = stats
            logger.info(f"RAG statistics: {stats['total_entries']} total entries across {len(stats['collections'])} systems")
        except Exception as e:
            results['errors'].append(f"Failed to get statistics: {e}")
            logger.error(f"Failed to get statistics: {e}")
        
        # 5. Mark as successful if core components are working
        if results['rag_service_initialized'] and len(results['systems_initialized']) > 0:
            results['success'] = True
            logger.info(f"Cross-system RAG initialized successfully with {len(results['systems_initialized'])} systems")
        
        return results
        
    except Exception as e:
        results['errors'].append(f"Critical error during initialization: {e}")
        logger.error(f"Critical error during RAG initialization: {e}")
        return results

async def load_system_knowledge(
    system: str, 
    knowledge_data: List[Dict[str, Any]]
) -> Dict[str, int]:
    """
    Load knowledge entries for a specific system
    
    Args:
        system: Name of the system
        knowledge_data: List of knowledge entries to load
        
    Returns:
        Dictionary with success/failure counts
    """
    logger = logging.getLogger(__name__)
    results = {'success': 0, 'failed': 0}
    
    try:
        client = await create_rag_client(system)
        
        for entry_data in knowledge_data:
            try:
                success = await client.add_knowledge(
                    content=entry_data.get('content', ''),
                    category=entry_data.get('category', system),
                    metadata=entry_data.get('metadata', {}),
                    tags=entry_data.get('tags', [])
                )
                
                if success:
                    results['success'] += 1
                else:
                    results['failed'] += 1
                    
            except Exception as e:
                logger.error(f"Failed to add knowledge entry to {system}: {e}")
                results['failed'] += 1
        
        logger.info(f"Loaded knowledge for {system}: {results['success']} successful, {results['failed']} failed")
        
    except Exception as e:
        logger.error(f"Failed to load knowledge for system {system}: {e}")
        results['failed'] = len(knowledge_data)
    
    return results

async def test_rag_functionality() -> Dict[str, Any]:
    """
    Test basic RAG functionality across systems
    
    Returns:
        Dictionary with test results
    """
    logger = logging.getLogger(__name__)
    test_results = {
        'success': True,
        'tests_passed': 0,
        'tests_failed': 0,
        'system_tests': {}
    }
    
    test_systems = ['dialogue', 'quest', 'npc']
    test_queries = {
        'dialogue': "How should NPCs greet players?",
        'quest': "What makes a good fetch quest?",
        'npc': "NPC personality traits for merchants"
    }
    
    for system in test_systems:
        try:
            client = await create_rag_client(system)
            query = test_queries.get(system, "test query")
            
            # Test query functionality
            results = await client.query(query, max_results=3)
            
            # Test response enhancement
            base_response = "This is a test response."
            enhanced = await client.enhance_response(
                base_response=base_response,
                context=query
            )
            
            test_results['system_tests'][system] = {
                'query_results': len(results),
                'enhancement_worked': enhanced.context_used,
                'success': True
            }
            test_results['tests_passed'] += 1
            
        except Exception as e:
            test_results['system_tests'][system] = {
                'error': str(e),
                'success': False
            }
            test_results['tests_failed'] += 1
            test_results['success'] = False
            logger.error(f"RAG test failed for {system}: {e}")
    
    logger.info(f"RAG functionality tests: {test_results['tests_passed']} passed, {test_results['tests_failed']} failed")
    return test_results

async def get_rag_status() -> Dict[str, Any]:
    """
    Get current status of the RAG system
    
    Returns:
        Dictionary with current RAG status
    """
    from .rag_service import get_rag_service
    
    try:
        rag_service = await get_rag_service()
        stats = await rag_service.get_statistics()
        
        status = {
            'initialized': stats['initialized'],
            'total_entries': stats['total_entries'],
            'systems': list(stats['collections'].keys()),
            'system_counts': stats['collections'],
            'cache_size': stats['cache_size']
        }
        
        return status
        
    except Exception as e:
        return {
            'initialized': False,
            'error': str(e)
        }

def create_sample_knowledge_entries() -> List[Dict[str, Any]]:
    """
    Create sample knowledge entries for testing and demonstration
    
    Returns:
        List of sample knowledge entries
    """
    return [
        {
            'content': 'NPCs should have varied greeting patterns based on their personality, relationship with the player, and current circumstances.',
            'category': 'dialogue',
            'system': 'dialogue',
            'metadata': {'type': 'guideline', 'priority': 'high'},
            'tags': ['greeting', 'npc', 'personality']
        },
        {
            'content': 'Quest rewards should scale with difficulty and provide meaningful progression for the player character.',
            'category': 'quests',
            'system': 'quest',
            'metadata': {'type': 'design_principle', 'priority': 'medium'},
            'tags': ['rewards', 'progression', 'difficulty']
        },
        {
            'content': 'Magic spells should have clear costs, limitations, and visual effects to maintain game balance and immersion.',
            'category': 'magic',
            'system': 'magic',
            'metadata': {'type': 'game_rule', 'priority': 'high'},
            'tags': ['spells', 'balance', 'mechanics']
        },
        {
            'content': 'Faction relationships should influence NPC behavior, quest availability, and dialogue options throughout the game.',
            'category': 'factions',
            'system': 'faction',
            'metadata': {'type': 'system_mechanic', 'priority': 'high'},
            'tags': ['factions', 'relationships', 'influence']
        },
        {
            'content': 'Memory systems should prioritize recent interactions, emotionally significant events, and character-relevant information.',
            'category': 'memory',
            'system': 'memory',
            'metadata': {'type': 'algorithm_guideline', 'priority': 'medium'},
            'tags': ['memory', 'prioritization', 'events']
        }
    ]

# CLI-style interface for testing
async def main():
    """Main function for testing RAG initialization"""
    import sys
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'init':
            logger.info("Initializing cross-system RAG...")
            results = await initialize_cross_system_rag()
            print(f"Initialization results: {results}")
            
        elif command == 'test':
            logger.info("Testing RAG functionality...")
            test_results = await test_rag_functionality()
            print(f"Test results: {test_results}")
            
        elif command == 'status':
            logger.info("Getting RAG status...")
            status = await get_rag_status()
            print(f"RAG status: {status}")
            
        elif command == 'load-samples':
            logger.info("Loading sample knowledge...")
            sample_entries = create_sample_knowledge_entries()
            
            for system in ['dialogue', 'quest', 'magic', 'faction', 'memory']:
                system_entries = [e for e in sample_entries if e['system'] == system]
                if system_entries:
                    results = await load_system_knowledge(system, system_entries)
                    print(f"Loaded {system}: {results}")
        
        else:
            print("Available commands: init, test, status, load-samples")
    else:
        print("Usage: python initialize_rag.py <command>")
        print("Commands: init, test, status, load-samples")

if __name__ == "__main__":
    asyncio.run(main()) 