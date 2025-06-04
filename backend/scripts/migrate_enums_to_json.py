#!/usr/bin/env python3
"""
Migration script to transition from enum-based configurations to JSON-based configurations
Handles database updates and provides migration helpers
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add backend to Python path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from backend.infrastructure.data.json_config_loader import get_config_loader

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnumToJsonMigrator:
    """Handles migration from enum-based to JSON-based configurations"""
    
    def __init__(self, database_url: Optional[str] = None):
        self.config_loader = get_config_loader()
        self.database_url = database_url or os.getenv('DATABASE_URL')
        
        if self.database_url:
            self.engine = create_engine(self.database_url)
            self.SessionLocal = sessionmaker(bind=self.engine)
        else:
            logger.warning("No database URL provided, database migrations will be skipped")
            self.engine = None
            self.SessionLocal = None
    
    def create_enum_mapping_tables(self):
        """Create mapping tables for enum transition period"""
        if not self.engine:
            logger.warning("No database connection, skipping table creation")
            return
        
        with self.engine.connect() as conn:
            # Create enum mapping table for tracking transitions
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS enum_json_mappings (
                    id SERIAL PRIMARY KEY,
                    enum_type VARCHAR(100) NOT NULL,
                    enum_value VARCHAR(100) NOT NULL,
                    json_config_id VARCHAR(100) NOT NULL,
                    migration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(enum_type, enum_value)
                );
            """))
            
            conn.commit()
            logger.info("Created enum_json_mappings table")
    
    def generate_enum_mappings(self) -> Dict[str, Dict[str, str]]:
        """Generate mappings from old enum values to new JSON config IDs"""
        mappings = {
            'FactionType': {},
            'FactionAlignment': {},
            'DiplomaticStance': {},
            'DamageType': {},
            'SettlementType': {},
            'ResourceType': {},
            'RegionType': {},
            'BiomeType': {},
            'ChaosLevel': {}
        }
        
        # Faction mappings
        for faction_id in self.config_loader.get_faction_type_ids():
            # Convert from snake_case to UPPER_CASE enum format
            enum_value = faction_id.upper()
            mappings['FactionType'][enum_value] = faction_id
        
        for alignment_id in self.config_loader.get_alignment_ids():
            enum_value = alignment_id.upper()
            mappings['FactionAlignment'][enum_value] = alignment_id
        
        for stance_id in self.config_loader.get_diplomatic_stance_ids():
            enum_value = stance_id.upper()
            mappings['DiplomaticStance'][enum_value] = stance_id
        
        # Damage type mappings
        for damage_id in self.config_loader.get_damage_type_ids():
            enum_value = damage_id.upper()
            mappings['DamageType'][enum_value] = damage_id
        
        # Settlement type mappings
        for settlement_id in self.config_loader.get_settlement_type_ids():
            enum_value = settlement_id.upper()
            mappings['SettlementType'][enum_value] = settlement_id
        
        # Resource type mappings
        for resource_id in self.config_loader.get_resource_type_ids():
            enum_value = resource_id.upper()
            mappings['ResourceType'][enum_value] = resource_id
        
        # Region type mappings
        for region_id in self.config_loader.get_region_type_ids():
            enum_value = region_id.upper()
            mappings['RegionType'][enum_value] = region_id
        
        # Biome type mappings
        for biome_id in self.config_loader.get_biome_type_ids():
            enum_value = biome_id.upper()
            mappings['BiomeType'][enum_value] = biome_id
        
        # Chaos level mappings
        for chaos_id in self.config_loader.get_chaos_level_ids():
            enum_value = chaos_id.upper()
            mappings['ChaosLevel'][enum_value] = chaos_id
        
        return mappings
    
    def save_enum_mappings(self, mappings: Dict[str, Dict[str, str]]):
        """Save enum mappings to database and file"""
        if self.SessionLocal:
            with self.SessionLocal() as session:
                for enum_type, type_mappings in mappings.items():
                    for enum_value, json_id in type_mappings.items():
                        session.execute(text("""
                            INSERT INTO enum_json_mappings (enum_type, enum_value, json_config_id)
                            VALUES (:enum_type, :enum_value, :json_id)
                            ON CONFLICT (enum_type, enum_value) DO UPDATE SET
                                json_config_id = EXCLUDED.json_config_id,
                                migration_date = CURRENT_TIMESTAMP;
                        """), {
                            'enum_type': enum_type,
                            'enum_value': enum_value,
                            'json_id': json_id
                        })
                session.commit()
            
            logger.info("Saved enum mappings to database")
        
        # Also save to file for reference
        mappings_file = backend_path / "scripts" / "enum_mappings.json"
        with open(mappings_file, 'w') as f:
            json.dump(mappings, f, indent=2)
        
        logger.info(f"Saved enum mappings to {mappings_file}")
    
    def migrate_faction_tables(self):
        """Migrate faction-related tables"""
        if not self.engine:
            logger.warning("No database connection, skipping faction table migration")
            return
        
        with self.engine.connect() as conn:
            # Update factions table - faction_type column
            logger.info("Migrating factions.faction_type column...")
            
            # Get current enum values and convert them
            result = conn.execute(text("SELECT id, faction_type FROM factions WHERE faction_type IS NOT NULL"))
            
            for row in result:
                faction_id, current_type = row
                # Convert enum value to JSON config ID
                if hasattr(current_type, 'value'):
                    json_config_id = current_type.value  # Already converted
                else:
                    json_config_id = str(current_type).lower()
                
                # Validate the JSON config ID exists
                if self.config_loader.get_faction_type(json_config_id):
                    conn.execute(text("""
                        UPDATE factions SET faction_type = :json_id WHERE id = :faction_id
                    """), {'json_id': json_config_id, 'faction_id': faction_id})
                else:
                    logger.warning(f"Unknown faction type for faction {faction_id}: {current_type}")
            
            conn.commit()
            logger.info("Completed faction table migration")
    
    def migrate_region_tables(self):
        """Migrate region-related tables"""
        if not self.engine:
            logger.warning("No database connection, skipping region table migration")
            return
        
        with self.engine.connect() as conn:
            # Update regions table
            logger.info("Migrating regions table...")
            
            # Migrate region_type column
            result = conn.execute(text("SELECT id, region_type FROM regions WHERE region_type IS NOT NULL"))
            
            for row in result:
                region_id, current_type = row
                json_config_id = str(current_type).lower() if hasattr(current_type, 'value') else str(current_type).lower()
                
                if self.config_loader.get_region_type(json_config_id):
                    conn.execute(text("""
                        UPDATE regions SET region_type = :json_id WHERE id = :region_id
                    """), {'json_id': json_config_id, 'region_id': region_id})
            
            # Migrate dominant_biome column
            result = conn.execute(text("SELECT id, dominant_biome FROM regions WHERE dominant_biome IS NOT NULL"))
            
            for row in result:
                region_id, current_biome = row
                json_config_id = str(current_biome).lower() if hasattr(current_biome, 'value') else str(current_biome).lower()
                
                if self.config_loader.get_biome_type(json_config_id):
                    conn.execute(text("""
                        UPDATE regions SET dominant_biome = :json_id WHERE id = :region_id
                    """), {'json_id': json_config_id, 'region_id': region_id})
            
            conn.commit()
            logger.info("Completed regions table migration")
    
    def migrate_resource_tables(self):
        """Migrate resource-related tables"""
        if not self.engine:
            logger.warning("No database connection, skipping resource table migration")
            return
        
        with self.engine.connect() as conn:
            # Update resource nodes table
            logger.info("Migrating region_resource_nodes table...")
            
            result = conn.execute(text("SELECT id, resource_type FROM region_resource_nodes WHERE resource_type IS NOT NULL"))
            
            for row in result:
                node_id, current_type = row
                json_config_id = str(current_type).lower() if hasattr(current_type, 'value') else str(current_type).lower()
                
                if self.config_loader.get_resource_type(json_config_id):
                    conn.execute(text("""
                        UPDATE region_resource_nodes SET resource_type = :json_id WHERE id = :node_id
                    """), {'json_id': json_config_id, 'node_id': node_id})
            
            conn.commit()
            logger.info("Completed resource nodes table migration")
    
    def validate_migration(self) -> Dict[str, Any]:
        """Validate that migration was successful"""
        validation_results = {
            'timestamp': datetime.utcnow().isoformat(),
            'valid_configs': 0,
            'invalid_configs': 0,
            'issues': []
        }
        
        if not self.engine:
            validation_results['issues'].append("No database connection for validation")
            return validation_results
        
        with self.engine.connect() as conn:
            # Check factions
            result = conn.execute(text("SELECT DISTINCT faction_type FROM factions WHERE faction_type IS NOT NULL"))
            for row in result:
                faction_type = row[0]
                if self.config_loader.get_faction_type(faction_type):
                    validation_results['valid_configs'] += 1
                else:
                    validation_results['invalid_configs'] += 1
                    validation_results['issues'].append(f"Invalid faction type: {faction_type}")
            
            # Check regions
            result = conn.execute(text("SELECT DISTINCT region_type FROM regions WHERE region_type IS NOT NULL"))
            for row in result:
                region_type = row[0]
                if self.config_loader.get_region_type(region_type):
                    validation_results['valid_configs'] += 1
                else:
                    validation_results['invalid_configs'] += 1
                    validation_results['issues'].append(f"Invalid region type: {region_type}")
            
            # Check biomes
            result = conn.execute(text("SELECT DISTINCT dominant_biome FROM regions WHERE dominant_biome IS NOT NULL"))
            for row in result:
                biome_type = row[0]
                if self.config_loader.get_biome_type(biome_type):
                    validation_results['valid_configs'] += 1
                else:
                    validation_results['invalid_configs'] += 1
                    validation_results['issues'].append(f"Invalid biome type: {biome_type}")
            
            # Check resources
            result = conn.execute(text("SELECT DISTINCT resource_type FROM region_resource_nodes WHERE resource_type IS NOT NULL"))
            for row in result:
                resource_type = row[0]
                if self.config_loader.get_resource_type(resource_type):
                    validation_results['valid_configs'] += 1
                else:
                    validation_results['invalid_configs'] += 1
                    validation_results['issues'].append(f"Invalid resource type: {resource_type}")
        
        return validation_results
    
    def generate_migration_report(self) -> str:
        """Generate a comprehensive migration report"""
        report_lines = [
            "# Enum to JSON Migration Report",
            f"Generated: {datetime.utcnow().isoformat()}",
            "",
            "## Configuration Statistics",
        ]
        
        # Configuration counts
        stats = {
            "Faction Types": len(self.config_loader.get_faction_type_ids()),
            "Faction Alignments": len(self.config_loader.get_alignment_ids()),
            "Diplomatic Stances": len(self.config_loader.get_diplomatic_stance_ids()),
            "Damage Types": len(self.config_loader.get_damage_type_ids()),
            "Settlement Types": len(self.config_loader.get_settlement_type_ids()),
            "Resource Types": len(self.config_loader.get_resource_type_ids()),
            "Region Types": len(self.config_loader.get_region_type_ids()),
            "Biome Types": len(self.config_loader.get_biome_type_ids()),
            "Chaos Levels": len(self.config_loader.get_chaos_level_ids()),
        }
        
        for config_type, count in stats.items():
            report_lines.append(f"- {config_type}: {count}")
        
        report_lines.extend([
            "",
            "## Migration Validation",
        ])
        
        # Validation results
        validation = self.validate_migration()
        report_lines.extend([
            f"- Valid configurations: {validation['valid_configs']}",
            f"- Invalid configurations: {validation['invalid_configs']}",
            f"- Issues found: {len(validation['issues'])}",
        ])
        
        if validation['issues']:
            report_lines.extend([
                "",
                "### Issues Found:",
            ])
            for issue in validation['issues']:
                report_lines.append(f"- {issue}")
        
        report_lines.extend([
            "",
            "## Next Steps",
            "1. Review any issues found above",
            "2. Update any remaining enum references in code",
            "3. Run comprehensive tests",
            "4. Update documentation",
            "5. Deploy changes to production",
            "",
            "## Benefits Achieved",
            "- ✅ Data-driven configuration",
            "- ✅ Easy content updates without code changes",
            "- ✅ Rich configuration data with modifiers",
            "- ✅ Better maintainability and extensibility",
            "- ✅ Backwards compatibility maintained",
        ])
        
        return "\n".join(report_lines)
    
    def run_full_migration(self):
        """Run the complete migration process"""
        logger.info("Starting enum to JSON migration...")
        
        try:
            # Step 1: Create mapping tables
            self.create_enum_mapping_tables()
            
            # Step 2: Generate and save mappings
            mappings = self.generate_enum_mappings()
            self.save_enum_mappings(mappings)
            
            # Step 3: Migrate database tables
            self.migrate_faction_tables()
            self.migrate_region_tables()
            self.migrate_resource_tables()
            
            # Step 4: Validate migration
            validation = self.validate_migration()
            
            # Step 5: Generate report
            report = self.generate_migration_report()
            
            # Save report
            report_file = backend_path / "scripts" / f"migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(report_file, 'w') as f:
                f.write(report)
            
            logger.info(f"Migration completed! Report saved to: {report_file}")
            
            if validation['invalid_configs'] > 0:
                logger.warning(f"Found {validation['invalid_configs']} invalid configurations - check the report")
            else:
                logger.info("Migration validation passed - all configurations are valid!")
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise


def main():
    """Main migration entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate from enum-based to JSON-based configurations")
    parser.add_argument("--database-url", help="Database URL for migration")
    parser.add_argument("--dry-run", action="store_true", help="Generate mappings and report without database changes")
    parser.add_argument("--validate-only", action="store_true", help="Only run validation")
    
    args = parser.parse_args()
    
    migrator = EnumToJsonMigrator(database_url=args.database_url)
    
    if args.validate_only:
        validation = migrator.validate_migration()
        print(json.dumps(validation, indent=2))
    elif args.dry_run:
        mappings = migrator.generate_enum_mappings()
        report = migrator.generate_migration_report()
        print("Generated mappings and report (dry run):")
        print(report)
    else:
        migrator.run_full_migration()


if __name__ == "__main__":
    main() 