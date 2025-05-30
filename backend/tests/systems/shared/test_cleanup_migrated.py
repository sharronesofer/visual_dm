"""
Tests for backend.systems.shared.utils.cleanup_migrated

Comprehensive tests for the migrated files cleanup script.
"""

import pytest
import sys
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
from io import StringIO

# Import the module being tested
try: pass
    from backend.systems.shared.utils.cleanup_migrated import (
        check_modules_importable,
        check_files_exist,
        delete_migrated_files,
        main,
        MIGRATION_MAP,
        BASE_DIR,
        logger,
    )
except ImportError as e: pass
    pytest.skip(f"Could not import backend.systems.shared.utils.cleanup_migrated: {e}", allow_module_level=True)


def test_module_imports(): pass
    """Test that the module can be imported without errors."""
    assert check_modules_importable is not None
    assert check_files_exist is not None
    assert delete_migrated_files is not None
    assert main is not None
    assert MIGRATION_MAP is not None
    assert BASE_DIR is not None


class TestCleanupMigrated: pass
    """Test class for cleanup_migrated functionality."""

    def test_migration_map_structure(self): pass
        """Test that MIGRATION_MAP has the expected structure."""
        assert isinstance(MIGRATION_MAP, dict)
        assert len(MIGRATION_MAP) > 0
        
        # Check some expected mappings
        expected_mappings = {
            "time_utils.py": "core/time_utils.py",
            "json_storage_utils.py": "core/json_storage_utils.py",
            "memory_utils.py": "game/memory_utils.py",
        }
        
        for old_path, new_path in expected_mappings.items(): pass
            assert old_path in MIGRATION_MAP
            assert MIGRATION_MAP[old_path] == new_path

    @patch('backend.systems.shared.utils.cleanup_migrated.importlib.import_module')
    @patch('backend.systems.shared.utils.cleanup_migrated.logger')
    def test_check_modules_importable_success(self, mock_logger, mock_import): pass
        """Test check_modules_importable when all modules can be imported."""
        # Mock successful imports
        mock_import.return_value = MagicMock()
        
        result = check_modules_importable()
        
        assert result is True
        # Should have tried to import each module
        assert mock_import.call_count == len(MIGRATION_MAP)
        # Should have logged success for each module
        assert mock_logger.info.call_count == len(MIGRATION_MAP)

    @patch('backend.systems.shared.utils.cleanup_migrated.importlib.import_module')
    @patch('backend.systems.shared.utils.cleanup_migrated.logger')
    def test_check_modules_importable_failure(self, mock_logger, mock_import): pass
        """Test check_modules_importable when some modules fail to import."""
        # Mock import failure for first module
        mock_import.side_effect = [ImportError("Module not found")] + [MagicMock()] * (len(MIGRATION_MAP) - 1)
        
        result = check_modules_importable()
        
        assert result is False
        # Should have tried to import each module
        assert mock_import.call_count == len(MIGRATION_MAP)
        # Should have logged error for failed import
        mock_logger.error.assert_called()

    @patch('backend.systems.shared.utils.cleanup_migrated.BASE_DIR')
    @patch('backend.systems.shared.utils.cleanup_migrated.logger')
    def test_check_files_exist_all_exist(self, mock_logger, mock_base_dir): pass
        """Test check_files_exist when all target files exist."""
        # Create mock directory structure
        mock_base_dir.__truediv__ = Mock()
        mock_file = Mock()
        mock_file.exists.return_value = True
        mock_base_dir.__truediv__.return_value = mock_file
        
        result = check_files_exist()
        
        assert result is True
        # Should have checked each file
        assert mock_base_dir.__truediv__.call_count == len(MIGRATION_MAP) * 2  # old and new paths
        # Should have logged success for each file
        assert mock_logger.info.call_count == len(MIGRATION_MAP)

    @patch('backend.systems.shared.utils.cleanup_migrated.BASE_DIR')
    @patch('backend.systems.shared.utils.cleanup_migrated.logger')
    def test_check_files_exist_some_missing(self, mock_logger, mock_base_dir): pass
        """Test check_files_exist when some target files are missing."""
        # Create mock directory structure where first file doesn't exist
        mock_base_dir.__truediv__ = Mock()
        
        def mock_file_creation(path): pass
            mock_file = Mock()
            # First new file doesn't exist, others do
            if "core/time_utils.py" in str(path): pass
                mock_file.exists.return_value = False
            else: pass
                mock_file.exists.return_value = True
            return mock_file
        
        mock_base_dir.__truediv__.side_effect = mock_file_creation
        
        result = check_files_exist()
        
        assert result is False
        # Should have logged error for missing file
        mock_logger.error.assert_called()

    @patch('backend.systems.shared.utils.cleanup_migrated.BASE_DIR')
    @patch('backend.systems.shared.utils.cleanup_migrated.logger')
    def test_delete_migrated_files_dry_run(self, mock_logger, mock_base_dir): pass
        """Test delete_migrated_files in dry run mode."""
        # Create mock directory structure
        mock_base_dir.__truediv__ = Mock()
        mock_file = Mock()
        mock_file.exists.return_value = True
        mock_base_dir.__truediv__.return_value = mock_file
        
        delete_migrated_files(dry_run=True)
        
        # Should not have called unlink
        mock_file.unlink.assert_not_called()
        # Should have logged what would be deleted
        assert mock_logger.info.call_count == len(MIGRATION_MAP)

    @patch('backend.systems.shared.utils.cleanup_migrated.BASE_DIR')
    @patch('backend.systems.shared.utils.cleanup_migrated.logger')
    def test_delete_migrated_files_real_mode(self, mock_logger, mock_base_dir): pass
        """Test delete_migrated_files in real mode."""
        # Create mock directory structure
        mock_base_dir.__truediv__ = Mock()
        mock_file = Mock()
        mock_file.exists.return_value = True
        mock_base_dir.__truediv__.return_value = mock_file
        
        delete_migrated_files(dry_run=False)
        
        # Should have called unlink for each existing file
        assert mock_file.unlink.call_count == len(MIGRATION_MAP)
        # Should have logged deletion for each file
        assert mock_logger.info.call_count == len(MIGRATION_MAP)

    @patch('backend.systems.shared.utils.cleanup_migrated.BASE_DIR')
    @patch('backend.systems.shared.utils.cleanup_migrated.logger')
    def test_delete_migrated_files_nonexistent_files(self, mock_logger, mock_base_dir): pass
        """Test delete_migrated_files when some files don't exist."""
        # Create mock directory structure where files don't exist
        mock_base_dir.__truediv__ = Mock()
        mock_file = Mock()
        mock_file.exists.return_value = False
        mock_base_dir.__truediv__.return_value = mock_file
        
        delete_migrated_files(dry_run=False)
        
        # Should not have called unlink
        mock_file.unlink.assert_not_called()
        # Should have logged warning for each missing file
        assert mock_logger.warning.call_count == len(MIGRATION_MAP)

    @patch('backend.systems.shared.utils.cleanup_migrated.BASE_DIR')
    @patch('backend.systems.shared.utils.cleanup_migrated.logger')
    def test_delete_migrated_files_deletion_error(self, mock_logger, mock_base_dir): pass
        """Test delete_migrated_files when deletion fails."""
        # Create mock directory structure
        mock_base_dir.__truediv__ = Mock()
        mock_file = Mock()
        mock_file.exists.return_value = True
        mock_file.unlink.side_effect = OSError("Permission denied")
        mock_base_dir.__truediv__.return_value = mock_file
        
        delete_migrated_files(dry_run=False)
        
        # Should have tried to unlink each file
        assert mock_file.unlink.call_count == len(MIGRATION_MAP)
        # Should have logged error for each failed deletion
        assert mock_logger.error.call_count == len(MIGRATION_MAP)

    @patch('backend.systems.shared.utils.cleanup_migrated.sys.argv', ['script.py'])
    @patch('backend.systems.shared.utils.cleanup_migrated.check_files_exist')
    @patch('backend.systems.shared.utils.cleanup_migrated.check_modules_importable')
    @patch('backend.systems.shared.utils.cleanup_migrated.delete_migrated_files')
    @patch('backend.systems.shared.utils.cleanup_migrated.logger')
    def test_main_dry_run_success(self, mock_logger, mock_delete, mock_importable, mock_files_exist): pass
        """Test main function in dry run mode with successful checks."""
        mock_files_exist.return_value = True
        mock_importable.return_value = True
        
        main()
        
        # Should have called check functions
        mock_files_exist.assert_called_once()
        mock_importable.assert_called_once()
        # Should have called delete in dry run mode
        mock_delete.assert_called_once_with(True)
        # Should have logged various messages
        assert mock_logger.info.call_count > 0

    @patch('backend.systems.shared.utils.cleanup_migrated.sys.argv', ['script.py', '--real'])
    @patch('backend.systems.shared.utils.cleanup_migrated.check_files_exist')
    @patch('backend.systems.shared.utils.cleanup_migrated.check_modules_importable')
    @patch('backend.systems.shared.utils.cleanup_migrated.delete_migrated_files')
    @patch('backend.systems.shared.utils.cleanup_migrated.logger')
    def test_main_real_mode_success(self, mock_logger, mock_delete, mock_importable, mock_files_exist): pass
        """Test main function in real mode with successful checks."""
        mock_files_exist.return_value = True
        mock_importable.return_value = True
        
        main()
        
        # Should have called check functions
        mock_files_exist.assert_called_once()
        mock_importable.assert_called_once()
        # Should have called delete in real mode
        mock_delete.assert_called_once_with(False)

    @patch('backend.systems.shared.utils.cleanup_migrated.sys.argv', ['script.py', '--force'])
    @patch('backend.systems.shared.utils.cleanup_migrated.check_files_exist')
    @patch('backend.systems.shared.utils.cleanup_migrated.check_modules_importable')
    @patch('backend.systems.shared.utils.cleanup_migrated.delete_migrated_files')
    @patch('backend.systems.shared.utils.cleanup_migrated.logger')
    def test_main_force_mode_with_failed_checks(self, mock_logger, mock_delete, mock_importable, mock_files_exist): pass
        """Test main function in force mode with failed checks."""
        mock_files_exist.return_value = False
        mock_importable.return_value = False
        
        main()
        
        # Should have called check functions
        mock_files_exist.assert_called_once()
        mock_importable.assert_called_once()
        # Should have called delete despite failed checks
        mock_delete.assert_called_once_with(True)
        # Should have logged warning about force mode
        mock_logger.warning.assert_called()

    @patch('backend.systems.shared.utils.cleanup_migrated.sys.argv', ['script.py'])
    @patch('backend.systems.shared.utils.cleanup_migrated.check_files_exist')
    @patch('backend.systems.shared.utils.cleanup_migrated.check_modules_importable')
    @patch('backend.systems.shared.utils.cleanup_migrated.delete_migrated_files')
    @patch('backend.systems.shared.utils.cleanup_migrated.logger')
    @patch('backend.systems.shared.utils.cleanup_migrated.sys.exit')
    def test_main_failed_checks_no_force(self, mock_exit, mock_logger, mock_delete, mock_importable, mock_files_exist): pass
        """Test main function with failed checks and no force mode."""
        mock_files_exist.return_value = False
        mock_importable.return_value = True
        
        main()
        
        # Should have called check functions
        mock_files_exist.assert_called_once()
        mock_importable.assert_called_once()
        # Should not have called delete
        mock_delete.assert_not_called()
        # Should have logged error and exited
        mock_logger.error.assert_called()
        mock_exit.assert_called_once_with(1)

    @patch('backend.systems.shared.utils.cleanup_migrated.sys.argv', ['script.py', '--real', '--force'])
    @patch('backend.systems.shared.utils.cleanup_migrated.check_files_exist')
    @patch('backend.systems.shared.utils.cleanup_migrated.check_modules_importable')
    @patch('backend.systems.shared.utils.cleanup_migrated.delete_migrated_files')
    @patch('backend.systems.shared.utils.cleanup_migrated.logger')
    def test_main_real_and_force_mode(self, mock_logger, mock_delete, mock_importable, mock_files_exist): pass
        """Test main function with both real and force mode."""
        mock_files_exist.return_value = False
        mock_importable.return_value = False
        
        main()
        
        # Should have called check functions
        mock_files_exist.assert_called_once()
        mock_importable.assert_called_once()
        # Should have called delete in real mode
        mock_delete.assert_called_once_with(False)
        # Should have logged force mode warning
        mock_logger.warning.assert_called()

    def test_base_dir_is_path(self): pass
        """Test that BASE_DIR is a Path object."""
        assert isinstance(BASE_DIR, Path)
        assert BASE_DIR.name == "utils"  # Should be the utils directory

    @patch('backend.systems.shared.utils.cleanup_migrated.logger')
    def test_logger_configuration(self, mock_logger): pass
        """Test that logger is properly configured."""
        # Logger should be accessible
        assert logger is not None
        assert logger.name == "backend.systems.shared.utils.cleanup_migrated"
