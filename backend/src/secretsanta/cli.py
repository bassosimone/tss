"""Module containing the CLI."""

import argparse
import sys

from secretsanta.crypto import message_to_base64url_fragment
from secretsanta.readers import read_couples, read_participants
from secretsanta.pairings import PairingGenerationError, generate_valid_pairings


def _must_read_participants(filepath) -> list[str]:
    """Read the list of participants from file or exit."""
    try:
        participants = read_participants(filepath)
    except FileNotFoundError:
        print(f"Error: {filepath} not found")
        sys.exit(1)

    if len(participants) < 2:
        print("Error: Need at least 2 participants")
        sys.exit(1)

    return participants


def _validate_participant_names_or_exit(participants: list[str], padding_length: int):
    """Exit if any participant name is invalid."""
    max_name_length = max(len(name) for name in participants)
    if max_name_length > padding_length:
        print(f"Error: Name '{max(participants, key=len)}' is {max_name_length} chars")
        print(f"Maximum allowed length is {padding_length} characters")
        sys.exit(1)


def _must_read_couples(filepath: str) -> list[tuple[str, str]]:
    """Read the list of couples from file or exit."""
    try:
        couples = read_couples(filepath)
    except FileNotFoundError:
        print(f"Error: {filepath} not found")
        sys.exit(1)

    return couples


def _print_loaded_data(
    participants: list[str],
    couples: list[tuple[str, str]],
    padding_length: int,
):
    """Print information about the data we loaded"""
    print(f"Loaded {len(participants)} participants")
    if couples:
        print(f"Loaded {len(couples)} couple constraint(s)")
        for person1, person2 in couples:
            print(f"  - {person1} ↔ {person2}")
    print(f"Padding length: {padding_length} characters")
    print()


def _must_generate_pairings(
    participants: list[str],
    couples: list[tuple[str, str]],
    max_retries: int,
) -> list[tuple[str, str]]:
    """Generate the pairings with constraints or exit."""
    try:
        pairings, attempts = generate_valid_pairings(
            participants=participants,
            couples=couples,
            max_retries=max_retries,
        )
        print(f"Found valid pairings after {attempts} attempts")
        print()
        return pairings
    except PairingGenerationError as e:
        print(f"Error: {e}")
        print("Try again or check your constraints")
        sys.exit(1)


def _generate_urls(
    pairings: list[tuple[str, str]],
    base_url: str,
    padding_length: int,
) -> list[tuple[str, str, str]]:
    """
    Generate encrypted URLs for each pairing.

    Returns a list of tuples: [(giver, receiver, url), ...]
    """
    urls = []
    for giver, receiver in pairings:
        fragment = message_to_base64url_fragment(receiver, padding_length)
        url = f"{base_url}#{fragment}"
        urls.append((giver, receiver, url))
    return urls


def _print_urls(urls: list[tuple[str, str, str]], private: bool):
    """Print encrypted URLs in a format ready to send via WhatsApp."""
    for giver, receiver, url in urls:
        print("=" * 80)
        print()
        print(f"### {giver} -> {receiver}:\n") if not private else None
        print(f"Hi {giver}! Please find info about your receiver at: {url}")
        print()
        print("=" * 80)
        print()
        print()


def main():
    parser = argparse.ArgumentParser(description="Secret Santa pairing generator")
    parser.add_argument("--participants", default="../private/participants.txt")
    parser.add_argument("--couples", default="../private/couples.txt")
    parser.add_argument(
        "--base-url", default="https://bassosimone.github.io/secret-santa/"
    )
    parser.add_argument("--padding-length", type=int, default=32)
    parser.add_argument("--max-retries", type=int, default=1000)
    parser.add_argument("--debug", action="store_true", help="Show receiver names")

    args = parser.parse_args()

    participants = _must_read_participants(args.participants)
    _validate_participant_names_or_exit(participants, args.padding_length)
    couples = _must_read_couples(args.couples)
    _print_loaded_data(participants, couples, args.padding_length)
    pairings = _must_generate_pairings(participants, couples, args.max_retries)
    urls = _generate_urls(pairings, args.base_url, args.padding_length)
    _print_urls(urls, not args.debug)


if __name__ == "__main__":  # pragma: no cover
    main()
