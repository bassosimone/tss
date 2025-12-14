"""Tests for secretsanta.pairings module."""

import pytest

from secretsanta.pairings import (
    generate_pairings,
    violates_couples_constraint,
)


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


class TestGeneratePairings:
    """Tests for generate_pairings function."""

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


class TestViolatesCouplesConstraint:
    """Tests for violates_couples_constraint function."""

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
