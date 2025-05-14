"""
Version control schemas for request/response validation and Swagger documentation.
"""

from marshmallow import Schema, fields, validate

class VersionMetadataSchema(Schema):
    """Schema for version metadata."""
    parents = fields.List(fields.Str(), metadata={
        "description": "List of parent commit hashes",
        "example": ["abc123def456", "ghi789jkl012"]
    })
    files_changed = fields.List(fields.Str(), metadata={
        "description": "List of files changed in the commit",
        "example": ["app/core/models/user.py", "app/core/routes/auth.py"]
    })
    tag_message = fields.Str(allow_none=True, metadata={
        "description": "Message associated with the tag",
        "example": "Release v1.0.0"
    })

class CreateVersionRequestSchema(Schema):
    """Schema for creating a new version."""
    commit_hash = fields.Str(required=True, validate=validate.Length(equal=40), metadata={
        "description": "SHA-1 hash of the commit",
        "example": "abc123def456789ghi012jkl345mno678pqr901stu"
    })
    author = fields.Str(required=True, metadata={
        "description": "Author of the commit",
        "example": "John Doe <john.doe@example.com>"
    })
    commit_message = fields.Str(required=True, metadata={
        "description": "Commit message",
        "example": "feat: Add user authentication"
    })
    commit_timestamp = fields.DateTime(required=True, metadata={
        "description": "Timestamp of the commit",
        "example": "2024-03-15T12:34:56Z"
    })
    branch_name = fields.Str(metadata={
        "description": "Name of the branch",
        "example": "feature/user-auth"
    })
    tag_name = fields.Str(metadata={
        "description": "Name of the tag",
        "example": "v1.0.0"
    })
    metadata = fields.Nested(VersionMetadataSchema, metadata={
        "description": "Additional metadata about the version"
    })

class VersionResponseSchema(Schema):
    """Schema for version response."""
    id = fields.Int(required=True, metadata={
        "description": "Unique identifier for the version",
        "example": 1
    })
    commit_hash = fields.Str(required=True, metadata={
        "description": "SHA-1 hash of the commit",
        "example": "abc123def456789ghi012jkl345mno678pqr901stu"
    })
    author = fields.Str(required=True, metadata={
        "description": "Author of the commit",
        "example": "John Doe <john.doe@example.com>"
    })
    commit_message = fields.Str(required=True, metadata={
        "description": "Commit message",
        "example": "feat: Add user authentication"
    })
    commit_timestamp = fields.DateTime(required=True, metadata={
        "description": "Timestamp of the commit",
        "example": "2024-03-15T12:34:56Z"
    })
    branch_name = fields.Str(metadata={
        "description": "Name of the branch",
        "example": "feature/user-auth"
    })
    tag_name = fields.Str(metadata={
        "description": "Name of the tag",
        "example": "v1.0.0"
    })
    version_metadata = fields.Nested(VersionMetadataSchema, metadata={
        "description": "Additional metadata about the version"
    })

class CommitInfoSchema(Schema):
    """Schema for commit information."""
    hash = fields.Str(required=True, metadata={
        "description": "SHA-1 hash of the commit",
        "example": "abc123def456789ghi012jkl345mno678pqr901stu"
    })
    author = fields.Str(required=True, metadata={
        "description": "Author of the commit",
        "example": "John Doe <john.doe@example.com>"
    })
    message = fields.Str(required=True, metadata={
        "description": "Commit message",
        "example": "feat: Add user authentication"
    })
    timestamp = fields.DateTime(required=True, metadata={
        "description": "Timestamp of the commit",
        "example": "2024-03-15T12:34:56Z"
    })
    branch = fields.Str(metadata={
        "description": "Name of the current branch",
        "example": "feature/user-auth"
    })

class CommitDiffSchema(Schema):
    """Schema for commit diff information."""
    files_changed = fields.List(fields.Str(), metadata={
        "description": "List of files changed in the commit",
        "example": ["app/core/models/user.py", "app/core/routes/auth.py"]
    })
    insertions = fields.Int(metadata={
        "description": "Number of lines inserted",
        "example": 50
    })
    deletions = fields.Int(metadata={
        "description": "Number of lines deleted",
        "example": 20
    })
    diff = fields.Str(metadata={
        "description": "Git diff output",
        "example": "@@ -1,3 +1,5 @@\n+import os\n+from datetime import datetime\n def main():\n-    pass\n+    print('Hello')\n"
    })

class TaskIdsResponseSchema(Schema):
    """Schema for task IDs response."""
    task_ids = fields.List(fields.Int(), metadata={
        "description": "List of task IDs referenced in the commit",
        "example": [123, 456]
    })

class ErrorResponseSchema(Schema):
    """Schema for error responses."""
    error = fields.Str(required=True, metadata={
        "description": "Error message",
        "example": "Version not found"
    }) 