"""
Unit tests for ftp_client.py script.
Written with AI, I don't know if it helps, but stuff passes
"""

from unittest import mock, TestCase, main as unittest_main
from unittest.mock import Mock, patch
import os
import tempfile
from ftp_client import main, parse_flags, upload_dir, delete_remote_directory


class TestFTPScript(TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_ftp = Mock()
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up after each test method."""
        # Clean up test directory
        import shutil

        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_parse_flags_basic(self):
        """Test basic flag parsing."""
        with patch("sys.argv", ["ftp.py", "local_dir", "remote_dir"]):
            args = parse_flags()
            self.assertEqual(args.local_directory, "local_dir")
            self.assertEqual(args.remote_directory, "remote_dir")
            self.assertFalse(args.js_bundle)

    def test_parse_flags_with_js_bundle(self):
        """Test flag parsing with js-bundle flag."""
        with patch("sys.argv", ["ftp.py", "local_dir", "remote_dir", "--js-bundle"]):
            args = parse_flags()
            self.assertEqual(args.local_directory, "local_dir")
            self.assertEqual(args.remote_directory, "remote_dir")
            self.assertTrue(args.js_bundle)

    def test_upload_dir_single_file(self):
        """Test uploading a directory with a single file."""
        # Create test file
        test_file = os.path.join(self.test_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test content")

        # Mock FTP
        mock_ftp = Mock()

        # Test upload
        upload_dir(mock_ftp, self.test_dir, "/remote/")

        # Verify FTP put was called
        mock_ftp.put.assert_called_once_with(test_file, "/remote/")

    def test_upload_dir_with_subdirectory(self):
        """Test uploading a directory with subdirectories."""
        # Create test structure
        subdir = os.path.join(self.test_dir, "subdir")
        os.makedirs(subdir)

        test_file1 = os.path.join(self.test_dir, "file1.txt")
        test_file2 = os.path.join(subdir, "file2.txt")

        with open(test_file1, "w") as f:
            f.write("content1")
        with open(test_file2, "w") as f:
            f.write("content2")

        # Mock FTP
        mock_ftp = Mock()

        # Test upload
        upload_dir(mock_ftp, self.test_dir, "/remote/")

        # Verify both files were uploaded
        self.assertEqual(mock_ftp.put.call_count, 2)

        # Check call arguments
        calls = [call[0] for call in mock_ftp.put.call_args_list]
        self.assertIn((test_file1, "/remote/"), calls)
        self.assertIn((test_file2, "/remote/subdir/"), calls)

    def test_delete_remote_directory_success(self):
        """Test successful deletion of remote directory."""
        mock_ftp = Mock()
        mock_ftp.list.return_value = ["file1.txt", "file2.txt"]

        delete_remote_directory(mock_ftp, "/remote/assets")

        # Verify list was called
        mock_ftp.list.assert_called_once_with("/remote/assets")

        # Verify files were deleted
        expected_calls = [
            mock.call("/remote/assets/file1.txt"),
            mock.call("/remote/assets/file2.txt"),
            mock.call("/remote/assets"),
        ]
        mock_ftp.delete.assert_has_calls(expected_calls)

    def test_delete_remote_directory_with_subdirs(self):
        """Test deletion of directory with subdirectories."""
        mock_ftp = Mock()

        # First call returns subdirectory
        # Second call (recursive) returns files in subdirectory
        mock_ftp.list.side_effect = [
            ["subdir"],  # First call - directory contains subdirectory
            ["file.txt"],  # Second call - subdirectory contains file
        ]

        # First delete call fails (it's a directory), second succeeds
        mock_ftp.delete.side_effect = [Exception("Is directory"), None, None, None]

        delete_remote_directory(mock_ftp, "/remote/assets")

        # Should have been called multiple times due to recursion
        self.assertGreater(mock_ftp.delete.call_count, 1)

    def test_delete_remote_directory_not_exists(self):
        """Test deletion when directory doesn't exist."""
        mock_ftp = Mock()
        mock_ftp.list.side_effect = Exception("Directory not found")

        # Should not raise exception
        delete_remote_directory(mock_ftp, "/remote/nonexistent")

        mock_ftp.list.assert_called_once_with("/remote/nonexistent")

    @patch.dict(
        os.environ,
        {"HOST": "test.example.com", "USERNAME": "testuser", "PASSWORD": "testpass"},
    )
    @patch("ftp_client.ftpretty")
    @patch("ftp_client.parse_flags")
    def test_main_without_js_bundle(self, mock_parse_flags, mock_ftpretty):
        """Test main function without js-bundle flag."""
        # Setup mocks
        mock_args = Mock()
        mock_args.local_directory = "/local"
        mock_args.remote_directory = "/remote"
        mock_args.js_bundle = False
        mock_parse_flags.return_value = mock_args

        mock_ftp_instance = Mock()
        mock_ftpretty.return_value = mock_ftp_instance

        with patch("ftp_client.upload_dir") as mock_upload_dir:
            main()

            # Verify FTP connection
            mock_ftpretty.assert_called_once_with(
                host="test.example.com",
                user="testuser",
                password="testpass",
                secure=True,
                port=21,
            )

            # Verify upload was called
            mock_upload_dir.assert_called_once_with(
                mock_ftp_instance, "/local", "/remote"
            )

            # Verify connection was closed
            mock_ftp_instance.close.assert_called_once()

    @patch.dict(
        os.environ,
        {"HOST": "test.example.com", "USERNAME": "testuser", "PASSWORD": "testpass"},
    )
    @patch("ftp_client.ftpretty")
    @patch("ftp_client.parse_flags")
    def test_main_with_js_bundle(self, mock_parse_flags, mock_ftpretty):
        """Test main function with js-bundle flag."""
        # Setup mocks
        mock_args = Mock()
        mock_args.local_directory = "/local"
        mock_args.remote_directory = "/remote"
        mock_args.js_bundle = True
        mock_parse_flags.return_value = mock_args

        mock_ftp_instance = Mock()
        mock_ftpretty.return_value = mock_ftp_instance

        with patch("ftp_client.upload_dir") as mock_upload_dir, patch(
            "ftp_client.delete_remote_directory"
        ) as mock_delete:

            main()

            # Verify deletion was called
            mock_delete.assert_called_once_with(mock_ftp_instance, "/remote/assets")

            # Verify upload was called
            mock_upload_dir.assert_called_once_with(
                mock_ftp_instance, "/local", "/remote"
            )


if __name__ == "__main__":
    # Run tests with verbose output
    unittest_main(verbosity=2)


if __name__ == "__main__":
    # Run tests with verbose output
    unittest_main(verbosity=2)
