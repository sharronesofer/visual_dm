"""
Knowledge Loader
Utilities for loading knowledge from various sources into the RAG system
"""

import logging
import asyncio
import json
import yaml
import csv
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from datetime import datetime
import re

from .rag_service import KnowledgeEntry
from .rag_client import RAGKnowledgeManager

class KnowledgeLoader:
    """
    Utility for loading knowledge from various file formats and sources
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.knowledge_manager = RAGKnowledgeManager()
        
    async def initialize(self):
        """Initialize the knowledge loader"""
        await self.knowledge_manager.initialize()
    
    async def load_from_markdown(self, file_path: str, system: str, category: str) -> Dict[str, int]:
        """Load knowledge from Markdown files with section parsing"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            entries = []
            
            # Split by headers
            sections = re.split(r'^#+\s+(.+)$', content, flags=re.MULTILINE)
            
            current_header = "General"
            for i in range(1, len(sections), 2):
                if i + 1 < len(sections):
                    header = sections[i].strip()
                    section_content = sections[i + 1].strip()
                    
                    if section_content:
                        entry = KnowledgeEntry(
                            id=f"{system}_{category}_{header}_{hash(section_content)}",
                            content=f"# {header}\n\n{section_content}",
                            category=category,
                            system=system,
                            metadata={
                                'source_file': str(file_path),
                                'source_type': 'markdown',
                                'section': header
                            },
                            timestamp=datetime.now(),
                            tags=[header.lower().replace(' ', '_')]
                        )
                        entries.append(entry)
            
            return await self.knowledge_manager.bulk_add_knowledge(entries)
            
        except Exception as e:
            self.logger.error(f"Failed to load markdown from {file_path}: {e}")
            return {'success': 0, 'failed': 1}
    
    async def load_from_json(self, file_path: str, system: str, category: str, content_field: str = 'content') -> Dict[str, int]:
        """Load knowledge from JSON files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            entries = []
            
            if isinstance(data, list):
                for i, item in enumerate(data):
                    content = self._extract_content(item, content_field)
                    if content:
                        entry = self._create_entry_from_dict(item, content, system, category, file_path, i)
                        entries.append(entry)
            elif isinstance(data, dict):
                for key, item in data.items():
                    content = self._extract_content(item, content_field)
                    if content:
                        entry = self._create_entry_from_dict(item, content, system, category, file_path, key)
                        entries.append(entry)
            
            return await self.knowledge_manager.bulk_add_knowledge(entries)
            
        except Exception as e:
            self.logger.error(f"Failed to load JSON from {file_path}: {e}")
            return {'success': 0, 'failed': 1}
    
    async def load_from_yaml(self, file_path: str, system: str, category: str, content_field: str = 'content') -> Dict[str, int]:
        """Load knowledge from YAML files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            entries = []
            
            if isinstance(data, list):
                for i, item in enumerate(data):
                    content = self._extract_content(item, content_field)
                    if content:
                        entry = self._create_entry_from_dict(item, content, system, category, file_path, i)
                        entries.append(entry)
            elif isinstance(data, dict):
                for key, item in data.items():
                    content = self._extract_content(item, content_field)
                    if content:
                        entry = self._create_entry_from_dict(item, content, system, category, file_path, key)
                        entries.append(entry)
            
            return await self.knowledge_manager.bulk_add_knowledge(entries)
            
        except Exception as e:
            self.logger.error(f"Failed to load YAML from {file_path}: {e}")
            return {'success': 0, 'failed': 1}
    
    async def load_from_csv(self, file_path: str, system: str, category: str, content_column: str = 'content') -> Dict[str, int]:
        """Load knowledge from CSV files"""
        try:
            entries = []
            
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for i, row in enumerate(reader):
                    content = row.get(content_column, '')
                    if content:
                        metadata = {k: v for k, v in row.items() if k != content_column}
                        metadata.update({
                            'source_file': str(file_path),
                            'source_type': 'csv',
                            'row_number': i
                        })
                        
                        entry = KnowledgeEntry(
                            id=f"{system}_{category}_{i}_{hash(content)}",
                            content=content,
                            category=category,
                            system=system,
                            metadata=metadata,
                            timestamp=datetime.now(),
                            tags=[category.lower()]
                        )
                        entries.append(entry)
            
            return await self.knowledge_manager.bulk_add_knowledge(entries)
            
        except Exception as e:
            self.logger.error(f"Failed to load CSV from {file_path}: {e}")
            return {'success': 0, 'failed': 1}
    
    async def load_directory(self, directory_path: str, system: str, category_mapping: Optional[Dict[str, str]] = None) -> Dict[str, int]:
        """Load all supported files from a directory"""
        directory = Path(directory_path)
        total_results = {'success': 0, 'failed': 0}
        
        if not directory.exists():
            self.logger.error(f"Directory {directory_path} does not exist")
            return {'success': 0, 'failed': 1}
        
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                # Determine category from path or mapping
                category = self._determine_category(file_path, category_mapping, system)
                
                results = await self._load_file_by_extension(file_path, system, category)
                total_results['success'] += results['success']
                total_results['failed'] += results['failed']
        
        return total_results
    
    async def load_game_data(self, data_directory: str) -> Dict[str, Dict[str, int]]:
        """Load knowledge from structured game data directories"""
        results = {}
        data_path = Path(data_directory)
        
        # Define mappings for different game systems
        system_mappings = {
            'lore': {'system': 'dialogue', 'category': 'lore'},
            'characters': {'system': 'npc', 'category': 'characters'},
            'locations': {'system': 'region', 'category': 'locations'},
            'factions': {'system': 'faction', 'category': 'factions'},
            'quests': {'system': 'quest', 'category': 'quests'},
            'items': {'system': 'magic', 'category': 'items'},
            'spells': {'system': 'magic', 'category': 'magic'},
            'history': {'system': 'dialogue', 'category': 'history'},
            'rules': {'system': 'magic', 'category': 'rules'}
        }
        
        for folder_name, mapping in system_mappings.items():
            folder_path = data_path / folder_name
            if folder_path.exists():
                self.logger.info(f"Loading {folder_name} data from {folder_path}")
                results[folder_name] = await self.load_directory(
                    str(folder_path), 
                    mapping['system'], 
                    {folder_name: mapping['category']}
                )
        
        return results
    
    def _extract_content(self, item: Any, content_field: str) -> str:
        """Extract content from a data item"""
        if isinstance(item, str):
            return item
        elif isinstance(item, dict):
            # Try the specified field first
            if content_field in item:
                return str(item[content_field])
            
            # Fall back to common content fields
            for field in ['content', 'description', 'text', 'body', 'details']:
                if field in item:
                    return str(item[field])
            
            # If no content field found, create content from all fields
            return '\n'.join([f"{k}: {v}" for k, v in item.items() if isinstance(v, (str, int, float))])
        
        return str(item)
    
    def _create_entry_from_dict(self, item: dict, content: str, system: str, category: str, file_path: str, identifier: Union[str, int]) -> KnowledgeEntry:
        """Create a knowledge entry from a dictionary item"""
        metadata = {k: v for k, v in item.items() if k not in ['content', 'description', 'text', 'body', 'details']}
        metadata.update({
            'source_file': str(file_path),
            'source_type': 'structured_data'
        })
        
        # Extract tags from item
        tags = []
        if 'tags' in item:
            tags = item['tags'] if isinstance(item['tags'], list) else [item['tags']]
        elif 'type' in item:
            tags.append(str(item['type']).lower())
        
        tags.append(category.lower())
        
        return KnowledgeEntry(
            id=f"{system}_{category}_{identifier}_{hash(content)}",
            content=content,
            category=category,
            system=system,
            metadata=metadata,
            timestamp=datetime.now(),
            tags=tags
        )
    
    def _determine_category(self, file_path: Path, category_mapping: Optional[Dict[str, str]], default_system: str) -> str:
        """Determine category for a file based on its path"""
        if category_mapping:
            for pattern, category in category_mapping.items():
                if pattern in str(file_path):
                    return category
        
        # Extract category from parent directory name
        parent_name = file_path.parent.name.lower()
        return parent_name if parent_name else default_system
    
    async def _load_file_by_extension(self, file_path: Path, system: str, category: str) -> Dict[str, int]:
        """Load a file based on its extension"""
        extension = file_path.suffix.lower()
        
        try:
            if extension == '.md':
                return await self.load_from_markdown(str(file_path), system, category)
            elif extension == '.json':
                return await self.load_from_json(str(file_path), system, category)
            elif extension in ['.yml', '.yaml']:
                return await self.load_from_yaml(str(file_path), system, category)
            elif extension == '.csv':
                return await self.load_from_csv(str(file_path), system, category)
            elif extension == '.txt':
                return await self.knowledge_manager.import_from_file(str(file_path), system, category)
            else:
                self.logger.debug(f"Skipping unsupported file type: {file_path}")
                return {'success': 0, 'failed': 0}
                
        except Exception as e:
            self.logger.error(f"Failed to load file {file_path}: {e}")
            return {'success': 0, 'failed': 1}

class GameKnowledgeInitializer:
    """
    Utility for initializing game knowledge from existing game systems
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.loader = KnowledgeLoader()
    
    async def initialize(self):
        """Initialize the knowledge initializer"""
        await self.loader.initialize()
    
    async def load_system_documentation(self, docs_path: str = "docs/") -> Dict[str, Dict[str, int]]:
        """Load knowledge from system documentation"""
        results = {}
        docs_directory = Path(docs_path)
        
        if not docs_directory.exists():
            self.logger.warning(f"Documentation directory {docs_path} not found")
            return results
        
        # Load development bible sections
        bible_path = docs_directory / "development_bible.md"
        if bible_path.exists():
            results['development_bible'] = await self.loader.load_from_markdown(
                str(bible_path), 'dialogue', 'lore'
            )
        
        # Load system-specific documentation
        system_docs = {
            'dialogue': 'dialogue',
            'quest': 'quest', 
            'npc': 'npc',
            'faction': 'faction',
            'magic': 'magic',
            'memory': 'memory',
            'rumor': 'rumor'
        }
        
        for system, category in system_docs.items():
            system_doc_path = docs_directory / f"{system}.md"
            if system_doc_path.exists():
                results[system] = await self.loader.load_from_markdown(
                    str(system_doc_path), system, category
                )
        
        return results
    
    async def create_sample_knowledge(self) -> Dict[str, int]:
        """Create sample knowledge entries for testing"""
        entries = [
            # Dialogue system knowledge
            KnowledgeEntry(
                id="dialogue_greeting_001",
                content="Standard NPC greetings should vary based on time of day, weather, and the NPC's mood.",
                category="dialogue",
                system="dialogue",
                metadata={"type": "guideline", "priority": "high"},
                timestamp=datetime.now(),
                tags=["greeting", "npc", "variation"]
            ),
            
            # Quest system knowledge
            KnowledgeEntry(
                id="quest_design_001", 
                content="Fetch quests should include narrative context to make them engaging rather than simple collection tasks.",
                category="quests",
                system="quest",
                metadata={"type": "design_principle", "priority": "medium"},
                timestamp=datetime.now(),
                tags=["fetch", "design", "narrative"]
            ),
            
            # Magic system knowledge
            KnowledgeEntry(
                id="magic_schools_001",
                content="The five schools of magic are: Evocation (damage), Conjuration (summoning), Enchantment (mind effects), Transmutation (transformation), and Divination (information).",
                category="magic",
                system="magic", 
                metadata={"type": "lore", "priority": "high"},
                timestamp=datetime.now(),
                tags=["schools", "magic_system", "lore"]
            ),
            
            # Faction system knowledge
            KnowledgeEntry(
                id="faction_relations_001",
                content="Faction relationships should influence dialogue options, quest availability, and NPC behavior throughout the game world.",
                category="factions",
                system="faction",
                metadata={"type": "mechanic", "priority": "high"},
                timestamp=datetime.now(),
                tags=["relationships", "mechanics", "influence"]
            ),
            
            # NPC system knowledge
            KnowledgeEntry(
                id="npc_personality_001",
                content="NPCs should have distinct personality traits that influence their dialogue patterns, quest offerings, and reactions to player actions.",
                category="npcs",
                system="npc",
                metadata={"type": "design_guideline", "priority": "medium"},
                timestamp=datetime.now(),
                tags=["personality", "traits", "behavior"]
            )
        ]
        
        return await self.loader.knowledge_manager.bulk_add_knowledge(entries)
    
    async def initialize_baseline_knowledge(self) -> Dict[str, Any]:
        """Initialize baseline knowledge for all systems"""
        results = {
            'documentation': await self.load_system_documentation(),
            'sample_data': await self.create_sample_knowledge()
        }
        
        # Try to load from common data directories
        common_paths = ["data/", "content/", "game_data/"]
        for path in common_paths:
            if Path(path).exists():
                results[f'data_{path.rstrip("/")}'] = await self.loader.load_game_data(path)
        
        return results

# Global initializer instance
_initializer = None

async def get_knowledge_initializer() -> GameKnowledgeInitializer:
    """Get or create the global knowledge initializer"""
    global _initializer
    if _initializer is None:
        _initializer = GameKnowledgeInitializer()
        await _initializer.initialize()
    return _initializer

async def initialize_game_knowledge() -> Dict[str, Any]:
    """Initialize all game knowledge from available sources"""
    initializer = await get_knowledge_initializer()
    return await initializer.initialize_baseline_knowledge() 