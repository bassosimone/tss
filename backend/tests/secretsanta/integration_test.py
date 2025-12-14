"""Integration tests for backend encryption + frontend decryption."""

import pytest
from pathlib import Path

from secretsanta.crypto import message_to_base64url_fragment


@pytest.fixture
def frontend_path():
    """Path to the frontend HTML file."""
    backend_dir = Path(__file__).parent.parent.parent
    frontend_dir = backend_dir.parent / "frontend"
    html_path = frontend_dir / "index.html"

    if not html_path.exists():
        pytest.skip(f"Frontend not found at {html_path}")

    return html_path


class TestBackendFrontendIntegration:
    """Integration tests verifying backend encryption works with frontend decryption."""

    def test_decrypts_simple_name(self, page, frontend_path):
        """Test that frontend correctly decrypts a simple name."""
        # Generate encrypted fragment using backend
        name = "Alice"
        fragment = message_to_base64url_fragment(name)

        # Load frontend page with fragment
        page.goto(f"file://{frontend_path}#{fragment}")

        # Wait for and verify decrypted message appears
        message_element = page.locator("#message")
        assert message_element.text_content().strip() == name

    def test_decrypts_longer_name(self, page, frontend_path):
        """Test that frontend correctly decrypts a longer name."""
        name = "Christopher"
        fragment = message_to_base64url_fragment(name)

        page.goto(f"file://{frontend_path}#{fragment}")

        message_element = page.locator("#message")
        assert message_element.text_content().strip() == name

    def test_decrypts_name_with_spaces(self, page, frontend_path):
        """Test that frontend correctly decrypts a name with spaces."""
        name = "Alice Smith"
        fragment = message_to_base64url_fragment(name)

        page.goto(f"file://{frontend_path}#{fragment}")

        message_element = page.locator("#message")
        assert message_element.text_content().strip() == name

    def test_multiple_names_have_different_urls(self, page, frontend_path):
        """Test that different names produce different fragments."""
        fragment1 = message_to_base64url_fragment("Alice")
        fragment2 = message_to_base64url_fragment("Bob")

        # Fragments should be different (due to random keys)
        assert fragment1 != fragment2

        # But both should decrypt correctly
        page.goto(f"file://{frontend_path}#{fragment1}")
        assert page.locator("#message").text_content().strip() == "Alice"

        # Navigate to blank page first to force a fresh load
        page.goto("about:blank")
        page.goto(f"file://{frontend_path}#{fragment2}")
        assert page.locator("#message").text_content().strip() == "Bob"

    def test_all_urls_have_same_length(self, page, frontend_path):
        """Test that all URLs have the same length (due to padding)."""
        short_name = "Al"
        long_name = "Christopher"

        fragment1 = message_to_base64url_fragment(short_name)
        fragment2 = message_to_base64url_fragment(long_name)

        # Fragments should have equal length
        assert len(fragment1) == len(fragment2)

        # Verify both decrypt correctly
        page.goto(f"file://{frontend_path}#{fragment1}")
        assert page.locator("#message").text_content().strip() == short_name

        # Navigate to blank page first to force a fresh load
        page.goto("about:blank")
        page.goto(f"file://{frontend_path}#{fragment2}")
        assert page.locator("#message").text_content().strip() == long_name
