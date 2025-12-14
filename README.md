# Trusted Secret Santa (TSS)

[![Build Status](https://github.com/bassosimone/tss/actions/workflows/ci.yml/badge.svg)](https://github.com/bassosimone/tss/actions) [![codecov](https://codecov.io/gh/bassosimone/tss/branch/main/graph/badge.svg)](https://codecov.io/gh/bassosimone/tss)

Privacy-conscious Secret Santa pairing generator
with client-side decryption.

![All Secret Santas are belong to us!](docs/mascot.png)

## Overview

TSS generates Secret Santa pairings and delivers them
via encrypted URLs. The organizer can verify pairings are
correct, but the encryption provides "obfuscation
through effort" to discourage from seeing the assignments.

**Key features:**

- 🔐 Client-side decryption (no backend server)

- 🔄 Cyclic derangement algorithm (everyone connected in one chain)

- 💑 Couples constraint (prevent partners from giving to each other)

- 📏 Fixed-length padding (URLs are all the same length)

- 🔑 XOR one-time pad encryption (provably secure)

## Architecture

```
.
├── frontend/                 # Static decryption page (GitHub Pages)
│   └── index.html            # JavaScript client-side decryptor
├── backend/                  # Python pairing generator (runs locally)
│   ├── src/
│   │   └── secretsanta/
│   │       ├── cli.py        # CLI entry point
│   │       ├── crypto.py     # XOR encryption
│   │       ├── pairings.py   # Cyclic derangement + constraints
│   │       └── readers.py    # File I/O
│   └── tests/                # Comprehensive test suite
└── private/                  # Your participant data (gitignored)
    ├── participants.txt      # List of names
    └── couples.txt           # Couple constraints
```

## Quick Start

### 1. Setup

Install dependencies (requires Python 3.8+):

```bash
cd backend
uv sync
```

### 2. Prepare participant data

Copy templates and edit with your data:

```bash
cp private/participants.txt.template private/participants.txt
cp private/couples.txt.template private/couples.txt
```

Edit `private/participants.txt`. For example:

```
Alice
Bob
Charlie
Diana
```

Edit `private/couples.txt`. For example:
```
Alice,Bob
Charlie,Diana
```

### 3. Generate pairings

```bash
cd backend
uv run secretsanta
```

This will:

1. Load participants and couples

2. Generate valid pairings (retrying if couples constraint violated)

3. Output encrypted URLs for each participant

### 4. Distribute URLs

Send each person their unique URL via WhatsApp, email,
etc. They click it to see their assignment.

## Frontend Deployment

The frontend is a static HTML page hosted on GitHub Pages
using the following URL by default:

**URL**: `https://bassosimone.github.io/secret-santa/`

To deploy updates:

1. Edit `frontend/index.html`

2. Test locally

3. Copy to https://github.com/bassosimone/bassosimone.github.io

4. Commit and push

5. GitHub Pages will automatically deploy

### Testing the frontend locally

```bash
# Open in browser
open frontend/index.html

# Or use a local server
python3 -m http.server 8000 --directory frontend
# Then visit: http://localhost:8000#<encrypted-fragment>
```

## Backend Development

### Running the CLI

```bash
cd backend

# Basic usage (uses default paths)
uv run secretsanta

# Custom options
uv run secretsanta --participants ../private/my-participants.txt \
                   --couples ../private/my-couples.txt \
                   --max-retries 500

# Show receiver names (for debugging)
uv run secretsanta --debug

# Help
uv run secretsanta --help
```

### Development Setup

If you want to run tests or contribute to development:

```bash
cd backend

# Install development dependencies
uv sync --dev

# Install Playwright browsers (for integration tests)
uv run playwright install chromium
```

### Running tests

```bash
cd backend

# Run all tests (including integration tests with Playwright)
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/secretsanta/pairings_test.py

# Run with coverage
uv run pytest --cov=secretsanta
```

### Code quality checks

```bash
cd backend

# Type checking (pyright)
uv run pyright

# Format code
uv run ruff format

# Lint and auto-fix
uv run ruff check --fix
```

## How It Works

### Pairing Algorithm

Uses **cyclic derangement via random displacement**:

1. Generate random displacement `d` where `d ∈ {1, 2, ..., N-1}`

2. Each `participant[i]` gives to `participant[(i + d) mod N]`

3. Creates one connected chain through all participants

This ensures:

- No one gives to themselves

- Everyone appears exactly once as giver and receiver

- Forms a single cycle (no disconnected sub-groups)

### Couples Constraint

If participants A and B are a couple:

- Retry pairing generation until neither A→B nor B→A

- Typically succeeds within 1-5 attempts for reasonable group sizes

### Encryption

For each participant:

1. **Pad name** to fixed length (32 characters) with spaces

2. **Generate random key** (32 bytes, same length as padded message)

3. **XOR encrypt**: `ciphertext = plaintext ⊕ key`

4. **Create JSON payload**: `{"v": 1, "k": base64(key), "c": base64(ciphertext)}`

5. **Encode to URL**: `https://.../#base64url(JSON)`

Security properties:

- One-time pad provides perfect secrecy

- Fixed-length padding prevents name length inference

- Each URL has 256 bits of entropy (unguessable)

- URL fragments (#) don't appear in server logs

### Frontend Decryption

The frontend JavaScript:

1. Extracts URL fragment (after `#`)

2. Decodes base64url → JSON

3. Extracts key and ciphertext

4. XOR decrypts: `plaintext = ciphertext ⊕ key`

5. Trims padding and displays name

**No server-side processing** - everything happens in the browser.

## Privacy Model

**Threat model:**

✅ Prevents organizer from casually viewing pairings after distribution

✅ Participants cannot guess each other's assignments

✅ URLs are not predictable

❌ Does NOT protect against organizer deliberately clicking all URLs

❌ Does NOT protect against organizer during generation (they run the algorithm)

❌ System relies on organizer's self-restraint (hence "trusted")

This is **intentional** - the organizer is trusted to run the
process fairly. The encryption provides "obfuscation through
effort" to prevent accidental viewing.

## File Formats

### participants.txt

One name per line (ASCII recommended):

```
Alice
Bob
Charlie
```

Max name length: 32 characters (configurable via `--padding-length`)

### couples.txt

One couple per line (comma separated):

```
Charlie,Diana
```

## Testing Philosophy

The test suite follows these principles:

1. **Library code is well-tested** (crypto, pairings, readers)

2. **CLI is thin orchestration** (just translates exceptions to exit codes)

3. **Round-trip tests verify frontend compatibility** (decrypt function
in tests acts as contract specification)

4. **Generic fixtures** (Alice, Bob, etc. - safe for public repo)

## Contributing

This is a personal project for a specific use case, but you're welcome to:

1. Report issues

2. Suggest improvements

3. Fork

## License

```
SPDX-License-Identified: MIT
```

See the [LICENSE](LICENSE) file.

## See Also

- [backend/pyproject.toml](backend/pyproject.toml) - Package configuration
- [frontend/index.html](frontend/index.html) - Decryption implementation
