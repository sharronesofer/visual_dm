"""
Service layer for managing code version linkage operations.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_
from app.core.models.version_control import CodeVersion, TaskVersionLink, ReviewVersionLink
from app.core.database import db
from app.core.exceptions import VersionControlError

logger = logging.getLogger(__name__)

class VersionControlService:
    """Service for managing code version linkage operations."""

    @staticmethod
    def create_version(
        commit_hash: str,
        author: str,
        commit_message: str,
        commit_timestamp: datetime,
        branch_name: Optional[str] = None,
        tag_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> CodeVersion:
        """Create a new code version entry.
        
        Args:
            commit_hash: The SHA-1 hash of the commit
            author: The author of the commit
            commit_message: The commit message
            commit_timestamp: The timestamp of the commit
            branch_name: Optional branch name
            tag_name: Optional tag name
            metadata: Optional additional metadata
            
        Returns:
            The created CodeVersion instance
            
        Raises:
            VersionControlError: If version creation fails
        """
        try:
            version = CodeVersion(
                commit_hash=commit_hash,
                author=author,
                commit_message=commit_message,
                commit_timestamp=commit_timestamp,
                branch_name=branch_name,
                tag_name=tag_name,
                version_metadata=metadata or {}
            )
            db.session.add(version)
            db.session.commit()
            return version
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Failed to create code version: {str(e)}")
            raise VersionControlError(f"Failed to create code version: {str(e)}")

    @staticmethod
    def link_task_to_version(
        task_id: int,
        version_id: int,
        link_type: str = 'implementation',
        metadata: Optional[Dict[str, Any]] = None
    ) -> TaskVersionLink:
        """Link a task to a code version.
        
        Args:
            task_id: The ID of the task
            version_id: The ID of the code version
            link_type: The type of link (default: 'implementation')
            metadata: Optional additional metadata
            
        Returns:
            The created TaskVersionLink instance
            
        Raises:
            VersionControlError: If link creation fails
        """
        try:
            link = TaskVersionLink(
                task_id=task_id,
                version_id=version_id,
                link_type=link_type,
                link_metadata=metadata or {}
            )
            db.session.add(link)
            db.session.commit()
            return link
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Failed to link task to version: {str(e)}")
            raise VersionControlError(f"Failed to link task to version: {str(e)}")

    @staticmethod
    def link_review_to_version(
        review_id: int,
        version_id: int,
        link_type: str = 'review',
        metadata: Optional[Dict[str, Any]] = None
    ) -> ReviewVersionLink:
        """Link a review to a code version.
        
        Args:
            review_id: The ID of the review
            version_id: The ID of the code version
            link_type: The type of link (default: 'review')
            metadata: Optional additional metadata
            
        Returns:
            The created ReviewVersionLink instance
            
        Raises:
            VersionControlError: If link creation fails
        """
        try:
            link = ReviewVersionLink(
                review_id=review_id,
                version_id=version_id,
                link_type=link_type,
                link_metadata=metadata or {}
            )
            db.session.add(link)
            db.session.commit()
            return link
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Failed to link review to version: {str(e)}")
            raise VersionControlError(f"Failed to link review to version: {str(e)}")

    @staticmethod
    def get_task_versions(task_id: int) -> List[CodeVersion]:
        """Get all code versions linked to a task.
        
        Args:
            task_id: The ID of the task
            
        Returns:
            List of CodeVersion instances
        """
        try:
            links = TaskVersionLink.query.filter_by(task_id=task_id).all()
            return [link.version for link in links]
        except SQLAlchemyError as e:
            logger.error(f"Failed to get task versions: {str(e)}")
            raise VersionControlError(f"Failed to get task versions: {str(e)}")

    @staticmethod
    def get_review_versions(review_id: int) -> List[CodeVersion]:
        """Get all code versions linked to a review.
        
        Args:
            review_id: The ID of the review
            
        Returns:
            List of CodeVersion instances
        """
        try:
            links = ReviewVersionLink.query.filter_by(review_id=review_id).all()
            return [link.version for link in links]
        except SQLAlchemyError as e:
            logger.error(f"Failed to get review versions: {str(e)}")
            raise VersionControlError(f"Failed to get review versions: {str(e)}")

    @staticmethod
    def get_version_tasks(version_id: int) -> List[int]:
        """Get all task IDs linked to a code version.
        
        Args:
            version_id: The ID of the code version
            
        Returns:
            List of task IDs
        """
        try:
            links = TaskVersionLink.query.filter_by(version_id=version_id).all()
            return [link.task_id for link in links]
        except SQLAlchemyError as e:
            logger.error(f"Failed to get version tasks: {str(e)}")
            raise VersionControlError(f"Failed to get version tasks: {str(e)}")

    @staticmethod
    def get_version_reviews(version_id: int) -> List[int]:
        """Get all review IDs linked to a code version.
        
        Args:
            version_id: The ID of the code version
            
        Returns:
            List of review IDs
        """
        try:
            links = ReviewVersionLink.query.filter_by(version_id=version_id).all()
            return [link.review_id for link in links]
        except SQLAlchemyError as e:
            logger.error(f"Failed to get version reviews: {str(e)}")
            raise VersionControlError(f"Failed to get version reviews: {str(e)}")

    @staticmethod
    def update_version_metadata(version_id: int, metadata: Dict[str, Any]) -> CodeVersion:
        """Update the metadata of a code version.
        
        Args:
            version_id: The ID of the code version
            metadata: The new metadata to merge with existing
            
        Returns:
            The updated CodeVersion instance
            
        Raises:
            VersionControlError: If update fails
        """
        try:
            version = CodeVersion.query.get(version_id)
            if not version:
                raise VersionControlError(f"Version with ID {version_id} not found")
            
            # Merge new metadata with existing
            version.version_metadata.update(metadata)
            db.session.commit()
            return version
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Failed to update version metadata: {str(e)}")
            raise VersionControlError(f"Failed to update version metadata: {str(e)}")

    @staticmethod
    def delete_version_link(link_type: str, link_id: int) -> None:
        """Delete a version link.
        
        Args:
            link_type: The type of link ('task' or 'review')
            link_id: The ID of the link to delete
            
        Raises:
            VersionControlError: If deletion fails
        """
        try:
            if link_type == 'task':
                link = TaskVersionLink.query.get(link_id)
            elif link_type == 'review':
                link = ReviewVersionLink.query.get(link_id)
            else:
                raise VersionControlError(f"Invalid link type: {link_type}")

            if not link:
                raise VersionControlError(f"{link_type.capitalize()} link with ID {link_id} not found")

            db.session.delete(link)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Failed to delete version link: {str(e)}")
            raise VersionControlError(f"Failed to delete version link: {str(e)}")

    @staticmethod
    def get_version_by_commit_hash(commit_hash: str) -> Optional[CodeVersion]:
        """Get a code version by its commit hash.
        
        Args:
            commit_hash: The SHA-1 hash of the commit
            
        Returns:
            CodeVersion instance if found, None otherwise
        """
        try:
            return CodeVersion.query.filter_by(commit_hash=commit_hash).first()
        except SQLAlchemyError as e:
            logger.error(f"Failed to get version by commit hash: {str(e)}")
            raise VersionControlError(f"Failed to get version by commit hash: {str(e)}")

    @staticmethod
    def get_versions_by_branch(branch_name: str) -> List[CodeVersion]:
        """Get all code versions for a specific branch.
        
        Args:
            branch_name: The name of the branch
            
        Returns:
            List of CodeVersion instances
        """
        try:
            return CodeVersion.query.filter_by(branch_name=branch_name).order_by(CodeVersion.commit_timestamp.desc()).all()
        except SQLAlchemyError as e:
            logger.error(f"Failed to get versions by branch: {str(e)}")
            raise VersionControlError(f"Failed to get versions by branch: {str(e)}")

    @staticmethod
    def get_versions_by_tag(tag_name: str) -> List[CodeVersion]:
        """Get all code versions with a specific tag.
        
        Args:
            tag_name: The name of the tag
            
        Returns:
            List of CodeVersion instances
        """
        try:
            return CodeVersion.query.filter_by(tag_name=tag_name).order_by(CodeVersion.commit_timestamp.desc()).all()
        except SQLAlchemyError as e:
            logger.error(f"Failed to get versions by tag: {str(e)}")
            raise VersionControlError(f"Failed to get versions by tag: {str(e)}") 