"""
Tests for Git service.
"""

import os
import pytest
from datetime import datetime
from app.core.services.git_service import GitService
from app.core.exceptions import VersionControlError

def test_git_service_initialization(test_repo):
    """Test initializing the Git service."""
    service = GitService(test_repo.working_dir)
    assert service.repo is not None
    assert service.repo_path == test_repo.working_dir
    
    # Test initialization with invalid path
    with pytest.raises(VersionControlError):
        GitService('/invalid/path')

def test_get_current_commit(test_repo):
    """Test getting current commit information."""
    service = GitService(test_repo.working_dir)
    commit_info = service.get_current_commit()
    
    assert 'hash' in commit_info
    assert 'author' in commit_info
    assert 'message' in commit_info
    assert 'timestamp' in commit_info
    assert 'branch' in commit_info
    assert commit_info['message'] == 'Initial commit'

def test_get_commit_info(test_repo):
    """Test getting specific commit information."""
    service = GitService(test_repo.working_dir)
    commit_hash = test_repo.head.commit.hexsha
    commit_info = service.get_commit_info(commit_hash)
    
    assert commit_info['hash'] == commit_hash
    assert commit_info['message'] == 'Initial commit'
    assert commit_info['branch'] == 'test-branch'
    
    # Test with invalid commit hash
    with pytest.raises(VersionControlError):
        service.get_commit_info('invalid')

def test_get_branch_commits(test_repo):
    """Test getting commits from a branch."""
    service = GitService(test_repo.working_dir)
    
    # Add another commit
    test_file = os.path.join(test_repo.working_dir, 'test.txt')
    with open(test_file, 'a') as f:
        f.write('\nAdditional content')
    test_repo.index.add(['test.txt'])
    test_repo.index.commit('Second commit')
    
    commits = service.get_branch_commits('test-branch')
    assert len(commits) == 2
    assert commits[0]['message'] == 'Second commit'
    assert commits[1]['message'] == 'Initial commit'
    
    # Test with limit
    commits = service.get_branch_commits('test-branch', limit=1)
    assert len(commits) == 1
    assert commits[0]['message'] == 'Second commit'
    
    # Test with invalid branch
    with pytest.raises(VersionControlError):
        service.get_branch_commits('invalid-branch')

def test_get_tag_commits(test_repo):
    """Test getting commits associated with a tag."""
    service = GitService(test_repo.working_dir)
    commits = service.get_tag_commits('v1.0.0')
    
    assert len(commits) == 1
    assert commits[0]['message'] == 'Initial commit'
    
    # Test with invalid tag
    with pytest.raises(VersionControlError):
        service.get_tag_commits('invalid-tag')

def test_get_commit_diff(test_repo):
    """Test getting commit diff information."""
    service = GitService(test_repo.working_dir)
    
    # Add a new file
    new_file = os.path.join(test_repo.working_dir, 'new.txt')
    with open(new_file, 'w') as f:
        f.write('New file content')
    test_repo.index.add(['new.txt'])
    commit = test_repo.index.commit('Add new file')
    
    diff_data = service.get_commit_diff(commit.hexsha)
    assert diff_data['files_changed']
    assert diff_data['insertions'] > 0
    assert diff_data['deletions'] == 0
    
    # Test with invalid commit hash
    with pytest.raises(VersionControlError):
        service.get_commit_diff('invalid')

def test_get_file_history(test_repo):
    """Test getting file commit history."""
    service = GitService(test_repo.working_dir)
    
    # Add multiple commits to the file
    test_file = os.path.join(test_repo.working_dir, 'test.txt')
    for i in range(3):
        with open(test_file, 'a') as f:
            f.write(f'\nContent {i}')
        test_repo.index.add(['test.txt'])
        test_repo.index.commit(f'Update {i}')
    
    history = service.get_file_history('test.txt')
    assert len(history) == 4  # Initial commit + 3 updates
    
    # Test with limit
    history = service.get_file_history('test.txt', limit=2)
    assert len(history) == 2
    
    # Test with non-existent file
    with pytest.raises(VersionControlError):
        service.get_file_history('nonexistent.txt')

def test_get_branch_list(test_repo):
    """Test getting list of branches."""
    service = GitService(test_repo.working_dir)
    branches = service.get_branch_list()
    
    assert 'test-branch' in branches
    assert len(branches) >= 1

def test_get_tag_list(test_repo):
    """Test getting list of tags."""
    service = GitService(test_repo.working_dir)
    tags = service.get_tag_list()
    
    assert 'v1.0.0' in tags
    assert len(tags) == 1

def test_extract_task_ids_from_commit(test_repo):
    """Test extracting task IDs from commit message."""
    service = GitService(test_repo.working_dir)
    
    # Create commits with different task reference formats
    messages = [
        'Task #123: Initial implementation',
        'Fix #456 and #789',
        'Implement task 101',
        'Fix task 202 and #303'
    ]
    
    expected_ids = {
        0: [123],
        1: [456, 789],
        2: [101],
        3: [202, 303]
    }
    
    test_file = os.path.join(test_repo.working_dir, 'test.txt')
    for i, message in enumerate(messages):
        with open(test_file, 'a') as f:
            f.write(f'\nUpdate {i}')
        test_repo.index.add(['test.txt'])
        commit = test_repo.index.commit(message)
        
        task_ids = service.extract_task_ids_from_commit(commit.hexsha)
        assert sorted(task_ids) == sorted(expected_ids[i])
    
    # Test with invalid commit hash
    with pytest.raises(VersionControlError):
        service.extract_task_ids_from_commit('invalid')

def test_link_commit_to_tasks(test_repo, session):
    """Test linking commit to tasks based on commit message."""
    service = GitService(test_repo.working_dir)
    
    # Create a commit with task references
    test_file = os.path.join(test_repo.working_dir, 'test.txt')
    with open(test_file, 'a') as f:
        f.write('\nUpdate for tasks')
    test_repo.index.add(['test.txt'])
    commit = test_repo.index.commit('Fix task 101 and #202')
    
    task_ids = service.link_commit_to_tasks(commit.hexsha)
    assert sorted(task_ids) == [101, 202]
    
    # Test with invalid commit hash
    with pytest.raises(VersionControlError):
        service.link_commit_to_tasks('invalid') 