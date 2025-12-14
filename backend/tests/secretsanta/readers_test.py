"""Tests for secretsanta.readers module."""

import pytest

from secretsanta.readers import (
    read_participants,
    read_couples,
)


class TestReadParticipants:
    """Tests for read_participants."""

    def test_read_participants(self, tmp_path):
        """Test reading participants from file."""
        participants_file = tmp_path / "participants.txt"
        participants_file.write_text("Alice\nBob\nCharlie\n")

        participants = read_participants(str(participants_file))
        assert participants == ["Alice", "Bob", "Charlie"]

    def test_read_participants_ignores_empty_lines(self, tmp_path):
        """Test that empty lines are ignored."""
        participants_file = tmp_path / "participants.txt"
        participants_file.write_text("Alice\n\nBob\n\n\nCharlie\n")

        participants = read_participants(str(participants_file))
        assert participants == ["Alice", "Bob", "Charlie"]

    def test_read_participants_strips_whitespace(self, tmp_path):
        """Test that whitespace is stripped from names."""
        participants_file = tmp_path / "participants.txt"
        participants_file.write_text("  Alice  \n\tBob\t\n Charlie \n")

        participants = read_participants(str(participants_file))
        assert participants == ["Alice", "Bob", "Charlie"]


class TestReadCouples:
    """Tests for read_couples."""

    def test_read_valid_file(self, tmp_path):
        """Test reading couples with comma separation."""
        couples_file = tmp_path / "couples.txt"
        couples_file.write_text("Alice,Bob\nCharlie,Diana\n")

        couples = read_couples(str(couples_file))
        assert couples == [("Alice", "Bob"), ("Charlie", "Diana")]

    def test_read_with_stripping(self, tmp_path):
        """Test reading couples with comma separation."""
        couples_file = tmp_path / "couples.txt"
        couples_file.write_text(" Alice , Bob  \n Charlie ,  Diana \n")

        couples = read_couples(str(couples_file))
        assert couples == [("Alice", "Bob"), ("Charlie", "Diana")]

    def test_read_couples_ignores_empty_lines(self, tmp_path):
        """Test that empty lines are ignored."""
        couples_file = tmp_path / "couples.txt"
        couples_file.write_text("Alice,Bob\n\nCharlie,Diana\n\n")

        couples = read_couples(str(couples_file))
        assert couples == [("Alice", "Bob"), ("Charlie", "Diana")]

    def test_read_couples_missing_file(self):
        """Test that missing couples file returns empty list."""
        with pytest.raises(FileNotFoundError):
            _ = read_couples("/nonexistent/path/couples.txt")

    def test_read_couples_too_many_entries(self, tmp_path):
        """Test handling of invalid couple format."""
        couples_file = tmp_path / "couples.txt"
        couples_file.write_text("Alice,Bob,Charlie\n")

        with pytest.raises(ValueError):
            _ = read_couples(str(couples_file))

    def test_read_couples_too_few_entries(self, tmp_path):
        """Test handling of invalid couple format."""
        couples_file = tmp_path / "couples.txt"
        couples_file.write_text("Alice Bob\n")

        with pytest.raises(ValueError):
            _ = read_couples(str(couples_file))
