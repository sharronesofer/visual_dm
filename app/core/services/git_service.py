"""
Service for Git repository operations and integration.
"""

import os
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging
from git import Repo, GitCommandError
from app.core.exceptions import VersionControlError
from app.core.services.version_control_service import VersionControlService

logger = logging.getLogger(__name__)

class GitService:
    """Service for handling Git repository operations."""
    
    def __init__(self, repo_path: str):
        """Initialize the Git service.
        
        Args:
            repo_path: Path to the Git repository
        """
        try:
            self.repo = Repo(repo_path)
            self.repo_path = repo_path
        except Exception as e:
            raise VersionControlError(f"Failed to initialize Git repository: {str(e)}")
    
    def get_current_commit(self) -> Dict[str, Any]:
        """Get information about the current commit.
        
        Returns:
            Dict containing commit information
        """
        try:
            commit = self.repo.head.commit
            return {
                'hash': commit.hexsha,
                'author': f"{commit.author.name} <{commit.author.email}>",
                'message': commit.message.strip(),
                'timestamp': datetime.fromtimestamp(commit.committed_date),
                'branch': self.repo.active_branch.name
            }
        except Exception as e:
            raise VersionControlError(f"Failed to get current commit info: {str(e)}")
    
    def get_commit_info(self, commit_hash: str) -> Dict[str, Any]:
        """Get information about a specific commit.
        
        Args:
            commit_hash: The hash of the commit
            
        Returns:
            Dict containing commit information
        """
        try:
            commit = self.repo.commit(commit_hash)
            return {
                'hash': commit.hexsha,
                'author': f"{commit.author.name} <{commit.author.email}>",
                'message': commit.message.strip(),
                'timestamp': datetime.fromtimestamp(commit.committed_date),
                'branch': self._get_branch_for_commit(commit.hexsha)
            }
        except Exception as e:
            raise VersionControlError(f"Failed to get commit info: {str(e)}")
    
    def get_branch_commits(self, branch_name: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get commits from a specific branch.
        
        Args:
            branch_name: Name of the branch
            limit: Maximum number of commits to return
            
        Returns:
            List of dicts containing commit information
        """
        try:
            branch = self.repo.branches[branch_name]
            commits = []
            for commit in self.repo.iter_commits(branch, max_count=limit):
                commits.append({
                    'hash': commit.hexsha,
                    'author': f"{commit.author.name} <{commit.author.email}>",
                    'message': commit.message.strip(),
                    'timestamp': datetime.fromtimestamp(commit.committed_date)
                })
            return commits
        except Exception as e:
            raise VersionControlError(f"Failed to get branch commits: {str(e)}")
    
    def get_tag_commits(self, tag_name: str) -> List[Dict[str, Any]]:
        """Get commits associated with a specific tag.
        
        Args:
            tag_name: Name of the tag
            
        Returns:
            List of dicts containing commit information
        """
        try:
            tag = self.repo.tags[tag_name]
            commits = []
            for commit in self.repo.iter_commits(tag):
                commits.append({
                    'hash': commit.hexsha,
                    'author': f"{commit.author.name} <{commit.author.email}>",
                    'message': commit.message.strip(),
                    'timestamp': datetime.fromtimestamp(commit.committed_date)
                })
            return commits
        except Exception as e:
            raise VersionControlError(f"Failed to get tag commits: {str(e)}")
    
    def get_commit_diff(self, commit_hash: str) -> Dict[str, Any]:
        """Get the diff for a specific commit.
        
        Args:
            commit_hash: The hash of the commit
            
        Returns:
            Dict containing diff information
        """
        try:
            commit = self.repo.commit(commit_hash)
            parent = commit.parents[0] if commit.parents else None
            
            diff_data = {
                'files_changed': [],
                'insertions': 0,
                'deletions': 0
            }
            
            if parent:
                diff = parent.diff(commit)
                diff_data['insertions'] = diff.stats.total['insertions']
                diff_data['deletions'] = diff.stats.total['deletions']
                
                for diff_item in diff:
                    file_diff = {
                        'path': diff_item.a_path or diff_item.b_path,
                        'change_type': diff_item.change_type,
                        'insertions': 0,
                        'deletions': 0
                    }
                    
                    if diff_item.a_blob and diff_item.b_blob:
                        file_diff['insertions'] = len([l for l in diff_item.diff.decode().split('\n') if l.startswith('+')])
                        file_diff['deletions'] = len([l for l in diff_item.diff.decode().split('\n') if l.startswith('-')])
                    
                    diff_data['files_changed'].append(file_diff)
            
            return diff_data
        except Exception as e:
            raise VersionControlError(f"Failed to get commit diff: {str(e)}")
    
    def get_file_history(self, file_path: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get the commit history for a specific file.
        
        Args:
            file_path: Path to the file relative to repository root
            limit: Maximum number of commits to return
            
        Returns:
            List of dicts containing commit information
        """
        try:
            commits = []
            for commit in self.repo.iter_commits(paths=file_path, max_count=limit):
                commits.append({
                    'hash': commit.hexsha,
                    'author': f"{commit.author.name} <{commit.author.email}>",
                    'message': commit.message.strip(),
                    'timestamp': datetime.fromtimestamp(commit.committed_date)
                })
            return commits
        except Exception as e:
            raise VersionControlError(f"Failed to get file history: {str(e)}")
    
    def get_branch_list(self) -> List[str]:
        """Get a list of all branches in the repository.
        
        Returns:
            List of branch names
        """
        try:
            return [branch.name for branch in self.repo.branches]
        except Exception as e:
            raise VersionControlError(f"Failed to get branch list: {str(e)}")
    
    def get_tag_list(self) -> List[str]:
        """Get a list of all tags in the repository.
        
        Returns:
            List of tag names
        """
        try:
            return [tag.name for tag in self.repo.tags]
        except Exception as e:
            raise VersionControlError(f"Failed to get tag list: {str(e)}")
    
    def _get_branch_for_commit(self, commit_hash: str) -> Optional[str]:
        """Get the branch name that contains a specific commit.
        
        Args:
            commit_hash: The hash of the commit
            
        Returns:
            Branch name or None if not found
        """
        try:
            for branch in self.repo.branches:
                if commit_hash in [c.hexsha for c in self.repo.iter_commits(branch)]:
                    return branch.name
            return None
        except Exception:
            return None
    
    def sync_with_version_control(self) -> None:
        """Synchronize Git repository state with version control system.
        
        This method ensures that all commits, branches, and tags in the repository
        are properly tracked in the version control system.
        """
        try:
            # Get all branches
            for branch in self.repo.branches:
                # Get commits for each branch
                for commit in self.repo.iter_commits(branch):
                    commit_info = {
                        'commit_hash': commit.hexsha,
                        'author': f"{commit.author.name} <{commit.author.email}>",
                        'commit_message': commit.message.strip(),
                        'commit_timestamp': datetime.fromtimestamp(commit.committed_date),
                        'branch_name': branch.name,
                        'metadata': {
                            'parents': [p.hexsha for p in commit.parents],
                            'files_changed': list(commit.stats.files.keys())
                        }
                    }
                    
                    try:
                        # Try to create version entry
                        VersionControlService.create_version(**commit_info)
                    except VersionControlError:
                        # Version might already exist, continue
                        continue
            
            # Handle tags
            for tag in self.repo.tags:
                commit = tag.commit
                commit_info = {
                    'commit_hash': commit.hexsha,
                    'author': f"{commit.author.name} <{commit.author.email}>",
                    'commit_message': commit.message.strip(),
                    'commit_timestamp': datetime.fromtimestamp(commit.committed_date),
                    'tag_name': tag.name,
                    'metadata': {
                        'tag_message': tag.tag.message if isinstance(tag.tag, type) else None,
                        'parents': [p.hexsha for p in commit.parents],
                        'files_changed': list(commit.stats.files.keys())
                    }
                }
                
                try:
                    # Try to update version entry with tag information
                    version = VersionControlService.get_version_by_commit_hash(commit.hexsha)
                    if version:
                        VersionControlService.update_version_metadata(
                            version.id,
                            {**version.metadata, **commit_info['metadata']}
                        )
                except VersionControlError:
                    # Version doesn't exist, create it
                    VersionControlService.create_version(**commit_info)
                    
        except Exception as e:
            raise VersionControlError(f"Failed to sync with version control: {str(e)}")
    
    def extract_task_ids_from_commit(self, commit_hash: str) -> List[int]:
        """Extract task IDs from a commit message.
        
        Args:
            commit_hash: The hash of the commit
            
        Returns:
            List of task IDs referenced in the commit message
        """
        try:
            commit = self.repo.commit(commit_hash)
            # Look for patterns like "Task #123" or "#123" or "Fix task 123"
            patterns = [
                r'Task #(\d+)',
                r'#(\d+)',
                r'[Tt]ask (\d+)',
                r'[Ff]ix (\d+)'
            ]
            
            task_ids = set()
            for pattern in patterns:
                matches = re.finditer(pattern, commit.message)
                task_ids.update(int(match.group(1)) for match in matches)
            
            return sorted(list(task_ids))
        except Exception as e:
            raise VersionControlError(f"Failed to extract task IDs: {str(e)}")
    
    def link_commit_to_tasks(self, commit_hash: str) -> List[int]:
        """Link a commit to tasks based on its commit message.
        
        Args:
            commit_hash: The hash of the commit
            
        Returns:
            List of task IDs that were linked
        """
        try:
            task_ids = self.extract_task_ids_from_commit(commit_hash)
            commit_info = self.get_commit_info(commit_hash)
            
            # Create version entry if it doesn't exist
            try:
                version = VersionControlService.get_version_by_commit_hash(commit_hash)
                if not version:
                    version = VersionControlService.create_version(
                        commit_hash=commit_hash,
                        author=commit_info['author'],
                        commit_message=commit_info['message'],
                        commit_timestamp=commit_info['timestamp'],
                        branch_name=commit_info['branch'],
                        metadata={'auto_created': True}
                    )
            except VersionControlError:
                # Version already exists
                pass
            
            # Link tasks
            for task_id in task_ids:
                try:
                    VersionControlService.link_task_to_version(
                        task_id=task_id,
                        version_id=version.id,
                        link_type='implementation',
                        metadata={'auto_linked': True}
                    )
                except VersionControlError:
                    # Link might already exist
                    continue
            
            return task_ids
        except Exception as e:
            raise VersionControlError(f"Failed to link commit to tasks: {str(e)}") 