#!/usr/bin/env python3
"""
Database management script for motif system.

Provides CLI commands for database initialization, migration, and maintenance.
"""

import asyncio
import argparse
import logging
import os
import sys
from typing import Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from alembic import command
from alembic.config import Config

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../..'))
sys.path.insert(0, project_root)

from backend.infrastructure.systems.motif.database.schema import (
    Base, create_tables, drop_tables
)
from backend.infrastructure.systems.motif.models import (
    MotifCreate, MotifCategory, MotifScope, MotifLifecycle
)
from backend.systems.motif.services.service import MotifService
from backend.infrastructure.systems.motif.repositories import MotifRepository

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database operations for motif system."""
    
    def __init__(self, database_url: str):
        """
        Initialize database manager.
        
        Args:
            database_url: Database connection URL
        """
        self.database_url = database_url
        self.engine = create_async_engine(
            database_url,
            echo=False,  # Set to True for SQL debugging
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20
        )
        self.session_factory = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
    
    async def init_database(self) -> None:
        """Initialize database with schema."""
        try:
            logger.info("Creating database schema...")
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database schema created successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def drop_database(self) -> None:
        """Drop all database tables."""
        try:
            logger.info("Dropping database schema...")
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
            logger.info("Database schema dropped successfully")
        except Exception as e:
            logger.error(f"Failed to drop database: {e}")
            raise
    
    async def reset_database(self) -> None:
        """Reset database by dropping and recreating schema."""
        await self.drop_database()
        await self.init_database()
    
    async def generate_sample_data(self) -> None:
        """Generate sample motifs for testing."""
        try:
            logger.info("Generating sample data...")
            
            async with self.session_factory() as session:
                repository = MotifRepository(session)
                service = MotifService(repository)
                
                # Sample motifs
                sample_motifs = [
                    MotifCreate(
                        name="Rising Hope",
                        description="A sense of hope emerges in the darkest times",
                        category=MotifCategory.HOPE,
                        scope=MotifScope.GLOBAL,
                        intensity=6,
                        theme="hope against adversity",
                        descriptors=["inspiring", "uplifting", "resilient"]
                    ),
                    MotifCreate(
                        name="Ancient Mystery",
                        description="Mysterious forces stir in forgotten places",
                        category=MotifCategory.MYSTERY,
                        scope=MotifScope.REGIONAL,
                        intensity=7,
                        theme="ancient secrets",
                        region_id="region_1",
                        descriptors=["enigmatic", "ancient", "hidden"]
                    ),
                    MotifCreate(
                        name="Personal Betrayal",
                        description="Trust is shattered by those closest",
                        category=MotifCategory.BETRAYAL,
                        scope=MotifScope.PLAYER_CHARACTER,
                        intensity=8,
                        theme="broken trust",
                        player_id="player_1",
                        descriptors=["painful", "personal", "devastating"]
                    )
                ]
                
                for motif_data in sample_motifs:
                    motif = await service.create_motif(motif_data)
                    logger.info(f"Created sample motif: {motif.name}")
                
                logger.info(f"Generated {len(sample_motifs)} sample motifs")
                
        except Exception as e:
            logger.error(f"Failed to generate sample data: {e}")
            raise
    
    async def generate_canonical_motifs(self) -> None:
        """Generate the 50 canonical motifs."""
        try:
            logger.info("Generating canonical motifs...")
            
            async with self.session_factory() as session:
                repository = MotifRepository(session)
                service = MotifService(repository)
                
                result = await service.generate_canonical_motifs(force_regenerate=False)
                logger.info(f"Canonical motifs: {result['message']}")
                
        except Exception as e:
            logger.error(f"Failed to generate canonical motifs: {e}")
            raise
    
    async def validate_schema(self) -> bool:
        """Validate database schema integrity."""
        try:
            logger.info("Validating database schema...")
            
            async with self.engine.begin() as conn:
                # Check if main tables exist
                result = await conn.execute(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = 'public' AND table_name IN "
                    "('motifs', 'motif_evolutions', 'motif_conflicts', 'motif_statistics')"
                )
                tables = [row[0] for row in result.fetchall()]
                
                expected_tables = ['motifs', 'motif_evolutions', 'motif_conflicts', 'motif_statistics']
                missing_tables = set(expected_tables) - set(tables)
                
                if missing_tables:
                    logger.error(f"Missing tables: {missing_tables}")
                    return False
                
                # Check if indices exist
                result = await conn.execute(
                    "SELECT indexname FROM pg_indexes "
                    "WHERE tablename IN ('motifs', 'motif_evolutions', 'motif_conflicts', 'motif_statistics')"
                )
                indices = [row[0] for row in result.fetchall()]
                
                # Key indices that should exist
                key_indices = [
                    'idx_motif_category_lifecycle',
                    'idx_motif_scope_intensity',
                    'idx_motif_spatial',
                    'idx_evolution_motif_time',
                    'idx_conflict_unique'
                ]
                
                missing_indices = set(key_indices) - set(indices)
                if missing_indices:
                    logger.warning(f"Missing indices: {missing_indices}")
                
                logger.info("Database schema validation completed")
                return True
                
        except Exception as e:
            logger.error(f"Schema validation failed: {e}")
            return False
    
    async def get_stats(self) -> dict:
        """Get database statistics."""
        try:
            async with self.session_factory() as session:
                repository = MotifRepository(session)
                service = MotifService(repository)
                
                stats = await service.get_motif_statistics()
                return stats
                
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"error": str(e)}
    
    async def cleanup_expired(self) -> int:
        """Clean up expired motifs."""
        try:
            async with self.session_factory() as session:
                repository = MotifRepository(session)
                service = MotifService(repository)
                
                count = await service.cleanup_expired_motifs()
                logger.info(f"Cleaned up {count} expired motifs")
                return count
                
        except Exception as e:
            logger.error(f"Failed to cleanup expired motifs: {e}")
            return 0
    
    async def close(self) -> None:
        """Close database connections."""
        await self.engine.dispose()


def run_alembic_command(cmd: str, *args) -> None:
    """Run Alembic command."""
    try:
        # Get the directory containing this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        alembic_cfg = Config(os.path.join(script_dir, "alembic.ini"))
        
        # Override database URL from environment
        database_url = os.getenv('DATABASE_URL', 'postgresql+asyncpg://user:pass@localhost/motif_db')
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)
        
        if cmd == "upgrade":
            command.upgrade(alembic_cfg, "head")
        elif cmd == "downgrade":
            command.downgrade(alembic_cfg, "-1")
        elif cmd == "revision":
            command.revision(alembic_cfg, autogenerate=True, message=args[0] if args else "Auto-generated")
        elif cmd == "current":
            command.current(alembic_cfg)
        elif cmd == "history":
            command.history(alembic_cfg)
        else:
            logger.error(f"Unknown Alembic command: {cmd}")
            
    except Exception as e:
        logger.error(f"Alembic command failed: {e}")
        raise


async def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Motif System Database Manager")
    parser.add_argument(
        "--database-url",
        default=os.getenv('DATABASE_URL', 'postgresql+asyncpg://user:pass@localhost/motif_db'),
        help="Database connection URL"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Init command
    subparsers.add_parser("init", help="Initialize database schema")
    
    # Drop command
    subparsers.add_parser("drop", help="Drop database schema")
    
    # Reset command
    subparsers.add_parser("reset", help="Reset database (drop and recreate)")
    
    # Sample data command
    subparsers.add_parser("sample", help="Generate sample data")
    
    # Canonical motifs command
    subparsers.add_parser("canonical", help="Generate canonical motifs")
    
    # Validate command
    subparsers.add_parser("validate", help="Validate database schema")
    
    # Stats command
    subparsers.add_parser("stats", help="Show database statistics")
    
    # Cleanup command
    subparsers.add_parser("cleanup", help="Clean up expired motifs")
    
    # Migration commands
    migration_parser = subparsers.add_parser("migrate", help="Database migration commands")
    migration_parser.add_argument("action", choices=["upgrade", "downgrade", "current", "history", "revision"])
    migration_parser.add_argument("--message", "-m", help="Migration message (for revision)")
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if not args.command:
        parser.print_help()
        return
    
    # Handle migration commands separately (they don't need async)
    if args.command == "migrate":
        try:
            if args.action == "revision":
                run_alembic_command("revision", args.message or "Auto-generated migration")
            else:
                run_alembic_command(args.action)
            logger.info(f"Migration command '{args.action}' completed successfully")
        except Exception as e:
            logger.error(f"Migration command failed: {e}")
            sys.exit(1)
        return
    
    # Handle other commands (async)
    db_manager = DatabaseManager(args.database_url)
    
    try:
        if args.command == "init":
            await db_manager.init_database()
        elif args.command == "drop":
            await db_manager.drop_database()
        elif args.command == "reset":
            await db_manager.reset_database()
        elif args.command == "sample":
            await db_manager.generate_sample_data()
        elif args.command == "canonical":
            await db_manager.generate_canonical_motifs()
        elif args.command == "validate":
            is_valid = await db_manager.validate_schema()
            if not is_valid:
                sys.exit(1)
        elif args.command == "stats":
            stats = await db_manager.get_stats()
            print("Database Statistics:")
            print(f"  Total motifs: {stats.get('total_motifs', 'N/A')}")
            print(f"  Active motifs: {stats.get('active_motifs', 'N/A')}")
            print(f"  System health: {stats.get('system_health', 'N/A')}")
        elif args.command == "cleanup":
            count = await db_manager.cleanup_expired()
            print(f"Cleaned up {count} expired motifs")
        
        logger.info(f"Command '{args.command}' completed successfully")
        
    except Exception as e:
        logger.error(f"Command failed: {e}")
        sys.exit(1)
    finally:
        await db_manager.close()


if __name__ == "__main__":
    asyncio.run(main()) 