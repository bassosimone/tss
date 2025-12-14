"""Module to encode a message to a base64 URL fragment."""

import secrets
import json
import base64


def message_to_base64url_fragment(message, padding_length=32):
    """
    Encrypt a message using XOR with one-time pad and returns the
    corresponding base64url fragment for the frontend.

    The message is padded with spaces to padding_length to ensure
    all encrypted URLs have the same length (preventing length-based
    inference attacks). The frontend trims padding when displaying.
    """
    # Pad message to fixed length with spaces
    padded_message = message.ljust(padding_length)

    # Encode message to UTF-8 bytes
    message_bytes = padded_message.encode("utf-8")

    # Generate one-time pad using a key with same length as message
    key = secrets.token_bytes(len(message_bytes))

    # XOR encryption
    ciphertext = bytes(a ^ b for a, b in zip(message_bytes, key))

    # Create JSON payload
    payload = {
        "v": 1,
        "k": base64.b64encode(key).decode("ascii"),
        "c": base64.b64encode(ciphertext).decode("ascii"),
    }

    # Encode to the base64url format
    json_str = json.dumps(payload, separators=(",", ":"))
    fragment = base64.urlsafe_b64encode(json_str.encode("utf-8")).decode("ascii")
    fragment = fragment.rstrip("=")  # Remove padding

    return fragment
