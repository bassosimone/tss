"""Tests for the secretsanta.crypto module"""

import base64
import json

from secretsanta.crypto import message_to_base64url_fragment


def _base64url_fragment_to_message(fragment):
    """
    Decrypt a base64url fragment back to the original message.

    This is primarily for testing purposes to verify round-trip
    encryption/decryption works correctly.
    """
    # Add padding back if needed
    while len(fragment) % 4:
        fragment += "="

    # Decode from base64url
    json_bytes = base64.urlsafe_b64decode(fragment)
    json_str = json_bytes.decode("utf-8")

    # Parse JSON payload
    payload = json.loads(json_str)

    if payload["v"] != 1:
        raise ValueError(f"Unsupported version: {payload['v']}")

    # Decode key and ciphertext from base64
    key = base64.b64decode(payload["k"])
    ciphertext = base64.b64decode(payload["c"])

    # XOR decrypt
    plaintext_bytes = bytes(a ^ b for a, b in zip(ciphertext, key))

    # Decode UTF-8 and trim padding
    plaintext = plaintext_bytes.decode("utf-8")
    return plaintext.strip()


class TestMessageToBase64URLFragment:
    """Tests for message_to_base64url_fragment function."""

    def test_result_is_base64url(self):
        """Test that encryption returns valid base64url string."""
        fragment = message_to_base64url_fragment("Alice", padding_length=32)

        # Base64url should only contain A-Z, a-z, 0-9, -, _
        valid_chars = set(
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
        )
        assert all(c in valid_chars for c in fragment)

    def test_same_message_different_keys(self):
        """Test that same message produces different ciphertexts (different keys)."""
        fragment1 = message_to_base64url_fragment("Alice", padding_length=32)
        fragment2 = message_to_base64url_fragment("Alice", padding_length=32)

        # Should be different due to random key
        assert fragment1 != fragment2

    def test_padding_produces_equal_length(self):
        """Test that padding produces equal-length ciphertexts."""
        short_name = message_to_base64url_fragment("Al", padding_length=32)
        long_name = message_to_base64url_fragment("Christopher", padding_length=32)

        # Both should produce same-length fragments
        assert len(short_name) == len(long_name)

    def test_padding_length_respected(self):
        """Test that different padding lengths produce different output sizes."""
        fragment_16 = message_to_base64url_fragment("Alice", padding_length=16)
        fragment_32 = message_to_base64url_fragment("Alice", padding_length=32)

        assert len(fragment_16) != len(fragment_32)
        assert len(fragment_32) > len(fragment_16)

    def test_round_trip(self):
        """
        Test that we can round-trip a message.

        If this test fails, it means we have broken the frontend.
        """
        expect = "Alice"
        fragment = message_to_base64url_fragment(expect)
        actual = _base64url_fragment_to_message(fragment)
        assert actual == expect
