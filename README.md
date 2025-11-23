# bunenv - Bun Virtual Environment

[![PyPI version](https://badge.fury.io/py/bunenv.svg)](https://badge.fury.io/py/bunenv)
[![Python Versions](https://img.shields.io/pypi/pyversions/bunenv.svg)](https://pypi.org/project/bunenv/)
[![License](https://img.shields.io/badge/license-BSD--3--Clause-blue.svg)](LICENSE)

Create isolated [Bun](https://bun.sh) environments, similar to Python's virtualenv. Inspired by and adapted from [nodeenv](https://github.com/ekalinin/nodeenv).

## Why bunenv?

- **Isolated Bun installations** - Keep different Bun versions per project
- **No global pollution** - Install packages without affecting system Bun
- **Easy version management** - Switch between Bun versions effortlessly
- **Python integration** - Works alongside Python virtual environments
- **Cross-platform** - Supports macOS, Linux, and Windows

## Installation

### Using uv (Recommended)

```bash
uv tool install bunenv
```

### Using pip

```bash
pip install bunenv
```

### From source

```bash
git clone https://github.com/JacobCoffee/bunenv.git
cd bunenv
uv pip install -e .
```

## Quick Start

### Create a Bun environment

```bash
# Create environment with latest Bun
bunenv myenv

# Create with specific version
bunenv myenv --bun=1.3.3

# List available Bun versions
bunenv --list
```

### Activate the environment

```bash
# On macOS/Linux
source myenv/bin/activate

# On Windows
myenv\Scripts\activate.bat
```

### Use Bun

```bash
bun --version          # Check version
bun init               # Initialize a project
bun add express        # Install packages
bun run index.ts       # Run scripts
```

### Deactivate

```bash
deactivate_bun
```

## Usage Examples

### Development Workflow

```bash
# Create project environment
bunenv .venv --bun=latest

# Activate
source .venv/bin/activate

# Your project is now using isolated Bun
bun install
bun run dev
```

### Multiple Projects, Different Versions

```bash
# Legacy project with Bun 1.0
bunenv ~/projects/legacy/.bunenv --bun=1.0.0
cd ~/projects/legacy
source .bunenv/bin/activate

# New project with latest Bun
bunenv ~/projects/new/.bunenv --bun=latest
cd ~/projects/new
source .bunenv/bin/activate
```

### CI/CD Integration

```yaml
# GitHub Actions example
- name: Setup Bun environment
  run: |
    pip install bunenv
    bunenv .bunenv --bun=1.3.3
    source .bunenv/bin/activate
    bun install
    bun test
```

### Python + Bun Projects

```bash
# Create Python virtualenv
python -m venv .venv
source .venv/bin/activate

# Install bunenv in the virtualenv
pip install bunenv

# Create Bun environment inside Python virtualenv
bunenv --python-virtualenv --bun=latest

# Now you have both Python and Bun isolated!
python --version
bun --version
```

## Command-Line Options

### Basic Options

```
bunenv [OPTIONS] DEST_DIR
```

| Option | Description |
|--------|-------------|
| `DEST_DIR` | Destination directory for the environment |
| `--version` | Show bunenv version |
| `-h, --help` | Show help message |

### Bun Version Options

| Option | Description |
|--------|-------------|
| `--bun=VERSION` | Specify Bun version (e.g., `1.3.3`, `latest`, `system`) |
| `--list, -l` | List all available Bun versions |
| `--variant=VARIANT` | Choose variant: `baseline`, `musl`, `profile` |

### Installation Options

| Option | Description |
|--------|-------------|
| `--mirror=URL` | Use alternative GitHub mirror for downloads |
| `--github-token=TOKEN` | GitHub API token (avoid rate limits) |
| `--prebuilt` | Install from prebuilt binaries (default, only option) |
| `--ignore_ssl_certs` | Ignore SSL certificate verification (unsafe) |

### Integration Options

| Option | Description |
|--------|-------------|
| `--python-virtualenv, -p` | Install into active Python virtualenv |
| `--requirements=FILE, -r` | Install packages from requirements file |
| `--clean-src, -c` | Remove downloaded files after installation |
| `--force` | Overwrite existing environment directory |

### Customization Options

| Option | Description |
|--------|-------------|
| `--prompt=PROMPT` | Custom shell prompt prefix |
| `--verbose, -v` | Verbose output |
| `--quiet, -q` | Minimal output |
| `--config-file=FILE, -C` | Use custom config file (default: `~/.bunenvrc`) |

## Configuration File

Create `~/.bunenvrc` to set defaults:

```ini
[bunenv]
bun = latest
variant =
github_token = ghp_xxxxxxxxxxxxx
ignore_ssl_certs = False
```

You can also use `.bun-version` file in your project:

```bash
echo "1.3.3" > .bun-version
bunenv .venv  # Will use version from .bun-version
```

## Requirements File

Create a `requirements.txt` with packages to install:

```
# requirements.txt
express
typescript
@types/node
```

Install with:

```bash
bunenv myenv --requirements=requirements.txt
```

## Platform Support

### Supported Platforms

- **macOS**: Intel (x64) and Apple Silicon (aarch64)
- **Linux**: x64, aarch64, with glibc or musl (Alpine, Void)
- **Windows**: x64

### Variants

| Variant | Description |
|---------|-------------|
| *default* | Optimized for modern CPUs (Haswell/Excavator+) |
| `baseline` | Compatible with older CPUs (Nehalem/Bulldozer+) |
| `musl` | For Alpine Linux, Void Linux (auto-detected) |
| `profile` | Debug/profiling build |

```bash
# Auto-detect best variant
bunenv myenv

# Force baseline for old CPU
bunenv myenv --variant=baseline

# Use musl on Alpine Linux (auto-detected)
bunenv myenv  # Will use musl variant automatically
```

## Environment Variables

When activated, bunenv sets:

- `BUN_VIRTUAL_ENV` - Path to the environment
- `BUN_INSTALL` - Bun install directory
- `BUN_INSTALL_BIN` - Binary installation directory
- `PATH` - Prepended with environment's bin directory

## Comparison with Other Tools

| Feature | bunenv | asdf | mise | Homebrew |
|---------|--------|------|------|----------|
| Isolated environments |  | L | L | L |
| Multiple versions simultaneously |  |  |  | L |
| Python integration |  | L | L | L |
| Cross-platform |  |  |  | L |
| No shell modification needed |  | L | L | N/A |

## Real-World Example: Byte Bot

The [Byte Bot](https://github.com/JacobCoffee/byte) project uses Bun for frontend tooling (TailwindCSS, Biome linter) alongside Python (uv). With bunenv:

```bash
# Setup isolated environment
bunenv .bunenv --bun=latest
source .bunenv/bin/activate

# Frontend development
bun install
bun run format    # Biome formatting
bun run lint      # Biome linting
```

## Troubleshooting

### GitHub API Rate Limits

If you see rate limit errors:

```bash
# Create a GitHub token (read-only, public repos)
# https://github.com/settings/tokens

# Use with bunenv
bunenv myenv --github-token=ghp_xxxxx

# Or set in ~/.bunenvrc
echo "github_token = ghp_xxxxx" >> ~/.bunenvrc
```

### Architecture Detection

On ARM systems:

```bash
# Bunenv auto-detects and uses aarch64 binaries
bunenv myenv  # Uses bun-darwin-aarch64 or bun-linux-aarch64

# Fallback to x64 if needed (Rosetta on macOS)
bunenv myenv --variant=baseline
```

### Alpine Linux / musl

```bash
# Auto-detected on Alpine/Void Linux
bunenv myenv  # Automatically uses bun-linux-x64-musl

# Force musl variant
bunenv myenv --variant=musl
```

## Development

### Running Tests

```bash
# Clone repository
git clone https://github.com/JacobCoffee/bunenv.git
cd bunenv

# Install development dependencies
uv sync

# Run tests
uv run pytest

# Run linter
uv run ruff check
```

### Building Documentation

```bash
# Install docs dependencies
uv sync --group docs

# Build docs
cd docs
uv run make html
```

## Differences from nodeenv

Bunenv is adapted from the excellent [nodeenv](https://github.com/ekalinin/nodeenv) project. Key differences:

| Feature | nodeenv | bunenv |
|---------|---------|--------|
| Runtime | Node.js | Bun |
| Package Manager | npm (separate) | Built-in |
| Distribution | nodejs.org | GitHub Releases |
| Source builds | Supported | Not available |
| LTS versions | Yes | Not yet |
| Version API | index.json | GitHub Releases API |

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

BSD-3-Clause License. See [LICENSE](LICENSE) for details.

Based on [nodeenv](https://github.com/ekalinin/nodeenv) by Eugene Kalinin.

## Acknowledgments

- **Eugene Kalinin** - Original [nodeenv](https://github.com/ekalinin/nodeenv) author
- **Oven.sh** - [Bun](https://bun.sh) runtime creators
- All contributors to nodeenv and bunenv

## Links

- **GitHub**: https://github.com/JacobCoffee/bunenv
- **PyPI**: https://pypi.org/project/bunenv/
- **Documentation**: https://bunenv.readthedocs.io/
- **Bun**: https://bun.sh
- **nodeenv**: https://github.com/ekalinin/nodeenv
