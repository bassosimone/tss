"""Module to generate the pairings and check for constraints."""

import secrets


def violates_couples_constraint(pairings, couples):
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


def generate_pairings(participants):
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
