# Setup Bun with bunenv - GitHub Action

[![GitHub Action](https://img.shields.io/badge/action-setup--bunenv-orange?logo=github)](https://github.com/JacobCoffee/bunenv)

A GitHub Action to set up [Bun](https://bun.sh) using [bunenv](https://github.com/JacobCoffee/bunenv) for isolated, reproducible environments in your CI/CD workflows.

## Why Use This Action?

- **Isolated Environments**: Each job gets its own Bun environment, just like Python's virtualenv
- **Version Pinning**: Lock to specific Bun versions for reproducible builds
- **Fast Caching**: Automatic caching of Bun installations across workflow runs
- **Cross-Platform**: Works on Ubuntu, macOS, and Windows runners
- **Zero Config**: Works out of the box with sensible defaults

## Quick Start

### Basic Usage (Latest Bun)

```yaml
steps:
  - uses: actions/checkout@v4

  - name: Setup Bun
    uses: JacobCoffee/bunenv@v1

  - name: Use Bun
    run: |
      bun --version
      bun install
      bun run build
```

### Specific Bun Version

```yaml
steps:
  - uses: actions/checkout@v4

  - name: Setup Bun 1.3.3
    uses: JacobCoffee/bunenv@v1
    with:
      bun-version: '1.3.3'

  - name: Run tests
    run: bun test
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `bun-version` | Bun version to install (e.g., "latest", "1.3.3") | No | `latest` |
| `variant` | Bun variant ("", "baseline", "musl", "profile") | No | `""` (auto-detect) |
| `github-token` | GitHub token for API requests | No | `${{ github.token }}` |
| `cache` | Enable caching of Bun installations | No | `true` |
| `python-version` | Python version for installing bunenv | No | `3.12` |

## Outputs

| Output | Description |
|--------|-------------|
| `bun-version` | The actual Bun version that was installed |
| `bunenv-path` | Path to the bunenv environment directory |

## Examples

### Matrix Testing with Multiple Bun Versions

```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        bun-version: ['latest', '1.3.3', '1.3.0']

    steps:
      - uses: actions/checkout@v4

      - name: Setup Bun ${{ matrix.bun-version }}
        uses: JacobCoffee/bunenv@v1
        with:
          bun-version: ${{ matrix.bun-version }}

      - name: Run tests
        run: bun test
```

### Cross-Platform Testing

```yaml
name: Cross-Platform

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]

    steps:
      - uses: actions/checkout@v4

      - name: Setup Bun
        uses: JacobCoffee/bunenv@v1
        with:
          bun-version: 'latest'

      - name: Build
        run: bun run build

      - name: Test
        run: bun test
```

### Using with Python (Polyglot Project)

```yaml
name: Polyglot Build

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Setup Bun
        uses: JacobCoffee/bunenv@v1
        with:
          bun-version: 'latest'

      - name: Install Python dependencies
        run: pip install -r requirements.txt

      - name: Install frontend dependencies
        run: bun install

      - name: Build frontend
        run: bun run build

      - name: Run Python tests
        run: pytest

      - name: Run frontend tests
        run: bun test
```

### Specific Variant (Older CPUs)

```yaml
steps:
  - uses: actions/checkout@v4

  - name: Setup Bun (baseline variant)
    uses: JacobCoffee/bunenv@v1
    with:
      bun-version: 'latest'
      variant: 'baseline'  # For older CPUs without AVX2

  - name: Build
    run: bun run build
```

### Alpine Linux (musl variant)

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    container:
      image: alpine:latest

    steps:
      - uses: actions/checkout@v4

      - name: Install dependencies
        run: apk add --no-cache python3 py3-pip

      - name: Setup Bun (musl variant)
        uses: JacobCoffee/bunenv@v1
        with:
          bun-version: 'latest'
          variant: 'musl'  # Required for Alpine/musl

      - name: Build
        run: bun run build
```

### Disable Caching

```yaml
steps:
  - uses: actions/checkout@v4

  - name: Setup Bun (no cache)
    uses: JacobCoffee/bunenv@v1
    with:
      bun-version: 'latest'
      cache: 'false'  # Disable caching

  - name: Build
    run: bun run build
```

### Using Outputs

```yaml
steps:
  - uses: actions/checkout@v4

  - name: Setup Bun
    id: setup-bun
    uses: JacobCoffee/bunenv@v1
    with:
      bun-version: 'latest'

  - name: Display Bun version
    run: echo "Using Bun ${{ steps.setup-bun.outputs.bun-version }}"

  - name: Display bunenv path
    run: echo "Bunenv at ${{ steps.setup-bun.outputs.bunenv-path }}"
```

### Avoid GitHub API Rate Limits

```yaml
steps:
  - uses: actions/checkout@v4

  - name: Setup Bun with token
    uses: JacobCoffee/bunenv@v1
    with:
      bun-version: 'latest'
      github-token: ${{ secrets.GITHUB_TOKEN }}  # Increases rate limit
```

## Caching

The action automatically caches Bun installations to speed up subsequent workflow runs. The cache key is based on:

- Operating system (`ubuntu-latest`, `macos-latest`, `windows-latest`)
- Architecture (`X64`, `ARM64`)
- Bun version
- Bun variant

Cache is stored in `~/.bunenv-cache` and shared across workflow runs.

To disable caching, set `cache: 'false'`.

## Bun Variants

Bun provides different binary variants for specific use cases:

| Variant | Use Case |
|---------|----------|
| `` (default) | Modern CPUs with AVX2 support |
| `baseline` | Older CPUs without AVX2 |
| `musl` | Alpine Linux and musl-based distros |
| `profile` | Profiling and performance analysis |

The action auto-detects the appropriate variant, but you can override with the `variant` input.

## Comparison with Other Actions

| Feature | This Action | oven-sh/setup-bun | Direct Install |
|---------|-------------|-------------------|----------------|
| Isolated Environments | ✅ | ❌ | ❌ |
| Version Pinning | ✅ | ✅ | ❌ |
| Caching | ✅ | ✅ | ❌ |
| Variant Selection | ✅ | ✅ | ❌ |
| Python Integration | ✅ | ❌ | ❌ |
| Based on nodeenv | ✅ | ❌ | ❌ |

**Use This Action When:**
- You want isolated Bun environments (like Python's virtualenv)
- You're building polyglot projects (Python + Bun)
- You need reproducible builds with locked versions
- You're familiar with nodeenv and want the same for Bun

**Use oven-sh/setup-bun When:**
- You just need Bun installed globally
- You don't need environment isolation
- You want official Bun support

## Troubleshooting

### Action Fails to Install Bun

**Issue**: `bunenv` command fails or times out

**Solutions**:
1. Check if the Bun version exists: https://github.com/oven-sh/bun/releases
2. For pre-releases, use exact version from releases (e.g., `1.3.3-canary.1`)
3. Add `github-token` input to avoid rate limits

### Bun Not Found in PATH

**Issue**: `bun: command not found` after setup

**Solutions**:
1. Ensure you're running commands after the setup step
2. Check workflow logs for activation errors
3. Verify the runner OS is supported (Ubuntu, macOS, Windows)

### Wrong Bun Version

**Issue**: Wrong Bun version is installed

**Solutions**:
1. Clear GitHub Actions cache for your repository
2. Specify exact version instead of `latest`
3. Check if caching is causing issues (try `cache: 'false'`)

### Alpine/musl Issues

**Issue**: Bun doesn't work on Alpine Linux

**Solutions**:
1. Explicitly set `variant: 'musl'`
2. Ensure Python 3 is installed in the container
3. Use `apk add --no-cache python3 py3-pip`

## Advanced Usage

### Install Additional Dependencies

```yaml
steps:
  - uses: actions/checkout@v4

  - name: Setup Bun
    uses: JacobCoffee/bunenv@v1

  - name: Install global tools
    run: |
      bun add -g typescript@latest
      bun add -g @biomejs/biome
```

### Custom bunenv Cache Location

```yaml
steps:
  - uses: actions/checkout@v4

  - name: Setup Bun with custom cache
    uses: JacobCoffee/bunenv@v1
    with:
      bun-version: 'latest'
    env:
      BUNENV_CACHE: ${{ github.workspace }}/.bunenv-cache
```

## Contributing

Found a bug or want to add a feature? Contributions are welcome!

1. Open an [issue](https://github.com/JacobCoffee/bunenv/issues) to discuss
2. Fork and create a branch
3. Make your changes
4. Test with the example workflows
5. Submit a pull request

## License

BSD-3-Clause - see [LICENSE](LICENSE) file

## Credits

- Based on [bunenv](https://github.com/JacobCoffee/bunenv) by Jacob Coffee
- Inspired by [nodeenv](https://github.com/ekalinin/nodeenv) by Eugene Kalinin
- Bun by [Oven.sh](https://oven.sh)

## Links

- **bunenv**: https://github.com/JacobCoffee/bunenv
- **bunenv on PyPI**: https://pypi.org/project/bunenv/
- **Bun**: https://bun.sh
- **Bun Releases**: https://github.com/oven-sh/bun/releases
