# bunenv - Development Guide

> **Version**: 0.1.0 | **Python**: 3.8+ | **Build**: uv_build | **Updated**: 2025-11-23

---

## ⚡ Critical Rules

1. **ALWAYS use `uv`** - Never call `pip` or `python` directly
2. **ALWAYS use `uv run`** for commands - `uv run bunenv`, `uv run pytest`, etc.
3. **ALWAYS run quality checks** before committing - `uv run ruff check && uv run ruff format`
4. **NO breaking changes** without version bump - This is a stable package
5. **Test on multiple platforms** - macOS, Linux, Windows support required
6. **Credit nodeenv** - This is adapted from nodeenv, always acknowledge

---

## 🏗️ Architecture

**Single Package Structure**:
```
bunenv/
├── src/bunenv/__init__.py    # Main implementation (~1,235 lines)
├── pyproject.toml             # Project config (uv_build backend)
├── dist/                      # Built packages (gitignored)
└── .github/workflows/         # CI/CD automation
```

**Key Concepts**:
- **Single-file module** - All code in `src/bunenv/__init__.py`
- **Adapted from nodeenv** - Core architecture mirrors nodeenv's proven design
- **GitHub Releases API** - Fetches Bun versions (no versions.json like Node.js)
- **Prebuilt binaries only** - No source compilation (Bun is prebuilt-only)
- **Trusted publishing** - PyPI publishing via GitHub Actions OIDC

---

## 🚀 Quick Start Commands

### Setup

```bash
# Clone and install in development mode
git clone https://github.com/JacobCoffee/bunenv.git
cd bunenv
uv pip install -e .
```

### Development

```bash
# Run bunenv
uv run bunenv --help

# List Bun versions
uv run bunenv --list

# Create test environment
uv run bunenv /tmp/test-env --bun=latest

# Test activation
source /tmp/test-env/bin/activate
bun --version
deactivate_bun
```

### Quality Checks

```bash
# Lint
uv run ruff check src/

# Format
uv run ruff format src/

# Type check (future - not yet configured)
# uv run ty check

# All checks (run before commit)
uv run ruff check src/ && uv run ruff format --check src/
```

### Building

```bash
# Build package
uv build --no-sources

# Check built package
ls -lh dist/

# Test installation from wheel
uv pip install dist/bunenv-*.whl --force-reinstall
```

### Publishing

```bash
# Update version
uv version --bump patch  # or minor, major

# Build
uv build --no-sources

# Publish to PyPI (trusted publishing via GitHub Actions)
git commit -am "bump: version X.Y.Z"
git push
gh release create vX.Y.Z --generate-notes

# Or publish manually (requires PyPI token)
UV_PUBLISH_TOKEN='pypi-...' uv publish
```

---

## 📁 Project Structure

```
bunenv/
├── src/bunenv/
│   ├── __init__.py           # Main module (all code here)
│   └── py.typed              # PEP 561 marker
├── dist/                     # Built distributions (generated)
├── .github/workflows/
│   ├── ci.yml               # Tests on all platforms/Python versions
│   └── publish.yml          # Trusted publishing to PyPI
├── pyproject.toml           # Project metadata & build config
├── README.md                # Comprehensive user documentation
├── LICENSE                  # BSD-3-Clause (credits nodeenv)
└── .claude/
    └── CLAUDE.md            # This file
```

---

## 🔧 Technology Stack

| Component | Tool | Notes |
|-----------|------|-------|
| **Package Manager** | uv | Fast, modern Python package manager |
| **Build Backend** | uv_build | Native uv build backend |
| **Linting** | ruff | Fast Python linter & formatter |
| **Type Checking** | ty | Type checker (future integration) |
| **Git Hooks** | prek | Git hook manager (future integration) |
| **Testing** | pytest | Test framework (future integration) |
| **CI/CD** | GitHub Actions | Automated testing & publishing |
| **Publishing** | Trusted Publishing | OIDC-based PyPI publishing |

---

## 🔄 Development Workflow

### Making Changes

```bash
# 1. Create feature branch
git checkout -b feature/your-feature

# 2. Make changes to src/bunenv/__init__.py

# 3. Test locally
uv run bunenv /tmp/test-env --bun=latest

# 4. Run quality checks
uv run ruff check src/
uv run ruff format src/

# 5. Commit (descriptive message)
git commit -m "feat: add new feature"

# 6. Push and create PR
git push origin feature/your-feature
gh pr create
```

### Release Process

```bash
# 1. Update version
uv version --bump patch  # Updates pyproject.toml

# 2. Update CHANGELOG (manual)
# Document changes in release notes

# 3. Commit version bump
git commit -am "bump: version 0.1.1"
git push

# 4. Create release (triggers publish workflow)
gh release create v0.1.1 \
  --title "bunenv v0.1.1" \
  --notes "$(git log --oneline v0.1.0..HEAD)"

# 5. Workflow publishes to PyPI automatically via trusted publishing
```

---

## 🧪 Testing

### Manual Testing

```bash
# Test basic functionality
uv run bunenv /tmp/test --bun=latest
source /tmp/test/bin/activate
bun --version
deactivate_bun

# Test version listing
uv run bunenv --list | head

# Test specific version
uv run bunenv /tmp/test-1.3.0 --bun=1.3.0

# Test variants
uv run bunenv /tmp/test-baseline --bun=latest --variant=baseline
```

### Platform Testing (via CI)

The CI workflow tests on:
- **OS**: Ubuntu, macOS, Windows
- **Python**: 3.8, 3.9, 3.10, 3.11, 3.12, 3.13

### Future Test Suite

```bash
# Run tests (when implemented)
uv run pytest tests/

# Run with coverage
uv run pytest --cov=bunenv --cov-report=html
```

---

## 📝 Code Conventions

### Style Guidelines

- **Line length**: 120 characters
- **Imports**: Standard library → Third party → Local
- **Docstrings**: Keep existing nodeenv-style comments
- **Type hints**: Not required (maintains nodeenv compatibility)

### Naming Conventions

- Functions: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Variables: `snake_case`
- Classes: `PascalCase` (minimal - mostly functional code)

### Git Commit Messages

Follow Conventional Commits:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `build:` - Build system changes
- `ci:` - CI/CD changes
- `refactor:` - Code refactoring
- `bump:` - Version bumps

---

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| **Command not found: bunenv** | Use `uv run bunenv` instead |
| **GitHub API rate limits** | Use `--github-token` or set in `~/.bunenvrc` |
| **Bun binary not found** | Check platform/architecture support |
| **Build fails** | Ensure `uv_build>=0.9.11` installed |
| **Publish fails** | Verify trusted publisher configured on PyPI |

---

## 📚 Key Implementation Details

### Bun Version Discovery

```python
def _get_versions_json():
    """Fetch Bun versions from GitHub Releases API"""
    url = 'https://api.github.com/repos/oven-sh/bun/releases'
    # Returns list of releases, not index.json like Node.js
```

**Key Differences from nodeenv**:
- Node.js: `https://nodejs.org/dist/index.json`
- Bun: `https://api.github.com/repos/oven-sh/bun/releases`
- No LTS concept in Bun (yet)
- Rate limiting: 60 req/hr unauthenticated, 5000 with token

### Binary URL Construction

```python
# Bun format: bun-{platform}-{arch}[-variant].zip
# Example: bun-darwin-aarch64.zip, bun-linux-x64-musl.zip
```

**Architecture Mapping**:
- `arm64/ARM64` → `aarch64` (Bun uses aarch64, not arm64!)
- `x86_64/amd64` → `x64`

### Environment Variables

When activated, sets:
- `BUN_VIRTUAL_ENV` - Environment path
- `BUN_INSTALL` - Bun install directory
- `BUN_INSTALL_BIN` - Binary directory
- `PATH` - Prepended with bin directory

**Removed from nodeenv**:
- `NODE_PATH` (not needed for Bun)
- `NPM_CONFIG_PREFIX` (Bun is all-in-one)

---

## 🔗 Important Links

- **PyPI**: https://pypi.org/project/bunenv/
- **GitHub**: https://github.com/JacobCoffee/bunenv
- **Bun Docs**: https://bun.sh/docs
- **nodeenv** (original): https://github.com/ekalinin/nodeenv
- **Trusted Publishing**: https://docs.pypi.org/trusted-publishers/

---

## 🤝 Contributing Guidelines

1. **Open an issue first** - Discuss before implementing
2. **Follow existing patterns** - Code mirrors nodeenv structure
3. **Test on multiple platforms** - macOS, Linux, Windows
4. **Update documentation** - Keep README.md current
5. **Add examples** - Real-world usage scenarios
6. **Credit sources** - Always acknowledge nodeenv inspiration

---

## 🎯 Project Goals

**Primary Goal**: Provide isolated Bun environments like virtualenv for Python

**Secondary Goals**:
- ✅ Mirror nodeenv's proven architecture
- ✅ Support all Bun platforms (macOS, Linux, Windows)
- ✅ GitHub Releases API integration
- ✅ Cross-platform activation scripts
- ✅ Python virtualenv integration
- 🔄 Comprehensive test suite (future)
- 🔄 Type hints with ty (future)
- 🔄 Git hooks with prek (future)

---

## 📊 Maintenance Notes

### Dependencies

**Zero runtime dependencies!** Pure stdlib Python.

**Build dependencies**:
- `uv_build>=0.9.11,<0.10.0` - Build backend

### Version Support

- **Python**: 3.8+ (wide compatibility)
- **Bun**: All versions from GitHub Releases
- **Platforms**: macOS (Intel/ARM), Linux (glibc/musl), Windows

### Security

- No code execution during install
- Downloads verified from official Bun releases
- HTTPS-only communication
- Optional SSL cert verification (unsafe flag available)

---

## 🎓 Learning Resources

**Understanding the Codebase**:
1. Read nodeenv source first: https://github.com/ekalinin/nodeenv
2. Compare with bunenv to see adaptations
3. Study Bun release structure: https://github.com/oven-sh/bun/releases
4. Review activation script templates (ACTIVATE_SH, etc.)

**Key Files to Understand**:
- `src/bunenv/__init__.py` - Everything is here
- Lines 789-842: Version discovery (GitHub API)
- Lines 490-526: URL construction for Bun binaries
- Lines 908-1232: Activation script templates
- Lines 586-662: Installation logic

---

**Repository**: https://github.com/JacobCoffee/bunenv
**Based on**: [nodeenv](https://github.com/ekalinin/nodeenv) by Eugene Kalinin
