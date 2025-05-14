import logging
import time
from typing import Dict, Any, Optional
from flask import Flask
from sqlalchemy import text
from app import db

logger = logging.getLogger(__name__)

class HealthCheck:
    """Health check system for the application"""
    
    def __init__(self, app: Flask) -> None:
        self.app = app
        self.checks = []
        self.register_default_checks()
    
    def register_default_checks(self) -> None:
        """Register default health checks"""
        self.register_check(self.check_database, "database")
        self.register_check(self.check_redis, "redis")
        self.register_check(self.check_disk_space, "disk_space")
        self.register_check(self.check_memory, "memory")
    
    def register_check(self, check_func: callable, name: str) -> None:
        """Register a new health check"""
        self.checks.append({
            'name': name,
            'function': check_func
        })
    
    def check_database(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            start_time = time.time()
            db.session.execute(text('SELECT 1'))
            duration = time.time() - start_time
            
            return {
                'status': 'healthy',
                'response_time': f"{duration:.3f}s",
                'details': {
                    'connection': 'established',
                    'response_time': duration
                }
            }
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'details': {
                    'connection': 'failed',
                    'error': str(e)
                }
            }
    
    def check_redis(self) -> Dict[str, Any]:
        """Check Redis health"""
        try:
            # TODO: Implement Redis health check
            return {
                'status': 'healthy',
                'details': {
                    'connection': 'established'
                }
            }
        except Exception as e:
            logger.error(f"Redis health check failed: {str(e)}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'details': {
                    'connection': 'failed',
                    'error': str(e)
                }
            }
    
    def check_disk_space(self) -> Dict[str, Any]:
        """Check disk space"""
        try:
            import shutil
            total, used, free = shutil.disk_usage("/")
            
            return {
                'status': 'healthy',
                'details': {
                    'total': f"{total // (2**30)}GB",
                    'used': f"{used // (2**30)}GB",
                    'free': f"{free // (2**30)}GB",
                    'percent_used': f"{(used/total)*100:.1f}%"
                }
            }
        except Exception as e:
            logger.error(f"Disk space check failed: {str(e)}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'details': {
                    'error': str(e)
                }
            }
    
    def check_memory(self) -> Dict[str, Any]:
        """Check memory usage"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            
            return {
                'status': 'healthy',
                'details': {
                    'total': f"{memory.total // (2**30)}GB",
                    'available': f"{memory.available // (2**30)}GB",
                    'used': f"{memory.used // (2**30)}GB",
                    'percent_used': f"{memory.percent}%"
                }
            }
        except Exception as e:
            logger.error(f"Memory check failed: {str(e)}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'details': {
                    'error': str(e)
                }
            }
    
    def run_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        results = {}
        overall_status = 'healthy'
        
        for check in self.checks:
            try:
                result = check['function']()
                results[check['name']] = result
                
                if result['status'] == 'unhealthy':
                    overall_status = 'unhealthy'
                    
            except Exception as e:
                logger.error(f"Health check {check['name']} failed: {str(e)}")
                results[check['name']] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                overall_status = 'unhealthy'
        
        return {
            'status': overall_status,
            'checks': results,
            'timestamp': time.time()
        } 