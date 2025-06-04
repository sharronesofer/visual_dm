#!/usr/bin/env python3
"""
Quest System CLI Tools
Provides command-line utilities for quest development, debugging, and maintenance.
"""

import click
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add the backend directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    from backend.services.quest.models import QuestStatus, QuestDifficulty, QuestTheme
    from backend.services.quest.services import QuestBusinessService
    from backend.services.quest.generator import QuestGenerator
    from backend.infrastructure.config.quest_config_loader import QuestConfigLoader
    from backend.infrastructure.cache.quest_cache import get_quest_cache, QuestCacheManager
except ImportError as e:
    click.echo(f"Error importing quest modules: {e}")
    click.echo("Make sure you're running from the correct directory")
    sys.exit(1)


# CLI context and shared utilities
class QuestCLIContext:
    """Shared context for CLI commands"""
    
    def __init__(self):
        self.config_loader = None
        self.quest_service = None
        self.generator_service = None
        self.cache_manager = None
        self._initialized = False
    
    def initialize(self):
        """Initialize services lazily"""
        if self._initialized:
            return
        
        try:
            # Initialize configuration loader
            self.config_loader = QuestConfigLoader()
            
            # Initialize quest generator (only needs config loader)
            self.generator_service = QuestGenerator(self.config_loader)
            
            # Note: QuestBusinessService needs repository dependencies
            # For CLI demo purposes, we'll skip initializing it
            self.quest_service = None
            
            # Initialize cache manager
            self.cache_manager = QuestCacheManager()
            
            self._initialized = True
            
        except Exception as e:
            click.echo(f"Warning: Some quest services unavailable: {e}", err=True)
            # Continue with limited functionality
            self.generator_service = QuestGenerator()  # Without config loader
            self._initialized = True


# Global context
ctx = QuestCLIContext()


def format_quest_output(quest_data: Dict[str, Any], verbose: bool = False) -> str:
    """Format quest data for CLI output"""
    if not quest_data:
        return "No quest data"
    
    output = []
    output.append(f"🎯 Quest: {quest_data.get('title', 'Unknown')}")
    output.append(f"   ID: {quest_data.get('id', 'Unknown')}")
    output.append(f"   Status: {quest_data.get('status', 'Unknown')}")
    output.append(f"   Difficulty: {quest_data.get('difficulty', 'Unknown')}")
    output.append(f"   Theme: {quest_data.get('theme', 'Unknown')}")
    output.append(f"   Level: {quest_data.get('level', 'Unknown')}")
    
    if npc_id := quest_data.get('npc_id'):
        output.append(f"   NPC ID: {npc_id}")
    
    if player_id := quest_data.get('player_id'):
        output.append(f"   Player ID: {player_id}")
    
    if verbose:
        output.append(f"\n   Description: {quest_data.get('description', 'No description')}")
        
        if steps := quest_data.get('steps', []):
            output.append(f"\n   Steps ({len(steps)}):")
            for step in steps:
                status_icon = "✅" if step.get('completed') else "⏸️"
                output.append(f"     {status_icon} {step.get('title', 'Unknown step')}")
        
        if rewards := quest_data.get('rewards', {}):
            output.append(f"\n   Rewards:")
            if gold := rewards.get('gold'):
                output.append(f"     💰 Gold: {gold}")
            if exp := rewards.get('experience'):
                output.append(f"     ⭐ Experience: {exp}")
            if items := rewards.get('items', []):
                output.append(f"     🎁 Items: {len(items)}")
    
    return "\n".join(output)


# Main CLI group
@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def quest_cli(ctx_obj, verbose):
    """Quest System CLI Tools for development and debugging"""
    ctx_obj.ensure_object(dict)
    ctx_obj.obj['verbose'] = verbose
    ctx.initialize()


# Quest management commands
@quest_cli.group()
def quest():
    """Quest management commands"""
    pass


@quest.command('list')
@click.option('--status', '-s', type=click.Choice(['pending', 'active', 'completed', 'failed', 'abandoned', 'expired']),
              help='Filter by quest status')
@click.option('--theme', '-t', type=click.Choice(['combat', 'exploration', 'social', 'mystery', 'crafting', 'trade', 'aid', 'knowledge', 'general']),
              help='Filter by quest theme')
@click.option('--difficulty', '-d', type=click.Choice(['easy', 'medium', 'hard', 'epic']),
              help='Filter by quest difficulty')
@click.option('--player-id', '-p', help='Filter by player ID')
@click.option('--npc-id', '-n', help='Filter by NPC ID')
@click.option('--limit', '-l', type=int, default=20, help='Limit number of results')
@click.pass_context
def list_quests(ctx_obj, status, theme, difficulty, player_id, npc_id, limit):
    """List quests with optional filters"""
    verbose = ctx_obj.obj.get('verbose', False)
    
    click.echo("🔍 Listing quests...")
    
    # Mock quest data for demonstration (replace with actual service call)
    quests = [
        {
            'id': 'quest_001',
            'title': 'Defeat the Dragon',
            'status': 'pending',
            'difficulty': 'epic',
            'theme': 'combat',
            'level': 25,
            'npc_id': 'npc_warrior_001',
            'description': 'A fearsome dragon threatens the village',
            'steps': [
                {'id': 1, 'title': 'Gather information', 'completed': False},
                {'id': 2, 'title': 'Find the dragon\'s lair', 'completed': False},
                {'id': 3, 'title': 'Defeat the dragon', 'completed': False}
            ],
            'rewards': {'gold': 1000, 'experience': 2500, 'items': []}
        }
    ]
    
    # Apply filters (mock implementation)
    if status:
        quests = [q for q in quests if q.get('status') == status]
    if theme:
        quests = [q for q in quests if q.get('theme') == theme]
    if difficulty:
        quests = [q for q in quests if q.get('difficulty') == difficulty]
    if player_id:
        quests = [q for q in quests if q.get('player_id') == player_id]
    if npc_id:
        quests = [q for q in quests if q.get('npc_id') == npc_id]
    
    # Limit results
    quests = quests[:limit]
    
    if not quests:
        click.echo("No quests found matching criteria")
        return
    
    click.echo(f"\nFound {len(quests)} quest(s):\n")
    
    for quest in quests:
        click.echo(format_quest_output(quest, verbose))
        click.echo()


@quest.command('show')
@click.argument('quest_id')
@click.pass_context
def show_quest(ctx_obj, quest_id):
    """Show detailed information about a specific quest"""
    click.echo(f"🔍 Getting quest details for: {quest_id}")
    
    # Mock quest data (replace with actual service call)
    quest_data = {
        'id': quest_id,
        'title': 'Defeat the Dragon',
        'status': 'pending',
        'difficulty': 'epic',
        'theme': 'combat',
        'level': 25,
        'npc_id': 'npc_warrior_001',
        'description': 'A fearsome dragon threatens the village. The local guard captain needs brave adventurers to deal with this threat.',
        'steps': [
            {'id': 1, 'title': 'Gather information about the dragon', 'completed': False, 'description': 'Talk to villagers and gather intelligence'},
            {'id': 2, 'title': 'Find the dragon\'s lair', 'completed': False, 'description': 'Locate the dragon\'s hidden lair in the mountains'},
            {'id': 3, 'title': 'Defeat the dragon', 'completed': False, 'description': 'Face the dragon in epic combat'}
        ],
        'rewards': {
            'gold': 1000,
            'experience': 2500,
            'items': [{'name': 'Dragon Scale Armor', 'rarity': 'legendary'}]
        }
    }
    
    click.echo(format_quest_output(quest_data, verbose=True))


@quest.command('generate')
@click.option('--theme', '-t', type=click.Choice(['combat', 'exploration', 'social', 'mystery', 'crafting', 'trade', 'aid', 'knowledge', 'general']),
              help='Quest theme')
@click.option('--difficulty', '-d', type=click.Choice(['easy', 'medium', 'hard', 'epic']),
              help='Quest difficulty')
@click.option('--level', '-l', type=int, help='Quest level')
@click.option('--npc-id', '-n', help='NPC ID for quest giver')
@click.option('--location-id', '-loc', help='Location ID for quest')
@click.option('--use-template', '-tmp', help='Use specific template ID')
@click.option('--output', '-o', type=click.Path(), help='Save generated quest to file')
@click.pass_context
def generate_quest(ctx_obj, theme, difficulty, level, npc_id, location_id, use_template, output):
    """Generate a new quest using the quest generation system"""
    click.echo("🎲 Generating quest...")
    
    # Prepare context for generation
    context = {}
    if level:
        context['level'] = level
    if location_id:
        context['location_id'] = location_id
    
    # Mock NPC data if provided
    npc_data = {}
    if npc_id:
        npc_data = {
            'id': npc_id,
            'name': f'NPC_{npc_id}',
            'profession': 'warrior',
            'level': level or 10,
            'location_id': location_id
        }
        context['npc'] = npc_data
    
    try:
        if use_template:
            # Generate from specific template
            quest_data = ctx.generator_service.generate_quest_from_template(use_template, context)
        elif theme and difficulty:
            # Generate by theme and difficulty
            theme_enum = QuestTheme(theme)
            difficulty_enum = QuestDifficulty(difficulty)
            quest_data = ctx.generator_service.generate_quest_by_theme(theme_enum, difficulty_enum, context)
        elif npc_data:
            # Generate for NPC
            quest_data = ctx.generator_service.generate_quest_for_npc(npc_data, context)
        else:
            click.echo("Error: Must provide either --theme and --difficulty, --npc-id, or --use-template", err=True)
            return
        
        if quest_data:
            # Convert to dict for display (assuming quest_data is a data class)
            quest_dict = {
                'id': str(quest_data.id),
                'title': quest_data.title,
                'description': quest_data.description,
                'status': quest_data.status.value,
                'difficulty': quest_data.difficulty.value,
                'theme': quest_data.theme.value,
                'level': quest_data.level,
                'npc_id': quest_data.npc_id,
                'steps': [
                    {
                        'id': step.id,
                        'title': step.title,
                        'description': step.description,
                        'completed': step.completed
                    } for step in quest_data.steps
                ],
                'rewards': {
                    'gold': quest_data.rewards.gold,
                    'experience': quest_data.rewards.experience,
                    'items': quest_data.rewards.items
                }
            }
            
            click.echo("✅ Quest generated successfully!\n")
            click.echo(format_quest_output(quest_dict, verbose=True))
            
            if output:
                with open(output, 'w') as f:
                    json.dump(quest_dict, f, indent=2)
                click.echo(f"\n💾 Quest saved to: {output}")
        else:
            click.echo("❌ Failed to generate quest", err=True)
            
    except Exception as e:
        click.echo(f"❌ Error generating quest: {e}", err=True)


# Configuration commands
@quest_cli.group()
def config():
    """Quest configuration management"""
    pass


@config.command('show')
@click.option('--templates', '-t', is_flag=True, help='Show quest templates')
@click.option('--status-flow', '-s', is_flag=True, help='Show status flow configuration')
@click.option('--themes', '-th', is_flag=True, help='Show theme metadata')
def show_config(templates, status_flow, themes):
    """Show quest system configuration"""
    
    if templates:
        click.echo("📋 Quest Templates:")
        try:
            quest_templates = ctx.config_loader.get_quest_templates()
            for template in quest_templates[:5]:  # Show first 5
                click.echo(f"\n  Template: {template.get('id', 'Unknown')}")
                click.echo(f"    Theme: {template.get('theme', 'Unknown')}")
                click.echo(f"    Difficulty: {template.get('difficulty', 'Unknown')}")
                click.echo(f"    Title: {template.get('title', 'Unknown')}")
        except Exception as e:
            click.echo(f"Error loading templates: {e}", err=True)
    
    if status_flow:
        click.echo("🔄 Quest Status Flow:")
        try:
            status_flow_config = ctx.config_loader.get_status_flow()
            for status, transitions in status_flow_config.items():
                click.echo(f"\n  {status} → {', '.join(transitions)}")
        except Exception as e:
            click.echo(f"Error loading status flow: {e}", err=True)
    
    if themes:
        click.echo("🎨 Quest Themes:")
        try:
            themes_config = ctx.config_loader.get_theme_metadata()
            for theme, metadata in themes_config.items():
                click.echo(f"\n  {theme}:")
                click.echo(f"    Description: {metadata.get('description', 'No description')}")
                click.echo(f"    Typical Objectives: {', '.join(metadata.get('typical_objectives', []))}")
        except Exception as e:
            click.echo(f"Error loading themes: {e}", err=True)
    
    if not any([templates, status_flow, themes]):
        click.echo("Please specify what to show: --templates, --status-flow, or --themes")


@config.command('validate')
def validate_config():
    """Validate quest system configuration files"""
    click.echo("🔍 Validating quest configuration...")
    
    try:
        # Test configuration loading
        ctx.config_loader.get_quest_config()
        click.echo("✅ Quest config loaded successfully")
        
        ctx.config_loader.get_quest_templates()
        click.echo("✅ Quest templates loaded successfully")
        
        ctx.config_loader.get_quest_schema()
        click.echo("✅ Quest schema loaded successfully")
        
        click.echo("\n🎉 All configuration files are valid!")
        
    except Exception as e:
        click.echo(f"❌ Configuration validation failed: {e}", err=True)


# Cache management commands
@quest_cli.group()
def cache():
    """Quest cache management"""
    pass


@cache.command('clear')
@click.option('--all', '-a', is_flag=True, help='Clear all cache data')
@click.option('--quest-id', '-q', help='Clear cache for specific quest')
@click.option('--player-id', '-p', help='Clear cache for specific player')
@click.option('--pattern', help='Clear cache entries matching pattern')
def clear_cache(all, quest_id, player_id, pattern):
    """Clear quest system cache"""
    
    if all:
        click.echo("🧹 Clearing all quest cache...")
        ctx.cache_manager.cache.clear_all()
        click.echo("✅ All cache cleared")
    
    elif quest_id:
        click.echo(f"🧹 Clearing cache for quest: {quest_id}")
        ctx.cache_manager.invalidate_quest_cache(quest_id)
        click.echo("✅ Quest cache cleared")
    
    elif player_id:
        click.echo(f"🧹 Clearing cache for player: {player_id}")
        ctx.cache_manager.invalidate_player_cache(player_id)
        click.echo("✅ Player cache cleared")
    
    elif pattern:
        click.echo(f"🧹 Clearing cache matching pattern: {pattern}")
        deleted = ctx.cache_manager.cache.delete_pattern(pattern)
        click.echo(f"✅ Cleared {deleted} cache entries")
    
    else:
        click.echo("Please specify what to clear: --all, --quest-id, --player-id, or --pattern")


@cache.command('stats')
def cache_stats():
    """Show quest cache statistics"""
    click.echo("📊 Quest Cache Statistics:")
    click.echo("  Redis Status: Connected" if ctx.cache_manager.cache.redis_client else "  Redis Status: Not connected")
    click.echo(f"  Memory Cache Entries: {len(ctx.cache_manager.cache.memory_cache)}")
    
    # Show some sample cache keys
    memory_keys = list(ctx.cache_manager.cache.memory_cache.keys())[:10]
    if memory_keys:
        click.echo(f"\n  Sample Cache Keys:")
        for key in memory_keys:
            click.echo(f"    {key}")


# Development utilities
@quest_cli.group()
def dev():
    """Development utilities"""
    pass


@dev.command('test-generation')
@click.option('--count', '-c', type=int, default=5, help='Number of quests to generate')
@click.option('--theme', '-t', type=click.Choice(['combat', 'exploration', 'social', 'mystery', 'crafting', 'trade', 'aid', 'knowledge', 'general']))
def test_generation(count, theme):
    """Test quest generation system"""
    click.echo(f"🧪 Testing quest generation ({count} quests)...")
    
    themes = [theme] if theme else ['combat', 'exploration', 'social', 'mystery', 'crafting']
    difficulties = ['easy', 'medium', 'hard', 'epic']
    
    successful = 0
    failed = 0
    
    for i in range(count):
        try:
            # Pick random theme and difficulty
            import random
            selected_theme = random.choice(themes)
            selected_difficulty = random.choice(difficulties)
            
            # Generate quest
            theme_enum = QuestTheme(selected_theme)
            difficulty_enum = QuestDifficulty(selected_difficulty)
            
            quest_data = ctx.generator_service.generate_quest_by_theme(
                theme_enum, 
                difficulty_enum, 
                {'level': random.randint(1, 50)}
            )
            
            if quest_data:
                click.echo(f"  ✅ Generated: {quest_data.title} ({selected_theme}, {selected_difficulty})")
                successful += 1
            else:
                click.echo(f"  ❌ Failed to generate quest {i+1}")
                failed += 1
                
        except Exception as e:
            click.echo(f"  ❌ Error generating quest {i+1}: {e}")
            failed += 1
    
    click.echo(f"\n📊 Results: {successful} successful, {failed} failed")


@dev.command('mock-data')
@click.option('--quests', '-q', type=int, default=10, help='Number of mock quests to create')
@click.option('--output', '-o', type=click.Path(), help='Output file for mock data')
def generate_mock_data(quests, output):
    """Generate mock quest data for testing"""
    click.echo(f"🎲 Generating {quests} mock quests...")
    
    mock_quests = []
    
    for i in range(quests):
        mock_quest = {
            'id': f'mock_quest_{i+1:03d}',
            'title': f'Mock Quest {i+1}',
            'description': f'This is a mock quest for testing purposes.',
            'status': 'pending',
            'difficulty': ['easy', 'medium', 'hard', 'epic'][i % 4],
            'theme': ['combat', 'exploration', 'social', 'mystery'][i % 4],
            'level': (i % 20) + 1,
            'npc_id': f'npc_{i+1:03d}',
            'created_at': datetime.now().isoformat(),
            'steps': [
                {
                    'id': 1,
                    'title': 'Complete objective',
                    'description': 'Complete the main objective',
                    'completed': False
                }
            ],
            'rewards': {
                'gold': (i + 1) * 50,
                'experience': (i + 1) * 100,
                'items': []
            }
        }
        mock_quests.append(mock_quest)
    
    if output:
        with open(output, 'w') as f:
            json.dump(mock_quests, f, indent=2)
        click.echo(f"✅ Mock data saved to: {output}")
    else:
        click.echo(json.dumps(mock_quests, indent=2))


if __name__ == '__main__':
    quest_cli() 