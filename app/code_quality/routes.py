"""
Code quality analysis routes.
"""

from flask import Blueprint, jsonify, request, current_app
from app.code_quality.service import CodeQualityService
from app.core.auth import login_required
from flasgger import swag_from
from app.core.schemas.code_analysis_schemas import (
    CodeQualityMetricsSchema,
    SecurityIssueSchema,
    ErrorResponseSchema
)

code_quality_bp = Blueprint('code_quality', __name__, url_prefix='/api/v1/code-quality')

@code_quality_bp.route('/analyze', methods=['POST'])
@login_required
@swag_from({
    'tags': ['code-quality'],
    'summary': 'Analyze code quality',
    'description': 'Analyze the codebase and return code quality metrics',
    'parameters': [
        {
            'name': 'path',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Path to analyze (defaults to entire codebase)'
        }
    ],
    'responses': {
        '200': {
            'description': 'Code quality analysis completed successfully',
            'schema': CodeQualityMetricsSchema
        },
        '400': {
            'description': 'Invalid request parameters',
            'schema': ErrorResponseSchema
        },
        '500': {
            'description': 'Server error',
            'schema': ErrorResponseSchema
        }
    },
    'security': [
        {
            'Bearer': []
        }
    ]
})
def analyze_code():
    """Analyze code quality for the specified path."""
    try:
        path = request.args.get('path', '.')
        service = CodeQualityService()
        metrics = service.analyze_codebase(path)
        return jsonify(metrics.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@code_quality_bp.route('/security/scan', methods=['POST'])
@login_required
@swag_from({
    'tags': ['code-quality'],
    'summary': 'Scan for security issues',
    'description': 'Perform a security scan of the codebase',
    'parameters': [
        {
            'name': 'scan_type',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Type of scan to perform (code, vulnerability, or all)',
            'enum': ['code', 'vulnerability', 'all'],
            'default': 'all'
        }
    ],
    'responses': {
        '200': {
            'description': 'Security scan completed successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'issues': {
                        'type': 'array',
                        'items': SecurityIssueSchema
                    }
                }
            }
        },
        '400': {
            'description': 'Invalid request parameters',
            'schema': ErrorResponseSchema
        },
        '500': {
            'description': 'Server error',
            'schema': ErrorResponseSchema
        }
    },
    'security': [
        {
            'Bearer': []
        }
    ]
})
def scan_security():
    """Perform a security scan."""
    try:
        scan_type = request.args.get('scan_type', 'all')
        security_manager = current_app.extensions.get('security_manager')
        
        if not security_manager:
            return jsonify({'error': 'Security manager not enabled'}), 503
            
        issues = []
        if scan_type in ['code', 'all']:
            issues.extend(security_manager.scan_code())
        if scan_type in ['vulnerability', 'all']:
            issues.extend(security_manager.scan_vulnerabilities())
            
        return jsonify({
            'issues': [issue.to_dict() for issue in issues]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500 