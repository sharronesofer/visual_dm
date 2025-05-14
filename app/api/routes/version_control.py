"""
API endpoints for version control operations.
"""

from typing import Dict, Any, List
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import os
from app.core.services.version_control_service import VersionControlService
from app.core.services.git_service import GitService
from app.core.exceptions import VersionControlError
from app.core.auth import login_required
from app.core.utils.validation import validate_request
from flasgger import swag_from
from app.core.schemas.version_control_schemas import (
    CreateVersionRequestSchema,
    VersionResponseSchema,
    CommitInfoSchema,
    CommitDiffSchema,
    TaskIdsResponseSchema,
    ErrorResponseSchema
)

version_control_bp = Blueprint('version_control', __name__, url_prefix='/api/v1/version-control')

# Initialize Git service
git_service = None

def init_git_service(app):
    """Initialize the Git service when the app starts."""
    global git_service
    if not git_service and not app.config.get('TESTING', False):
        from app.core.services.git_service import GitService
        git_service = GitService()

def register_git_service(app):
    """Register the Git service initialization with the app."""
    app.before_first_request(lambda: init_git_service(app))

version_control_bp.record_once(register_git_service)

@version_control_bp.route('/versions', methods=['POST'])
@login_required
@swag_from({
    'tags': ['version-control'],
    'summary': 'Create a new code version',
    'description': 'Create a new version entry in the version control system',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': CreateVersionRequestSchema
        }
    ],
    'responses': {
        '201': {
            'description': 'Version created successfully',
            'schema': VersionResponseSchema
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
@validate_request({
    'type': 'object',
    'required': ['commit_hash', 'author', 'commit_message', 'commit_timestamp'],
    'properties': {
        'commit_hash': {'type': 'string', 'minLength': 40, 'maxLength': 40},
        'author': {'type': 'string'},
        'commit_message': {'type': 'string'},
        'commit_timestamp': {'type': 'string', 'format': 'date-time'},
        'branch_name': {'type': 'string'},
        'tag_name': {'type': 'string'},
        'metadata': {'type': 'object'}
    }
})
def create_version():
    """Create a new code version."""
    try:
        data = request.get_json()
        version = VersionControlService.create_version(
            commit_hash=data['commit_hash'],
            author=data['author'],
            commit_message=data['commit_message'],
            commit_timestamp=datetime.fromisoformat(data['commit_timestamp'].replace('Z', '+00:00')),
            branch_name=data.get('branch_name'),
            tag_name=data.get('tag_name'),
            metadata=data.get('metadata')
        )
        return jsonify({
            'message': 'Version created successfully',
            'version': {
                'id': version.id,
                'commit_hash': version.commit_hash,
                'author': version.author,
                'commit_message': version.commit_message,
                'commit_timestamp': version.commit_timestamp.isoformat(),
                'branch_name': version.branch_name,
                'tag_name': version.tag_name,
                'version_metadata': version.version_metadata
            }
        }), 201
    except VersionControlError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@version_control_bp.route('/versions/<commit_hash>', methods=['GET'])
@login_required
@swag_from({
    'tags': ['version-control'],
    'summary': 'Get version information',
    'description': 'Get version information by commit hash',
    'parameters': [
        {
            'name': 'commit_hash',
            'in': 'path',
            'required': True,
            'type': 'string',
            'description': 'SHA-1 hash of the commit'
        }
    ],
    'responses': {
        '200': {
            'description': 'Version information retrieved successfully',
            'schema': VersionResponseSchema
        },
        '404': {
            'description': 'Version not found',
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
def get_version(commit_hash: str):
    """Get version information by commit hash."""
    try:
        version = VersionControlService.get_version_by_commit_hash(commit_hash)
        if not version:
            return jsonify({'error': 'Version not found'}), 404
        return jsonify(version.to_dict()), 200
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@version_control_bp.route('/versions/<commit_hash>/tasks', methods=['GET'])
@login_required
def get_version_tasks(commit_hash: str):
    """Get tasks linked to a specific version."""
    try:
        tasks = VersionControlService.get_tasks_for_version(commit_hash)
        return jsonify([task.to_dict() for task in tasks]), 200
    except VersionControlError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@version_control_bp.route('/versions/<commit_hash>/tasks/<int:task_id>', methods=['POST'])
@login_required
@validate_request({
    'type': 'object',
    'required': ['link_type'],
    'properties': {
        'link_type': {'type': 'string', 'enum': ['implementation', 'review', 'test']},
        'metadata': {'type': 'object'}
    }
})
def link_task_to_version(commit_hash: str, task_id: int):
    """Link a task to a version."""
    try:
        data = request.get_json()
        version = VersionControlService.get_version_by_commit_hash(commit_hash)
        if not version:
            return jsonify({'error': 'Version not found'}), 404
            
        link = VersionControlService.link_task_to_version(
            task_id=task_id,
            version_id=version.id,
            link_type=data['link_type'],
            metadata=data.get('metadata', {})
        )
        return jsonify({
            'message': 'Task linked successfully',
            'link': {
                'id': link.id,
                'task_id': link.task_id,
                'version_id': link.version_id,
                'link_type': link.link_type,
                'link_metadata': link.link_metadata
            }
        }), 200
    except VersionControlError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@version_control_bp.route('/git/current-commit', methods=['GET'])
@login_required
@swag_from({
    'tags': ['version-control'],
    'summary': 'Get current commit information',
    'description': 'Get information about the current commit in the repository',
    'responses': {
        '200': {
            'description': 'Current commit information retrieved successfully',
            'schema': CommitInfoSchema
        },
        '400': {
            'description': 'Git operation failed',
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
def get_current_commit():
    """Get information about the current commit."""
    try:
        commit_info = git_service.get_current_commit()
        return jsonify(commit_info), 200
    except VersionControlError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@version_control_bp.route('/git/commits/<commit_hash>', methods=['GET'])
@login_required
def get_commit_info(commit_hash: str):
    """Get information about a specific commit."""
    try:
        commit_info = git_service.get_commit_info(commit_hash)
        return jsonify(commit_info), 200
    except VersionControlError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@version_control_bp.route('/git/branches/<branch_name>/commits', methods=['GET'])
@login_required
def get_branch_commits(branch_name: str):
    """Get commits from a specific branch."""
    try:
        limit = request.args.get('limit', type=int)
        commits = git_service.get_branch_commits(branch_name, limit)
        return jsonify(commits), 200
    except VersionControlError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@version_control_bp.route('/git/tags/<tag_name>/commits', methods=['GET'])
@login_required
def get_tag_commits(tag_name: str):
    """Get commits associated with a specific tag."""
    try:
        commits = git_service.get_tag_commits(tag_name)
        return jsonify(commits), 200
    except VersionControlError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@version_control_bp.route('/git/commits/<commit_hash>/diff', methods=['GET'])
@login_required
@swag_from({
    'tags': ['version-control'],
    'summary': 'Get commit diff',
    'description': 'Get the diff for a specific commit',
    'parameters': [
        {
            'name': 'commit_hash',
            'in': 'path',
            'required': True,
            'type': 'string',
            'description': 'SHA-1 hash of the commit'
        }
    ],
    'responses': {
        '200': {
            'description': 'Commit diff retrieved successfully',
            'schema': CommitDiffSchema
        },
        '400': {
            'description': 'Git operation failed',
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
def get_commit_diff(commit_hash: str):
    """Get the diff for a specific commit."""
    try:
        diff_data = git_service.get_commit_diff(commit_hash)
        return jsonify(diff_data), 200
    except VersionControlError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@version_control_bp.route('/git/files/<path:file_path>/history', methods=['GET'])
@login_required
def get_file_history(file_path: str):
    """Get the commit history for a specific file."""
    try:
        limit = request.args.get('limit', type=int)
        history = git_service.get_file_history(file_path, limit)
        return jsonify(history), 200
    except VersionControlError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@version_control_bp.route('/git/branches', methods=['GET'])
@login_required
def get_branches():
    """Get a list of all branches in the repository."""
    try:
        branches = git_service.get_branch_list()
        return jsonify(branches), 200
    except VersionControlError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@version_control_bp.route('/git/tags', methods=['GET'])
@login_required
def get_tags():
    """Get a list of all tags in the repository."""
    try:
        tags = git_service.get_tag_list()
        return jsonify(tags), 200
    except VersionControlError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@version_control_bp.route('/git/sync', methods=['POST'])
@login_required
def sync_repository():
    """Synchronize Git repository state with version control system."""
    try:
        git_service.sync_with_version_control()
        return jsonify({'message': 'Repository synchronized successfully'}), 200
    except VersionControlError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@version_control_bp.route('/git/commits/<commit_hash>/tasks', methods=['GET'])
@login_required
@swag_from({
    'tags': ['version-control'],
    'summary': 'Get commit tasks',
    'description': 'Get task IDs referenced in a commit message',
    'parameters': [
        {
            'name': 'commit_hash',
            'in': 'path',
            'required': True,
            'type': 'string',
            'description': 'SHA-1 hash of the commit'
        }
    ],
    'responses': {
        '200': {
            'description': 'Task IDs retrieved successfully',
            'schema': TaskIdsResponseSchema
        },
        '400': {
            'description': 'Git operation failed',
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
def get_commit_tasks(commit_hash: str):
    """Get task IDs referenced in a commit message."""
    try:
        task_ids = git_service.extract_task_ids_from_commit(commit_hash)
        return jsonify({'task_ids': task_ids}), 200
    except VersionControlError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@version_control_bp.route('/git/commits/<commit_hash>/link-tasks', methods=['POST'])
@login_required
def link_commit_tasks(commit_hash: str):
    """Link a commit to tasks based on its commit message."""
    try:
        task_ids = git_service.link_commit_to_tasks(commit_hash)
        return jsonify({
            'message': 'Tasks linked successfully',
            'task_ids': task_ids
        }), 200
    except VersionControlError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@version_control_bp.route('/versions/review-links', methods=['POST'])
@login_required
@validate_request({
    'type': 'object',
    'required': ['review_id', 'version_id'],
    'properties': {
        'review_id': {'type': 'integer'},
        'version_id': {'type': 'integer'},
        'link_type': {'type': 'string'},
        'metadata': {'type': 'object'}
    }
})
def link_review():
    """Link a review to a code version."""
    try:
        data = request.get_json()
        link = VersionControlService.link_review_to_version(
            review_id=data['review_id'],
            version_id=data['version_id'],
            link_type=data.get('link_type', 'review'),
            metadata=data.get('metadata')
        )
        return jsonify({
            'message': 'Review linked successfully',
            'link': {
                'id': link.id,
                'review_id': link.review_id,
                'version_id': link.version_id,
                'link_type': link.link_type,
                'metadata': link.metadata
            }
        }), 201
    except VersionControlError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@version_control_bp.route('/versions/task/<int:task_id>', methods=['GET'])
@login_required
def get_task_versions(task_id: int):
    """Get all code versions linked to a task."""
    try:
        versions = VersionControlService.get_task_versions(task_id)
        return jsonify({
            'versions': [{
                'id': v.id,
                'commit_hash': v.commit_hash,
                'author': v.author,
                'commit_message': v.commit_message,
                'commit_timestamp': v.commit_timestamp.isoformat(),
                'branch_name': v.branch_name,
                'tag_name': v.tag_name,
                'version_metadata': v.version_metadata
            } for v in versions]
        }), 200
    except VersionControlError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@version_control_bp.route('/versions/review/<int:review_id>', methods=['GET'])
@login_required
def get_review_versions(review_id: int):
    """Get all code versions linked to a review."""
    try:
        versions = VersionControlService.get_review_versions(review_id)
        return jsonify({
            'versions': [{
                'id': v.id,
                'commit_hash': v.commit_hash,
                'author': v.author,
                'commit_message': v.commit_message,
                'commit_timestamp': v.commit_timestamp.isoformat(),
                'branch_name': v.branch_name,
                'tag_name': v.tag_name,
                'metadata': v.metadata
            } for v in versions]
        }), 200
    except VersionControlError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@version_control_bp.route('/versions/<int:version_id>/tasks', methods=['GET'])
@login_required
def get_version_tasks(version_id: int):
    """Get all task IDs linked to a code version."""
    try:
        task_ids = VersionControlService.get_version_tasks(version_id)
        return jsonify({'task_ids': task_ids}), 200
    except VersionControlError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@version_control_bp.route('/versions/<int:version_id>/reviews', methods=['GET'])
@login_required
def get_version_reviews(version_id: int):
    """Get all review IDs linked to a code version."""
    try:
        review_ids = VersionControlService.get_version_reviews(version_id)
        return jsonify({'review_ids': review_ids}), 200
    except VersionControlError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@version_control_bp.route('/versions/<int:version_id>/metadata', methods=['PATCH'])
@login_required
@validate_request({
    'type': 'object',
    'required': ['metadata'],
    'properties': {
        'metadata': {'type': 'object'}
    }
})
def update_version_metadata(version_id: int):
    """Update the metadata of a code version."""
    try:
        data = request.get_json()
        version = VersionControlService.update_version_metadata(version_id, data['metadata'])
        return jsonify({
            'message': 'Version metadata updated successfully',
            'version': {
                'id': version.id,
                'commit_hash': version.commit_hash,
                'metadata': version.metadata
            }
        }), 200
    except VersionControlError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@version_control_bp.route('/versions/links/<string:link_type>/<int:link_id>', methods=['DELETE'])
@login_required
def delete_link(link_type: str, link_id: int):
    """Delete a version link."""
    try:
        if link_type not in ['task', 'review']:
            return jsonify({'error': 'Invalid link type'}), 400
            
        VersionControlService.delete_version_link(link_type, link_id)
        return jsonify({'message': 'Link deleted successfully'}), 200
    except VersionControlError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@version_control_bp.route('/versions/commit/<string:commit_hash>', methods=['GET'])
@login_required
def get_by_commit_hash(commit_hash: str):
    """Get a code version by its commit hash."""
    try:
        version = VersionControlService.get_version_by_commit_hash(commit_hash)
        if not version:
            return jsonify({'error': 'Version not found'}), 404
            
        return jsonify({
            'version': {
                'id': version.id,
                'commit_hash': version.commit_hash,
                'author': version.author,
                'commit_message': version.commit_message,
                'commit_timestamp': version.commit_timestamp.isoformat(),
                'branch_name': version.branch_name,
                'tag_name': version.tag_name,
                'metadata': version.metadata
            }
        }), 200
    except VersionControlError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@version_control_bp.route('/versions/branch/<string:branch_name>', methods=['GET'])
@login_required
def get_by_branch(branch_name: str):
    """Get all code versions for a specific branch."""
    try:
        versions = VersionControlService.get_versions_by_branch(branch_name)
        return jsonify({
            'versions': [{
                'id': v.id,
                'commit_hash': v.commit_hash,
                'author': v.author,
                'commit_message': v.commit_message,
                'commit_timestamp': v.commit_timestamp.isoformat(),
                'branch_name': v.branch_name,
                'tag_name': v.tag_name,
                'metadata': v.metadata
            } for v in versions]
        }), 200
    except VersionControlError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@version_control_bp.route('/versions/tag/<string:tag_name>', methods=['GET'])
@login_required
def get_by_tag(tag_name: str):
    """Get all code versions with a specific tag."""
    try:
        versions = VersionControlService.get_versions_by_tag(tag_name)
        return jsonify({
            'versions': [{
                'id': v.id,
                'commit_hash': v.commit_hash,
                'author': v.author,
                'commit_message': v.commit_message,
                'commit_timestamp': v.commit_timestamp.isoformat(),
                'branch_name': v.branch_name,
                'tag_name': v.tag_name,
                'metadata': v.metadata
            } for v in versions]
        }), 200
    except VersionControlError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500 