#!/usr/bin/env python3

import secrets
import json
import base64
import sys


def encrypt_message(message, padding_length=32):
    """
    Encrypt a message using XOR with one-time pad.

    The message is padded with spaces to padding_length to ensure
    all encrypted URLs have the same length (preventing length-based
    inference attacks). The frontend trims the padding when displaying.
    """
    # Pad message to fixed length with spaces
    padded_message = message.ljust(padding_length)

    # Encode message to UTF-8 bytes
    message_bytes = padded_message.encode('utf-8')

    # Generate one-time pad (key same length as message)
    key = secrets.token_bytes(len(message_bytes))

    # XOR encryption
    ciphertext = bytes(a ^ b for a, b in zip(message_bytes, key))

    # Create JSON payload
    payload = {
        "v": 1,
        "k": base64.b64encode(key).decode('ascii'),
        "c": base64.b64encode(ciphertext).decode('ascii')
    }

    # Encode to base64url
    json_str = json.dumps(payload, separators=(',', ':'))
    fragment = base64.urlsafe_b64encode(json_str.encode('utf-8')).decode('ascii')
    fragment = fragment.rstrip('=')  # Remove padding

    return fragment


def read_participants(filepath):
    """Read participant names from file, one per line."""
    with open(filepath, 'r') as f:
        participants = [line.strip() for line in f if line.strip()]
    return participants


def read_couples(filepath):
    """
    Read couples from file, one couple per line.

    Format: two names separated by whitespace or comma.
    Returns a list of tuples: [(person1, person2), ...]
    """
    couples = []
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                # Split by comma or whitespace
                parts = [p.strip() for p in line.replace(',', ' ').split()]
                if len(parts) == 2:
                    couples.append((parts[0], parts[1]))
                else:
                    print(f"Warning: Skipping invalid couple line: {line}")
    except FileNotFoundError:
        # No couples file is fine - no constraints
        pass
    return couples


def violates_couples_constraint(pairings, couples):
    """
    Check if any pairing violates the couples constraint.

    Returns True if violation found, False otherwise.
    """
    for giver, receiver in pairings:
        for person1, person2 in couples:
            # Check both directions (A→B and B→A are both violations)
            if (giver == person1 and receiver == person2) or \
               (giver == person2 and receiver == person1):
                return True
    return False


def generate_pairings(participants):
    """
    Generate Secret Santa pairings using cyclic derangement.

    Returns a list of tuples: [(giver, receiver), ...]
    """
    n = len(participants)
    if n < 2:
        raise ValueError("Need at least 2 participants")

    # Generate random displacement d where d ∈ {1, 2, ..., N-1}
    displacement = secrets.randbelow(n - 1) + 1

    # Create pairings: participant[i] gives to participant[(i + d) mod N]
    pairings = []
    for i in range(n):
        giver = participants[i]
        receiver = participants[(i + displacement) % n]
        pairings.append((giver, receiver))

    return pairings


def generate_urls(pairings, base_url, padding_length):
    """
    Generate encrypted URLs for each pairing.

    Returns a list of tuples: [(giver, receiver, url), ...]
    """
    urls = []
    for giver, receiver in pairings:
        fragment = encrypt_message(receiver, padding_length)
        url = f"{base_url}#{fragment}"
        urls.append((giver, receiver, url))
    return urls


def print_urls(urls):
    """Print encrypted URLs in a format ready to send via WhatsApp."""
    print("ENCRYPTED URLs (send these via WhatsApp):")
    print("=" * 80)
    print()

    for giver, receiver, url in urls:
        print(f"{giver}:")
        print(f"  {url}")
        print()


def main():
    participants_file = '../private/participants.txt'
    couples_file = '../private/couples.txt'
    base_url = 'https://bassosimone.github.io/secret-santa/'
    padding_length = 32
    max_retries = 1000

    # Read participants
    try:
        participants = read_participants(participants_file)
    except FileNotFoundError:
        print(f"Error: {participants_file} not found")
        sys.exit(1)

    if len(participants) < 2:
        print("Error: Need at least 2 participants")
        sys.exit(1)

    # Check for names that are too long
    max_name_length = max(len(name) for name in participants)
    if max_name_length > padding_length:
        print(f"Error: Name '{max(participants, key=len)}' is {max_name_length} chars")
        print(f"Maximum allowed length is {padding_length} characters")
        sys.exit(1)

    # Read couples constraints
    couples = read_couples(couples_file)

    print(f"Loaded {len(participants)} participants")
    if couples:
        print(f"Loaded {len(couples)} couple constraint(s)")
        for person1, person2 in couples:
            print(f"  - {person1} ↔ {person2}")
    print(f"Padding length: {padding_length} characters")
    print()

    # Generate pairings with couples constraint
    pairings = None
    for attempt in range(max_retries):
        candidate_pairings = generate_pairings(participants)
        if not violates_couples_constraint(candidate_pairings, couples):
            pairings = candidate_pairings
            if attempt > 0:
                print(f"Found valid pairings after {attempt + 1} attempts")
                print()
            break

    if pairings is None:
        print(f"Error: Could not generate valid pairings after {max_retries} attempts")
        print("Try again or check your constraints")
        sys.exit(1)

    # Print plaintext pairings for verification
    print("PLAINTEXT PAIRINGS (for verification):")
    print("=" * 80)
    for giver, receiver in pairings:
        print(f"{giver} → {receiver}")
    print()

    # Generate encrypted URLs (but don't print them yet)
    # urls = generate_urls(pairings, base_url, padding_length)
    # print_urls(urls)


if __name__ == '__main__':
    main()
