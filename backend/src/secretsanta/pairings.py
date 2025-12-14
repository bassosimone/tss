"""Module to generate the pairings and check for constraints."""

import secrets


class PairingGenerationError(Exception):
    """Raised when cannot generate valid pairings within max retries."""

    pass


def violates_couples_constraint(
    *,
    pairings: list[tuple[str, str]],
    couples: list[tuple[str, str]],
) -> bool:
    """
    Check if any pairing violates the couples constraint.

    Returns True if violation found, False otherwise.
    """
    for giver, receiver in pairings:
        for person1, person2 in couples:
            if giver == person1 and receiver == person2:
                return True
            if giver == person2 and receiver == person1:
                return True
    return False


def generate_pairings(participants: list[str]) -> list[tuple[str, str]]:
    """
    Generate Secret Santa pairings using cyclic derangement.

    Returns a list of tuples: [(giver, receiver), ...]
    """
    tot = len(participants)
    if tot < 2:
        raise ValueError("Need at least 2 participants")

    # Generate random displacement d where d ∈ {1, 2, ..., N-1}
    displacement = secrets.randbelow(tot - 1) + 1

    # Create pairings: participant[i] gives to participant[(i + d) mod N]
    pairings = []
    for i in range(tot):
        giver = participants[i]
        receiver = participants[(i + displacement) % tot]
        pairings.append((giver, receiver))

    return pairings


def generate_valid_pairings(
    *,
    participants: list[str],
    couples: list[tuple[str, str]],
    max_retries: int,
) -> tuple[list[tuple[str, str]], int]:
    """
    Generate pairings that respect couples constraints.

    Returns (pairings, attempts) on success.
    Raises PairingGenerationError on failure.
    """
    for attempt in range(max_retries):
        candidates = generate_pairings(participants)
        if not violates_couples_constraint(pairings=candidates, couples=couples):
            return (candidates, attempt + 1)

    raise PairingGenerationError(
        f"Could not generate valid pairings after {max_retries} attempts"
    )
