"""Trusted Secret Santa pairing generator.

This package generates Secret Santa pairings and encrypts them into
unique URLs for distribution. Each URL contains an encrypted fragment
that decrypts client-side to reveal the recipient's name.

Key components:
- Pairing generation using cyclic derangement algorithm
- Couples constraint support (prevents partners from giving to each other)
- XOR one-time pad encryption with fixed-length padding
- CLI tool for generating encrypted URLs from participant lists

The system is "trusted" because the organizer runs the pairing algorithm
locally and can verify assignments, but encryption provides "obfuscation
through effort" to discourage casual viewing after distribution.

Input files:
- participants.txt: One name per line
- couples.txt: Comma-separated pairs

Output:
- Encrypted URLs containing pairing assignments for each participant
"""
