"""Module containing code for reading inputs."""


def read_participants(filepath):
    """Read participant names from file, one per line."""
    with open(filepath, "r") as filep:
        participants = [line.strip() for line in filep if line.strip()]
    return participants


def read_couples(filepath):
    """
    Read couples from file, one couple per line.

    Format: two names separated by comma.
    Returns a list of tuples: [(person1, person2), ...]
    """
    couples = []
    with open(filepath, "r") as filep:
        for line in filep:
            line = line.strip()
            if not line:
                continue
            parts = [p.strip() for p in line.split(",")]
            if len(parts) != 2:
                raise ValueError(f"Expected two entries, found {line}")
            couples.append((parts[0], parts[1]))
    return couples
