"""
Data System Management API Router

This module provides comprehensive API endpoints for managing Visual DM's data system,
including validation, migration management, and performance monitoring.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from backend.infrastructure.database import get_db
from backend.infrastructure.validation.data_validation import (
    ValidationService, 
    ValidationResult,
    DataIntegrityChecker
)
from backend.infrastructure.migrations.migration_system import (
    MigrationEngine,
    MigrationTracker,
    PerformanceMonitor as MigrationPerformanceMonitor
)
from backend.infrastructure.monitoring.performance_monitor import (
    PerformanceMonitor,
    QueryTracker,
    TableAnalyzer,
    ConnectionMonitor
)

# Initialize router
router = APIRouter(prefix="/api/data-system", tags=["Data System Management"])
logger = logging.getLogger(__name__)

# Pydantic Models for API Requests/Responses

class ValidationRequest(BaseModel):
    """Request model for entity validation"""
    entity_type: str = Field(..., description="Type of entity to validate (character, region, poi, market, quest)")
    data: Dict[str, Any] = Field(..., description="Entity data to validate")

class BulkValidationRequest(BaseModel):
    """Request model for bulk validation"""
    entities: List[Dict[str, Any]] = Field(..., description="List of entities with entity_type and data fields")

class ValidationResponse(BaseModel):
    """Response model for validation results"""
    is_valid: bool
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    warnings: List[Dict[str, Any]] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class MigrationStatusResponse(BaseModel):
    """Response model for migration status"""
    current_version: Optional[str]
    total_migrations: int
    completed_migrations: int
    pending_migrations: int
    failed_migrations: int
    history: List[Dict[str, Any]]
    database_health: Dict[str, Any]

class PerformanceReportResponse(BaseModel):
    """Response model for performance reports"""
    timestamp: str
    query_performance: Dict[str, Any]
    slow_queries: List[Dict[str, Any]]
    frequent_queries: List[Dict[str, Any]]
    table_analysis: Dict[str, Any]
    connection_health: Dict[str, Any]
    recommendations: List[str]

class SchemaInfoResponse(BaseModel):
    """Response model for schema information"""
    tables: List[Dict[str, Any]]
    total_tables: int
    relationships: List[Dict[str, Any]]
    indexes: List[Dict[str, Any]]

# Validation Endpoints

@router.post("/validate", response_model=ValidationResponse)
async def validate_entity(
    request: ValidationRequest,
    db: Session = Depends(get_db)
):
    """
    Validate a single entity according to Visual DM data standards
    
    **Supported Entity Types:**
    - character: Character entities with stats, abilities, and relationships
    - region: Regional entities with geography and political data
    - poi: Points of interest with location and accessibility data
    - market: Market entities with economic and trading data
    - quest: Quest entities with objectives and narrative elements
    - npc: NPC entities with personality and behavior data
    - faction: Faction entities with political and organizational data
    - event: Event entities with timing and impact data
    """
    try:
        logger.info(f"Validating {request.entity_type} entity")
        
        validation_service = ValidationService(db)
        result = validation_service.validate_entity(request.entity_type, request.data)
        
        return ValidationResponse(
            is_valid=result.is_valid,
            errors=result.errors,
            warnings=result.warnings
        )
    
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

@router.post("/validate/bulk", response_model=Dict[str, ValidationResponse])
async def validate_entities_bulk(
    request: BulkValidationRequest,
    db: Session = Depends(get_db)
):
    """
    Validate multiple entities in a single request
    
    **Request Format:**
    ```json
    {
      "entities": [
        {"entity_type": "character", "data": {...}},
        {"entity_type": "region", "data": {...}}
      ]
    }
    ```
    """
    try:
        logger.info(f"Bulk validating {len(request.entities)} entities")
        
        validation_service = ValidationService(db)
        results = validation_service.bulk_validate(request.entities)
        
        # Convert to API response format
        response = {}
        for i, (entity_id, result) in enumerate(results.items()):
            response[f"entity_{i}"] = ValidationResponse(
                is_valid=result.is_valid,
                errors=result.errors,
                warnings=result.warnings
            )
        
        return response
    
    except Exception as e:
        logger.error(f"Bulk validation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Bulk validation failed: {str(e)}")

@router.get("/validate/integrity", response_model=ValidationResponse)
async def validate_system_integrity(db: Session = Depends(get_db)):
    """
    Perform comprehensive system integrity validation
    
    **Checks Performed:**
    - Referential integrity between related entities
    - Data consistency across systems
    - Constraint validation
    - Orphaned record detection
    """
    try:
        logger.info("Performing system integrity validation")
        
        integrity_checker = DataIntegrityChecker(db)
        
        # Check referential integrity
        ref_result = integrity_checker.check_referential_integrity()
        
        # Check data consistency
        consistency_result = integrity_checker.check_data_consistency()
        
        # Combine results
        combined_errors = ref_result.errors + consistency_result.errors
        combined_warnings = ref_result.warnings + consistency_result.warnings
        
        return ValidationResponse(
            is_valid=len(combined_errors) == 0,
            errors=combined_errors,
            warnings=combined_warnings
        )
    
    except Exception as e:
        logger.error(f"Integrity validation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Integrity validation failed: {str(e)}")

# Migration Management Endpoints

@router.get("/migrations/status", response_model=MigrationStatusResponse)
async def get_migration_status(db: Session = Depends(get_db)):
    """
    Get comprehensive migration status and database health information
    """
    try:
        logger.info("Fetching migration status")
        
        migration_engine = MigrationEngine(db)
        migration_tracker = MigrationTracker(db)
        perf_monitor = MigrationPerformanceMonitor(db)
        
        # Get migration information
        status_info = migration_engine.get_migration_status()
        history = migration_tracker.get_migration_history()
        
        # Get database health
        table_sizes = perf_monitor.check_table_sizes()
        
        return MigrationStatusResponse(
            current_version=status_info.get('current_version'),
            total_migrations=status_info.get('total_migrations', 0),
            completed_migrations=status_info.get('completed_migrations', 0),
            pending_migrations=status_info.get('pending_migrations', 0),
            failed_migrations=status_info.get('failed_migrations', 0),
            history=[{
                'version': m.version,
                'name': m.name,
                'status': m.status.value,
                'execution_time': m.execution_time,
                'created_at': m.created_at.isoformat() if m.created_at else None
            } for m in history],
            database_health={
                'table_sizes': table_sizes,
                'total_tables': len(table_sizes)
            }
        )
    
    except Exception as e:
        logger.error(f"Migration status error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get migration status: {str(e)}")

@router.post("/migrations/execute")
async def execute_migrations(
    background_tasks: BackgroundTasks,
    target_version: Optional[str] = Query(None, description="Target migration version (latest if not specified)"),
    db: Session = Depends(get_db)
):
    """
    Execute pending migrations up to target version
    
    **Note:** This is a long-running operation executed in the background
    """
    try:
        logger.info(f"Executing migrations to version: {target_version or 'latest'}")
        
        def run_migrations():
            try:
                migration_engine = MigrationEngine(db)
                if target_version:
                    success = migration_engine.migrate_to_version(target_version)
                else:
                    success = migration_engine.migrate_to_latest()
                
                if success:
                    logger.info("Migrations completed successfully")
                else:
                    logger.error("Migration execution failed")
            except Exception as e:
                logger.error(f"Background migration error: {str(e)}")
        
        background_tasks.add_task(run_migrations)
        
        return {"message": "Migration execution started", "target_version": target_version}
    
    except Exception as e:
        logger.error(f"Migration execution error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start migration: {str(e)}")

@router.post("/migrations/rollback")
async def rollback_migrations(
    background_tasks: BackgroundTasks,
    target_version: str = Query(..., description="Target version to rollback to"),
    db: Session = Depends(get_db)
):
    """
    Rollback migrations to specified version
    
    **Warning:** This operation may cause data loss
    """
    try:
        logger.info(f"Rolling back migrations to version: {target_version}")
        
        def run_rollback():
            try:
                migration_engine = MigrationEngine(db)
                success = migration_engine.rollback_to_version(target_version)
                
                if success:
                    logger.info(f"Rollback to {target_version} completed successfully")
                else:
                    logger.error(f"Rollback to {target_version} failed")
            except Exception as e:
                logger.error(f"Background rollback error: {str(e)}")
        
        background_tasks.add_task(run_rollback)
        
        return {"message": "Migration rollback started", "target_version": target_version}
    
    except Exception as e:
        logger.error(f"Migration rollback error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start rollback: {str(e)}")

# Performance Monitoring Endpoints

@router.get("/performance/report", response_model=PerformanceReportResponse)
async def get_performance_report(db: Session = Depends(get_db)):
    """
    Get comprehensive performance analysis report
    
    **Includes:**
    - Query performance metrics
    - Slow query analysis
    - Table size and growth analysis
    - Connection pool health
    - Optimization recommendations
    """
    try:
        logger.info("Generating performance report")
        
        performance_monitor = PerformanceMonitor(db)
        query_tracker = QueryTracker()
        table_analyzer = TableAnalyzer(db)
        connection_monitor = ConnectionMonitor()
        
        # Get comprehensive data
        report = performance_monitor.get_comprehensive_report()
        slow_queries = query_tracker.get_slow_queries(threshold_ms=100.0)
        frequent_queries = query_tracker.get_frequent_queries(min_count=5)
        table_metrics = table_analyzer.get_table_metrics()
        connection_health = connection_monitor.get_connection_health()
        
        return PerformanceReportResponse(
            timestamp=datetime.now().isoformat(),
            query_performance=report.get('query_performance', {}),
            slow_queries=[{
                'query_hash': q.query_hash,
                'query_text': q.query_text[:200] + '...' if len(q.query_text) > 200 else q.query_text,
                'execution_count': q.execution_count,
                'avg_time': round(q.avg_time * 1000, 2),  # Convert to ms
                'max_time': round(q.max_time * 1000, 2),
                'table_names': q.table_names,
                'operation_type': q.operation_type
            } for q in slow_queries[:10]],
            frequent_queries=[{
                'query_hash': q.query_hash,
                'query_text': q.query_text[:200] + '...' if len(q.query_text) > 200 else q.query_text,
                'execution_count': q.execution_count,
                'avg_time': round(q.avg_time * 1000, 2),
                'table_names': q.table_names,
                'operation_type': q.operation_type
            } for q in frequent_queries[:10]],
            table_analysis={
                'tables': [{
                    'name': t.table_name,
                    'row_count': t.row_count,
                    'size_pretty': t.size_pretty,
                    'index_count': t.index_count,
                    'seq_scans': t.seq_scans,
                    'idx_scans': t.idx_scans
                } for t in table_metrics],
                'total_size': sum(t.size_bytes for t in table_metrics)
            },
            connection_health=connection_health,
            recommendations=report.get('recommendations', [])
        )
    
    except Exception as e:
        logger.error(f"Performance report error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate performance report: {str(e)}")

@router.get("/performance/metrics")
async def get_real_time_metrics(db: Session = Depends(get_db)):
    """
    Get real-time performance metrics
    
    **Returns:**
    - Current query rate
    - Active connections
    - Database size
    - Memory usage
    """
    try:
        logger.info("Fetching real-time metrics")
        
        performance_monitor = PerformanceMonitor(db)
        metrics = performance_monitor.get_real_time_metrics()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "status": "healthy" if metrics.get('connection_utilization', 0) < 0.8 else "warning"
        }
    
    except Exception as e:
        logger.error(f"Real-time metrics error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get real-time metrics: {str(e)}")

@router.get("/performance/slow-queries")
async def get_slow_queries(
    threshold_ms: float = Query(100.0, description="Threshold in milliseconds for slow queries"),
    limit: int = Query(10, description="Maximum number of queries to return"),
    db: Session = Depends(get_db)
):
    """
    Get analysis of slow queries for optimization
    
    **Query Analysis Includes:**
    - Execution frequency
    - Average and maximum execution time
    - Affected tables
    - Operation type (SELECT, INSERT, UPDATE, DELETE)
    - Optimization suggestions
    """
    try:
        logger.info(f"Analyzing slow queries (threshold: {threshold_ms}ms)")
        
        query_tracker = QueryTracker()
        slow_queries = query_tracker.get_slow_queries(threshold_ms=threshold_ms)
        
        # Generate optimization suggestions
        suggestions = []
        for query in slow_queries[:limit]:
            query_suggestions = []
            
            # Suggest indexes for SELECT queries with many table scans
            if query.operation_type == 'SELECT' and len(query.table_names) > 1:
                query_suggestions.append("Consider adding composite indexes for JOIN operations")
            
            # Suggest query optimization for frequently executed slow queries
            if query.execution_count > 10:
                query_suggestions.append("High frequency query - consider caching or optimization")
            
            # Suggest connection pooling for many small queries
            if query.avg_time < 0.01 and query.execution_count > 100:
                query_suggestions.append("Many small queries - consider batching operations")
            
            suggestions.append({
                'query_hash': query.query_hash,
                'suggestions': query_suggestions
            })
        
        return {
            "threshold_ms": threshold_ms,
            "total_slow_queries": len(slow_queries),
            "slow_queries": [{
                'query_hash': q.query_hash,
                'query_text': q.query_text[:500] + '...' if len(q.query_text) > 500 else q.query_text,
                'execution_count': q.execution_count,
                'avg_time_ms': round(q.avg_time * 1000, 2),
                'max_time_ms': round(q.max_time * 1000, 2),
                'min_time_ms': round(q.min_time * 1000, 2),
                'median_time_ms': round(q.median_time * 1000, 2),
                'total_time_ms': round(q.total_time * 1000, 2),
                'table_names': q.table_names,
                'operation_type': q.operation_type,
                'last_executed': q.last_executed.isoformat()
            } for q in slow_queries[:limit]],
            "optimization_suggestions": suggestions
        }
    
    except Exception as e:
        logger.error(f"Slow query analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze slow queries: {str(e)}")

@router.get("/performance/table-analysis")
async def get_table_analysis(db: Session = Depends(get_db)):
    """
    Get detailed table analysis and growth patterns
    """
    try:
        logger.info("Performing table analysis")
        
        table_analyzer = TableAnalyzer(db)
        metrics = table_analyzer.get_table_metrics()
        growth_analysis = table_analyzer.get_growth_analysis(days=30)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "table_metrics": [{
                'table_name': m.table_name,
                'row_count': m.row_count,
                'size_bytes': m.size_bytes,
                'size_pretty': m.size_pretty,
                'index_count': m.index_count,
                'last_vacuum': m.last_vacuum.isoformat() if m.last_vacuum else None,
                'last_analyze': m.last_analyze.isoformat() if m.last_analyze else None,
                'seq_scans': m.seq_scans,
                'seq_tup_read': m.seq_tup_read,
                'idx_scans': m.idx_scans,
                'idx_tup_fetch': m.idx_tup_fetch
            } for m in metrics],
            "growth_analysis": growth_analysis,
            "total_database_size": sum(m.size_bytes for m in metrics),
            "total_tables": len(metrics)
        }
    
    except Exception as e:
        logger.error(f"Table analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to perform table analysis: {str(e)}")

@router.get("/performance/connection-health")
async def get_connection_health(db: Session = Depends(get_db)):
    """
    Get database connection pool health and recommendations
    """
    try:
        logger.info("Checking connection health")
        
        connection_monitor = ConnectionMonitor()
        health_info = connection_monitor.get_connection_health()
        
        # Add status determination
        utilization = health_info.get('utilization', 0)
        if utilization < 0.5:
            status = "healthy"
        elif utilization < 0.8:
            status = "warning"
        else:
            status = "critical"
        
        return {
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "connection_health": health_info
        }
    
    except Exception as e:
        logger.error(f"Connection health check error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to check connection health: {str(e)}")

# Schema Information Endpoints

@router.get("/schema/tables")
async def get_table_schema_info(db: Session = Depends(get_db)):
    """
    Get comprehensive schema information for all tables
    
    **Includes:**
    - Table structure and column definitions
    - Primary and foreign key relationships
    - Index information
    - Constraint details
    """
    try:
        logger.info("Fetching table schema information")
        
        # Get table information from PostgreSQL system catalogs
        table_query = """
        SELECT 
            t.table_name,
            t.table_type,
            c.column_name,
            c.data_type,
            c.is_nullable,
            c.column_default,
            c.character_maximum_length,
            c.numeric_precision,
            c.numeric_scale
        FROM information_schema.tables t
        LEFT JOIN information_schema.columns c ON t.table_name = c.table_name
        WHERE t.table_schema = 'public' 
        AND t.table_type = 'BASE TABLE'
        ORDER BY t.table_name, c.ordinal_position;
        """
        
        result = db.execute(table_query).fetchall()
        
        # Organize data by table
        tables = {}
        for row in result:
            table_name = row[0]
            if table_name not in tables:
                tables[table_name] = {
                    'name': table_name,
                    'type': row[1],
                    'columns': []
                }
            
            if row[2]:  # If column_name exists
                tables[table_name]['columns'].append({
                    'name': row[2],
                    'data_type': row[3],
                    'nullable': row[4] == 'YES',
                    'default': row[5],
                    'max_length': row[6],
                    'precision': row[7],
                    'scale': row[8]
                })
        
        # Get index information
        index_query = """
        SELECT 
            schemaname,
            tablename,
            indexname,
            indexdef
        FROM pg_indexes 
        WHERE schemaname = 'public'
        ORDER BY tablename, indexname;
        """
        
        index_result = db.execute(index_query).fetchall()
        indexes = [{'table': row[1], 'name': row[2], 'definition': row[3]} for row in index_result]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "tables": list(tables.values()),
            "total_tables": len(tables),
            "indexes": indexes,
            "total_indexes": len(indexes)
        }
    
    except Exception as e:
        logger.error(f"Schema information error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get schema information: {str(e)}")

@router.get("/schema/relationships")
async def get_table_relationships(db: Session = Depends(get_db)):
    """
    Get foreign key relationships between tables
    """
    try:
        logger.info("Fetching table relationships")
        
        # Get foreign key relationships
        fk_query = """
        SELECT
            tc.table_name AS source_table,
            kcu.column_name AS source_column,
            ccu.table_name AS target_table,
            ccu.column_name AS target_column,
            tc.constraint_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage ccu
            ON ccu.constraint_name = tc.constraint_name
            AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
        AND tc.table_schema = 'public'
        ORDER BY tc.table_name;
        """
        
        result = db.execute(fk_query).fetchall()
        
        relationships = [{
            'source_table': row[0],
            'source_column': row[1],
            'target_table': row[2],
            'target_column': row[3],
            'constraint_name': row[4]
        } for row in result]
        
        # Create relationship summary
        relationship_summary = {}
        for rel in relationships:
            source = rel['source_table']
            target = rel['target_table']
            
            if source not in relationship_summary:
                relationship_summary[source] = {'references': [], 'referenced_by': []}
            if target not in relationship_summary:
                relationship_summary[target] = {'references': [], 'referenced_by': []}
            
            relationship_summary[source]['references'].append(target)
            relationship_summary[target]['referenced_by'].append(source)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "relationships": relationships,
            "total_relationships": len(relationships),
            "relationship_summary": relationship_summary
        }
    
    except Exception as e:
        logger.error(f"Relationship information error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get relationship information: {str(e)}")

# Health Check Endpoint

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Comprehensive health check for the data system
    
    **Checks:**
    - Database connectivity
    - Migration status
    - Performance thresholds
    - System integrity
    """
    try:
        logger.info("Performing health check")
        
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",
            "checks": {}
        }
        
        # Database connectivity check
        try:
            db.execute("SELECT 1")
            health_status["checks"]["database_connectivity"] = {"status": "pass", "message": "Database connection successful"}
        except Exception as e:
            health_status["checks"]["database_connectivity"] = {"status": "fail", "message": f"Database connection failed: {str(e)}"}
            health_status["status"] = "unhealthy"
        
        # Migration status check
        try:
            migration_engine = MigrationEngine(db)
            migration_status = migration_engine.get_migration_status()
            pending_count = migration_status.get('pending_migrations', 0)
            
            if pending_count == 0:
                health_status["checks"]["migrations"] = {"status": "pass", "message": "All migrations up to date"}
            else:
                health_status["checks"]["migrations"] = {"status": "warning", "message": f"{pending_count} pending migrations"}
                if health_status["status"] == "healthy":
                    health_status["status"] = "warning"
        except Exception as e:
            health_status["checks"]["migrations"] = {"status": "fail", "message": f"Migration check failed: {str(e)}"}
            health_status["status"] = "unhealthy"
        
        # Performance check
        try:
            connection_monitor = ConnectionMonitor()
            conn_health = connection_monitor.get_connection_health()
            utilization = conn_health.get('utilization', 0)
            
            if utilization < 0.8:
                health_status["checks"]["performance"] = {"status": "pass", "message": f"Connection utilization: {utilization:.1%}"}
            else:
                health_status["checks"]["performance"] = {"status": "warning", "message": f"High connection utilization: {utilization:.1%}"}
                if health_status["status"] == "healthy":
                    health_status["status"] = "warning"
        except Exception as e:
            health_status["checks"]["performance"] = {"status": "fail", "message": f"Performance check failed: {str(e)}"}
            health_status["status"] = "unhealthy"
        
        # System integrity check (lightweight version)
        try:
            # Just check if core tables exist
            core_tables = ['region_entities', 'character_entities', 'poi_entities']
            missing_tables = []
            
            for table in core_tables:
                try:
                    db.execute(f"SELECT 1 FROM {table} LIMIT 1")
                except Exception:
                    missing_tables.append(table)
            
            if not missing_tables:
                health_status["checks"]["system_integrity"] = {"status": "pass", "message": "Core tables present"}
            else:
                health_status["checks"]["system_integrity"] = {"status": "fail", "message": f"Missing tables: {missing_tables}"}
                health_status["status"] = "unhealthy"
        except Exception as e:
            health_status["checks"]["system_integrity"] = {"status": "fail", "message": f"Integrity check failed: {str(e)}"}
            health_status["status"] = "unhealthy"
        
        return health_status
    
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return {
            "timestamp": datetime.now().isoformat(),
            "status": "unhealthy",
            "error": str(e)
        }

# Export router for use in main application
__all__ = ["router"] 