# Changelog

All notable changes to bunenv will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-24

### Added

#### GitHub Action
- **GitHub Action for CI/CD** - Official `JacobCoffee/bunenv` action for easy Bun setup in workflows
  - Simple one-line setup: `uses: JacobCoffee/bunenv@v1`
  - Automatic caching for faster runs
  - Cross-platform support (Ubuntu, macOS, Windows)
  - Inputs: `bun-version`, `variant`, `github-token`, `cache`, `python-version`
  - Outputs: `bun-version`, `bunenv-path`
  - Complete documentation in `ACTION.md`
  - Validated in production by byte project (#136)

#### Documentation
- **Comprehensive Sphinx Documentation** - Professional docs with Shibuya theme
  - Complete API reference with examples
  - User guides: quickstart, workflows, configuration, troubleshooting
  - Advanced topics: variants, GitHub API, security
  - Comparison with nodeenv, asdf, mise
  - Migration guides from nodeenv and other tools
  - Hosted at GitHub Pages

- **Makefile for Documentation** - Easy documentation builds
  - `make docs` - Build HTML documentation
  - `make docs-serve` - Live preview with auto-rebuild
  - `make docs-clean` - Remove build artifacts

#### Testing & Quality
- **Comprehensive Test Suite** - 98%+ coverage
  - Cross-platform tests (Ubuntu, macOS, Windows)
  - Python 3.10, 3.11, 3.12, 3.13 support
  - Integration tests with real Bun installations
  - Smoke tests for all platforms
  - Mocked tests for offline validation

- **Modern Tooling**
  - `ruff` for linting and formatting
  - `ty` for type checking
  - `prek` for git hooks
  - `codespell` for spelling
  - `pytest` with coverage reporting
  - Automated CI/CD via GitHub Actions

#### Development
- **Python 3.10+ Modernization**
  - Type hints throughout codebase
  - Pattern matching for cleaner code
  - Union types with `|` operator
  - Simplified Optional handling
  - Better error messages

### Changed
- **Version bump to 1.0.0** - Stable release!
- **Updated README** - Added GitHub Action usage examples
- **Improved CI/CD** - More comprehensive testing matrix

### Fixed
- **Documentation Build Warnings** - All Sphinx warnings resolved
- **Cross-Platform Compatibility** - Validated on all major platforms

### Validated
- **Real-World Usage** - Successfully migrated byte project from nodeenv
  - Production validation in https://github.com/JacobCoffee/byte
  - Zero breaking changes from nodeenv migration
  - CI passing with bunenv in production

---

## [0.1.0] - 2025-11-23

### Added
- Initial release of bunenv
- Core Bun virtual environment functionality
- Adapted from nodeenv architecture
- GitHub Releases API integration
- Cross-platform support (macOS, Linux, Windows)
- Python virtualenv integration
- Variant support (baseline, musl, profile)
- Configuration file support (~/.bunenvrc, .bun-version)
- Activation scripts for multiple shells
- Zero runtime dependencies

[1.0.0]: https://github.com/JacobCoffee/bunenv/compare/v0.1.0...v1.0.0
[0.1.0]: https://github.com/JacobCoffee/bunenv/releases/tag/v0.1.0
