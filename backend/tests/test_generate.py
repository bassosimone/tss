#!/usr/bin/env python3

import pytest
import sys
import os

# Add parent directory to path to import generate module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generate import (
    encrypt_message,
    generate_pairings,
    violates_couples_constraint,
    read_participants,
    read_couples,
)


# Fixtures with generic names for public transparency


@pytest.fixture
def sample_participants():
    """Sample participants for testing."""
    return ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "George"]


@pytest.fixture
def sample_couples():
    """Sample couples constraint for testing."""
    return [("Alice", "Bob"), ("Charlie", "Diana")]


@pytest.fixture
def minimal_participants():
    """Minimal participant set (edge case)."""
    return ["Alice", "Bob"]


@pytest.fixture
def large_participants():
    """Larger participant set for stress testing."""
    return [f"Person{i}" for i in range(1, 21)]  # 20 participants


# Tests for generate_pairings


class TestGeneratePairings:
    def test_creates_valid_derangement(self, sample_participants):
        """Test that pairings form a valid derangement (no self-loops)."""
        pairings = generate_pairings(sample_participants)

        # Check no one gives to themselves
        for giver, receiver in pairings:
            assert giver != receiver, f"{giver} should not give to themselves"

    def test_everyone_appears_once_as_giver(self, sample_participants):
        """Test that everyone appears exactly once as a giver."""
        pairings = generate_pairings(sample_participants)
        givers = [giver for giver, _ in pairings]

        assert len(givers) == len(sample_participants)
        assert set(givers) == set(sample_participants)
        assert len(set(givers)) == len(givers), "Duplicate givers found"

    def test_everyone_appears_once_as_receiver(self, sample_participants):
        """Test that everyone appears exactly once as a receiver."""
        pairings = generate_pairings(sample_participants)
        receivers = [receiver for _, receiver in pairings]

        assert len(receivers) == len(sample_participants)
        assert set(receivers) == set(sample_participants)
        assert len(set(receivers)) == len(receivers), "Duplicate receivers found"

    def test_forms_single_cycle(self, sample_participants):
        """Test that pairings form a single connected cycle."""
        pairings = generate_pairings(sample_participants)
        pairings_dict = dict(pairings)

        # Start from first person and follow the chain
        start = sample_participants[0]
        visited = {start}
        current = pairings_dict[start]

        # Follow the chain
        while current != start:
            assert current not in visited, "Found sub-cycle"
            visited.add(current)
            current = pairings_dict[current]

        # Should have visited everyone
        assert len(visited) == len(sample_participants)

    def test_minimal_participants(self, minimal_participants):
        """Test with minimal number of participants (2)."""
        pairings = generate_pairings(minimal_participants)

        assert len(pairings) == 2
        # With 2 people, they must give to each other
        assert pairings == [("Alice", "Bob"), ("Bob", "Alice")] or pairings == [
            ("Bob", "Alice"),
            ("Alice", "Bob"),
        ]

    def test_large_participants(self, large_participants):
        """Test with larger participant set."""
        pairings = generate_pairings(large_participants)

        assert len(pairings) == 20
        givers = {giver for giver, _ in pairings}
        receivers = {receiver for _, receiver in pairings}
        assert givers == set(large_participants)
        assert receivers == set(large_participants)


# Tests for couples constraint


class TestCouplesConstraint:
    def test_detects_couple_violation_forward(self, sample_couples):
        """Test detection of A→B when (A,B) are a couple."""
        pairings = [("Alice", "Bob"), ("Bob", "Charlie")]
        assert violates_couples_constraint(pairings, sample_couples) is True

    def test_detects_couple_violation_backward(self, sample_couples):
        """Test detection of B→A when (A,B) are a couple."""
        pairings = [("Bob", "Alice"), ("Alice", "Charlie")]
        assert violates_couples_constraint(pairings, sample_couples) is True

    def test_no_violation_when_couples_separated(self, sample_couples):
        """Test no violation when couples don't give to each other."""
        pairings = [
            ("Alice", "Charlie"),
            ("Bob", "Diana"),
            ("Charlie", "Eve"),
            ("Diana", "Frank"),
            ("Eve", "George"),
            ("Frank", "Bob"),
            ("George", "Alice"),
        ]
        assert violates_couples_constraint(pairings, sample_couples) is False

    def test_empty_couples_list(self, sample_participants):
        """Test with no couples constraint."""
        pairings = generate_pairings(sample_participants)
        assert violates_couples_constraint(pairings, []) is False

    def test_multiple_couple_violations(self):
        """Test detection with multiple couple violations."""
        couples = [("Alice", "Bob"), ("Charlie", "Diana")]
        # Both couples give to each other
        pairings = [
            ("Alice", "Bob"),
            ("Bob", "Alice"),
            ("Charlie", "Diana"),
            ("Diana", "Charlie"),
        ]
        assert violates_couples_constraint(pairings, couples) is True


# Tests for encryption


class TestEncryption:
    def test_encrypt_returns_base64url(self):
        """Test that encryption returns valid base64url string."""
        fragment = encrypt_message("Alice", padding_length=32)

        # Base64url should only contain A-Z, a-z, 0-9, -, _
        valid_chars = set(
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
        )
        assert all(c in valid_chars for c in fragment)

    def test_encrypt_same_message_different_keys(self):
        """Test that same message produces different ciphertexts (different keys)."""
        fragment1 = encrypt_message("Alice", padding_length=32)
        fragment2 = encrypt_message("Alice", padding_length=32)

        # Should be different due to random key
        assert fragment1 != fragment2

    def test_padding_produces_equal_length(self):
        """Test that padding produces equal-length ciphertexts."""
        short_name = encrypt_message("Al", padding_length=32)
        long_name = encrypt_message("Christopher", padding_length=32)

        # Both should produce same-length fragments
        assert len(short_name) == len(long_name)

    def test_padding_length_respected(self):
        """Test that different padding lengths produce different output sizes."""
        fragment_16 = encrypt_message("Alice", padding_length=16)
        fragment_32 = encrypt_message("Alice", padding_length=32)

        assert len(fragment_16) != len(fragment_32)
        assert len(fragment_32) > len(fragment_16)


# Tests for file I/O


class TestFileIO:
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

    def test_read_couples_space_separated(self, tmp_path):
        """Test reading couples with space separation."""
        couples_file = tmp_path / "couples.txt"
        couples_file.write_text("Alice Bob\nCharlie Diana\n")

        couples = read_couples(str(couples_file))
        assert couples == [("Alice", "Bob"), ("Charlie", "Diana")]

    def test_read_couples_comma_separated(self, tmp_path):
        """Test reading couples with comma separation."""
        couples_file = tmp_path / "couples.txt"
        couples_file.write_text("Alice, Bob\nCharlie, Diana\n")

        couples = read_couples(str(couples_file))
        assert couples == [("Alice", "Bob"), ("Charlie", "Diana")]

    def test_read_couples_missing_file(self):
        """Test that missing couples file returns empty list."""
        couples = read_couples("/nonexistent/path/couples.txt")
        assert couples == []

    def test_read_couples_invalid_format(self, tmp_path, capsys):
        """Test handling of invalid couple format."""
        couples_file = tmp_path / "couples.txt"
        couples_file.write_text("Alice Bob Charlie\nDiana Eve\n")

        couples = read_couples(str(couples_file))
        # First line is invalid (3 names), second line is valid
        assert couples == [("Diana", "Eve")]

        # Check warning was printed
        captured = capsys.readouterr()
        assert "Warning" in captured.out


# Integration tests


class TestIntegration:
    def test_end_to_end_without_couples(self, sample_participants):
        """Test complete flow without couples constraint."""
        pairings = generate_pairings(sample_participants)

        # Verify basic properties
        assert len(pairings) == len(sample_participants)
        givers = {g for g, _ in pairings}
        receivers = {r for _, r in pairings}
        assert givers == set(sample_participants)
        assert receivers == set(sample_participants)

        # No couples constraint, so nothing to check
        assert violates_couples_constraint(pairings, []) is False

    def test_end_to_end_with_couples_retry(self, sample_participants, sample_couples):
        """Test that retry mechanism can find valid pairings with couples."""
        max_attempts = 100
        found_valid = False

        for _ in range(max_attempts):
            pairings = generate_pairings(sample_participants)
            if not violates_couples_constraint(pairings, sample_couples):
                found_valid = True
                break

        # With 7 participants and 2 couples, should be able to find valid pairing
        assert found_valid, "Could not find valid pairing within max attempts"

    def test_all_urls_same_length(self, sample_participants):
        """Test that all URLs have the same length (due to padding)."""
        pairings = generate_pairings(sample_participants)

        fragments = []
        for _, receiver in pairings:
            fragment = encrypt_message(receiver, padding_length=32)
            fragments.append(fragment)

        # All fragments should have the same length
        lengths = [len(f) for f in fragments]
        assert len(set(lengths)) == 1, f"Found different lengths: {set(lengths)}"
