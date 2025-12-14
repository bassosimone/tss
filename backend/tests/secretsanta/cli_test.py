"""Tests for secretsanta.cli module."""

import pytest

from secretsanta.cli import (
    _must_read_participants,
    _must_read_couples,
    _validate_participant_names_or_exit,
    _must_generate_pairings,
    _generate_urls,
    main,
)


class TestMustReadParticipants:
    """Tests for _must_read_participants function."""

    def test_reads_valid_file(self, tmp_path):
        """Test reading valid participants file."""
        participants_file = tmp_path / "participants.txt"
        participants_file.write_text("Alice\nBob\nCharlie\n")

        participants = _must_read_participants(str(participants_file))
        assert participants == ["Alice", "Bob", "Charlie"]

    def test_exits_on_missing_file(self):
        """Test that missing file causes sys.exit(1)."""
        with pytest.raises(SystemExit) as exc_info:
            _must_read_participants("/nonexistent/participants.txt")
        assert exc_info.value.code == 1

    def test_exits_on_too_few_participants(self, tmp_path):
        """Test that < 2 participants causes sys.exit(1)."""
        participants_file = tmp_path / "participants.txt"
        participants_file.write_text("Alice\n")

        with pytest.raises(SystemExit) as exc_info:
            _must_read_participants(str(participants_file))
        assert exc_info.value.code == 1


class TestValidateParticipantNamesOrExit:
    """Tests for _validate_participant_names_or_exit function."""

    def test_accepts_valid_names(self):
        """Test that valid names don't cause exit."""
        participants = ["Alice", "Bob", "Charlie"]
        # Should not raise
        _validate_participant_names_or_exit(participants, padding_length=32)

    def test_exits_on_name_too_long(self):
        """Test that name exceeding padding length causes sys.exit(1)."""
        participants = ["Alice", "Bob", "VeryLongNameThatExceedsPaddingLength"]

        with pytest.raises(SystemExit) as exc_info:
            _validate_participant_names_or_exit(participants, padding_length=16)
        assert exc_info.value.code == 1


class TestMustReadCouples:
    """Tests for _must_read_couples function."""

    def test_reads_valid_file(self, tmp_path):
        """Test reading valid couples file."""
        couples_file = tmp_path / "couples.txt"
        couples_file.write_text("Alice,Bob\nCharlie,Diana\n")

        couples = _must_read_couples(str(couples_file))
        assert couples == [("Alice", "Bob"), ("Charlie", "Diana")]

    def test_exits_on_missing_file(self):
        """Test that missing file causes sys.exit(1)."""
        with pytest.raises(SystemExit) as exc_info:
            _must_read_couples("/nonexistent/couples.txt")
        assert exc_info.value.code == 1


class TestMustGeneratePairings:
    """Tests for _must_generate_pairings function."""

    def test_generates_valid_pairings(self):
        """Test successful pairing generation."""
        participants = ["Alice", "Bob", "Charlie", "Diana"]
        couples = [("Alice", "Bob")]

        pairings = _must_generate_pairings(participants, couples, max_retries=100)

        assert len(pairings) == 4
        givers = {giver for giver, _ in pairings}
        assert givers == set(participants)

    def test_exits_on_impossible_constraints(self):
        """Test that impossible constraints cause sys.exit(1)."""
        # Only 2 people who are a couple - impossible
        participants = ["Alice", "Bob"]
        couples = [("Alice", "Bob")]

        with pytest.raises(SystemExit) as exc_info:
            _must_generate_pairings(participants, couples, max_retries=10)
        assert exc_info.value.code == 1


class TestGenerateUrls:
    """Tests for _generate_urls function."""

    def test_generates_correct_number_of_urls(self):
        """Test that correct number of URLs are generated."""
        pairings = [("Alice", "Bob"), ("Bob", "Charlie"), ("Charlie", "Alice")]
        base_url = "https://example.com/secret-santa/"

        urls = _generate_urls(pairings, base_url, padding_length=32)

        assert len(urls) == 3
        for giver, receiver, url in urls:
            assert url.startswith(base_url + "#")

    def test_urls_have_equal_length(self):
        """Test that all URLs have equal length (due to padding)."""
        pairings = [("Al", "Bob"), ("Christopher", "Di")]
        base_url = "https://example.com/"

        urls = _generate_urls(pairings, base_url, padding_length=32)

        url_lengths = [len(url) for _, _, url in urls]
        assert len(set(url_lengths)) == 1  # All same length


class TestMain:
    """Tests for main function."""

    def test_successful_execution(self, tmp_path, monkeypatch, capsys):
        """Test successful end-to-end execution."""
        # Create test files
        participants_file = tmp_path / "participants.txt"
        participants_file.write_text("Alice\nBob\nCharlie\nDiana\n")

        couples_file = tmp_path / "couples.txt"
        couples_file.write_text("Alice,Bob\n")

        # Mock command line arguments
        monkeypatch.setattr(
            "sys.argv",
            [
                "secretsanta",
                "--participants",
                str(participants_file),
                "--couples",
                str(couples_file),
                "--debug",  # Show receiver names
            ],
        )

        # Run main
        main()

        # Verify some output was produced (not checking exact format)
        captured = capsys.readouterr()
        assert "Alice" in captured.out
        assert "Bob" in captured.out
        assert "Charlie" in captured.out
        assert "Diana" in captured.out

    def test_exits_on_missing_participants_file(self, tmp_path, monkeypatch):
        """Test that missing participants file causes exit."""
        couples_file = tmp_path / "couples.txt"
        couples_file.write_text("")

        monkeypatch.setattr(
            "sys.argv",
            [
                "secretsanta",
                "--participants",
                "/nonexistent/participants.txt",
                "--couples",
                str(couples_file),
            ],
        )

        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

    def test_exits_on_missing_couples_file(self, tmp_path, monkeypatch):
        """Test that missing couples file causes exit."""
        participants_file = tmp_path / "participants.txt"
        participants_file.write_text("Alice\nBob\nCharlie\n")

        monkeypatch.setattr(
            "sys.argv",
            [
                "secretsanta",
                "--participants",
                str(participants_file),
                "--couples",
                "/nonexistent/couples.txt",
            ],
        )

        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

    def test_exits_on_name_too_long(self, tmp_path, monkeypatch):
        """Test that name exceeding padding length causes exit."""
        participants_file = tmp_path / "participants.txt"
        participants_file.write_text("A\nB\nVeryLongNameThatExceedsLimit\n")

        couples_file = tmp_path / "couples.txt"
        couples_file.write_text("")

        monkeypatch.setattr(
            "sys.argv",
            [
                "secretsanta",
                "--participants",
                str(participants_file),
                "--couples",
                str(couples_file),
                "--padding-length",
                "16",
            ],
        )

        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

    def test_exits_on_impossible_constraints(self, tmp_path, monkeypatch):
        """Test that impossible constraints cause exit."""
        participants_file = tmp_path / "participants.txt"
        participants_file.write_text("Alice\nBob\n")

        couples_file = tmp_path / "couples.txt"
        couples_file.write_text("Alice,Bob\n")

        monkeypatch.setattr(
            "sys.argv",
            [
                "secretsanta",
                "--participants",
                str(participants_file),
                "--couples",
                str(couples_file),
                "--max-retries",
                "10",
            ],
        )

        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1
