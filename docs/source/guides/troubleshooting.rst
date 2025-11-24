Troubleshooting
===============

Having issues with bunenv? This guide covers common problems and their solutions.

Quick Diagnostics
-----------------

Before diving into specific issues, run these diagnostic commands:

.. code-block:: bash

   # Check bunenv version
   bunenv --version

   # Check Python version
   python --version  # Should be 3.10+

   # Check platform
   uname -sm  # macOS/Linux
   # or
   echo %OS%  # Windows

   # Try verbose mode
   bunenv .venv --verbose --bun=latest

Installation Issues
-------------------

bunenv Command Not Found
~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom**:

.. code-block:: bash

   $ bunenv --version
   bash: bunenv: command not found

**Solutions**:

**Option 1: Check Python scripts directory**

.. code-block:: bash

   # Find where pip installed bunenv
   python -m pip show -f bunenv

   # Make sure scripts directory is in PATH
   echo $PATH | grep -o "$(python -m site --user-base)/bin"

**Option 2: Use python -m**

.. code-block:: bash

   # Run as module instead
   python -m bunenv --version

**Option 3: Reinstall with pipx**

.. code-block:: bash

   pipx install bunenv

**Option 4: Fix PATH (Linux/macOS)**

.. code-block:: bash

   # Add to ~/.bashrc or ~/.zshrc
   export PATH="$HOME/.local/bin:$PATH"

   # Reload shell
   source ~/.bashrc

**Option 5: Fix PATH (Windows)**

.. code-block:: powershell

   # Add Python Scripts to PATH
   $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
   $scriptsPath = python -c "import sysconfig; print(sysconfig.get_path('scripts', 'nt_user'))"
   [Environment]::SetEnvironmentVariable("Path", "$userPath;$scriptsPath", "User")

Permission Denied During Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom**:

.. code-block:: bash

   ERROR: Could not install packages due to an EnvironmentError: [Errno 13] Permission denied

**Solutions**:

**DON'T use sudo** - use user install instead:

.. code-block:: bash

   # User install (recommended)
   pip install --user bunenv

   # Or use virtualenv
   python -m venv .venv
   source .venv/bin/activate
   pip install bunenv

Environment Creation Issues
---------------------------

GitHub API Rate Limit Exceeded
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom**:

.. code-block:: text

   HTTP Error 403: rate limit exceeded

**Cause**: GitHub limits unauthenticated requests to 60/hour.

**Solutions**:

**Option 1: Create GitHub token** (recommended)

.. code-block:: bash

   # 1. Create token at https://github.com/settings/tokens
   #    No scopes needed for public repos

   # 2. Use it
   bunenv .venv --github-token=ghp_your_token_here

   # 3. Or save in config
   echo "github_token = ghp_your_token_here" >> ~/.bunenvrc

**Option 2: Wait for rate limit reset**

.. code-block:: bash

   # Check when limit resets
   curl https://api.github.com/rate_limit

**Option 3: Use specific version** (doesn't check latest)

.. code-block:: bash

   bunenv .venv --bun=1.3.3  # Skips version lookup

Download Failed or Incomplete
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom**:

.. code-block:: text

   IncompleteRead error
   Failed to download from https://github.com/...

**Solutions**:

**Option 1: Retry** (bunenv retries 3 times automatically)

.. code-block:: bash

   bunenv .venv --bun=1.3.3

**Option 2: Check internet connection**

.. code-block:: bash

   # Test GitHub connectivity
   curl -I https://github.com/oven-sh/bun/releases

**Option 3: Use mirror** (if behind corporate proxy)

.. code-block:: bash

   bunenv .venv --mirror=https://your-mirror.com/bun/releases

**Option 4: Disable SSL verification** (UNSAFE - last resort)

.. code-block:: bash

   bunenv .venv --ignore_ssl_certs

Platform or Architecture Not Supported
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom**:

.. code-block:: text

   Failed to download: 404 Not Found
   Could not find Bun binary for platform

**Solutions**:

**Check platform support**:

.. code-block:: bash

   # macOS: Intel, ARM (M1/M2/M3)
   # Linux: x64, aarch64 (glibc and musl)
   # Windows: x64

   # Check your architecture
   uname -m  # Linux/macOS
   echo %PROCESSOR_ARCHITECTURE%  # Windows

**For unsupported platforms**:

1. Use Docker with supported platform
2. Compile Bun from source (not via bunenv)
3. Use system Bun if available

Directory Already Exists
~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom**:

.. code-block:: text

   Environment already exists: .venv

**Solutions**:

**Option 1: Use different name**

.. code-block:: bash

   bunenv .venv-new --bun=1.3.3

**Option 2: Remove existing**

.. code-block:: bash

   rm -rf .venv
   bunenv .venv --bun=1.3.3

**Option 3: Force overwrite**

.. code-block:: bash

   bunenv .venv --bun=1.3.3 --force

Bun Binary Not Found After Install
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom**:

.. code-block:: bash

   $ source .venv/bin/activate
   (venv) $ bun --version
   bash: bun: command not found

**Diagnostic**:

.. code-block:: bash

   # Check if binary exists
   ls -la .venv/bin/bun

   # Check if executable
   file .venv/bin/bun

**Solutions**:

**If binary missing**:

.. code-block:: bash

   # Recreate environment
   rm -rf .venv
   bunenv .venv --bun=1.3.3 --verbose

**If not executable**:

.. code-block:: bash

   chmod +x .venv/bin/bun

**If wrong architecture**:

.. code-block:: bash

   # Check binary architecture
   file .venv/bin/bun
   # Should match your system architecture

   # Force correct variant
   bunenv .venv --bun=1.3.3 --variant=baseline

Activation Issues
-----------------

Activation Script Not Found
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom**:

.. code-block:: bash

   bash: .venv/bin/activate: No such file or directory

**Solutions**:

.. code-block:: bash

   # Check environment was created successfully
   ls -la .venv/

   # Recreate if incomplete
   rm -rf .venv
   bunenv .venv --bun=1.3.3

Activation Doesn't Change PATH
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom**:

.. code-block:: bash

   $ source .venv/bin/activate
   (venv) $ which bun
   /usr/local/bin/bun  # Still system Bun!

**Solutions**:

**Check activation actually ran**:

.. code-block:: bash

   echo $BUN_VIRTUAL_ENV
   # Should show path to .venv

**If empty, try explicit source**:

.. code-block:: bash

   source /absolute/path/to/.venv/bin/activate

**Check shell compatibility**:

.. code-block:: bash

   # bash/zsh
   source .venv/bin/activate

   # fish
   source .venv/bin/activate.fish

   # Windows PowerShell
   .venv\Scripts\Activate.ps1

   # Windows cmd
   .venv\Scripts\activate.bat

Prompt Doesn't Change After Activation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom**: No ``(venv)`` prefix after activation

**Cause**: Might be disabled or custom prompt

**Solutions**:

.. code-block:: bash

   # Check if disabled
   echo $BUN_VIRTUAL_ENV_DISABLE_PROMPT

   # If "1", prompt is intentionally disabled
   # To enable, unset before activating:
   unset BUN_VIRTUAL_ENV_DISABLE_PROMPT
   source .venv/bin/activate

**Or check if activated another way**:

.. code-block:: bash

   # Even without prompt change, check:
   echo $BUN_VIRTUAL_ENV
   which bun

Can't Deactivate Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom**:

.. code-block:: bash

   (venv) $ deactivate_bun
   bash: deactivate_bun: command not found

**Solutions**:

**Try alternative**:

.. code-block:: bash

   # Some shells use different command
   deactivate  # Python virtualenv style

**Manual deactivation**:

.. code-block:: bash

   # Restore PATH manually
   export PATH=$_OLD_BUN_VIRTUAL_PATH
   unset BUN_VIRTUAL_ENV
   unset BUN_INSTALL
   unset BUN_INSTALL_BIN

**Or just start new shell**:

.. code-block:: bash

   exec $SHELL

Usage Issues
------------

Bun Commands Fail After Activation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom**:

.. code-block:: bash

   (venv) $ bun --version
   Segmentation fault

**Solutions**:

**Wrong variant for CPU**:

.. code-block:: bash

   # Try baseline variant
   deactivate_bun
   rm -rf .venv
   bunenv .venv --variant=baseline

**Check CPU compatibility**:

.. code-block:: bash

   # Linux
   grep -o 'avx2' /proc/cpuinfo

   # If no avx2, use baseline

**musl vs glibc mismatch**:

.. code-block:: bash

   # Check your libc
   ldd --version

   # Alpine/Void need musl variant
   bunenv .venv --variant=musl

Package Installation Fails
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom**:

.. code-block:: bash

   (venv) $ bun add express
   error: ENOENT: no such file or directory

**Solutions**:

**Make sure in project directory**:

.. code-block:: bash

   # Bun needs package.json
   bun init  # Create one if missing
   bun add express

**Check disk space**:

.. code-block:: bash

   df -h .

**Check permissions**:

.. code-block:: bash

   # Make sure you own the directory
   ls -la .

System Bun vs Environment Bun Conflict
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom**: Wrong Bun version running

**Solutions**:

.. code-block:: bash

   # Check which Bun is active
   which bun
   # Should be: /path/to/.venv/bin/bun

   # If not, check activation
   echo $BUN_VIRTUAL_ENV

   # Reactivate
   deactivate_bun
   source .venv/bin/activate

Platform-Specific Issues
-------------------------

macOS Issues
~~~~~~~~~~~~

**M1/M2/M3 (ARM) Issues**:

.. code-block:: bash

   # If getting x64 binary on ARM Mac:
   # Check architecture detection
   uname -m  # Should show "arm64"

   # Force ARM binary
   bunenv .venv --bun=1.3.3

   # Verify
   file .venv/bin/bun  # Should say "arm64"

**Rosetta Issues**:

.. code-block:: bash

   # If need x64 for compatibility:
   arch -x86_64 bunenv .venv --bun=1.3.3

   # Run under Rosetta
   arch -x86_64 source .venv/bin/activate

**Gatekeeper Warnings**:

.. code-block:: bash

   # If macOS blocks Bun binary:
   xattr -dr com.apple.quarantine .venv/bin/bun

Linux Issues
~~~~~~~~~~~~

**Alpine/musl Issues**:

.. code-block:: bash

   # If standard binary fails on Alpine:
   bunenv .venv --variant=musl

   # Verify musl binary
   ldd .venv/bin/bun
   # Should NOT show glibc

**Permission Issues**:

.. code-block:: bash

   # If activation script not executable:
   chmod +x .venv/bin/activate

**SELinux Issues**:

.. code-block:: bash

   # If SELinux blocks execution:
   chcon -t bin_t .venv/bin/bun

   # Or disable SELinux enforcement (not recommended)

Windows Issues
~~~~~~~~~~~~~~

**PowerShell Execution Policy**:

.. code-block:: powershell

   # If activation blocked:
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

   # Then activate
   .venv\Scripts\Activate.ps1

**Path Length Issues**:

.. code-block:: bat

   REM Windows has 260 char path limit
   REM Use shorter paths:
   bunenv C:\bun\env

**Antivirus False Positives**:

.. code-block:: text

   Add .venv\ to antivirus exclusions

**Git Bash/MSYS Issues**:

.. code-block:: bash

   # Use Windows-style activation, not Unix
   .venv/Scripts/activate.bat  # Not: source .venv/bin/activate

Configuration Issues
--------------------

Config File Not Loaded
~~~~~~~~~~~~~~~~~~~~~~~

**Symptom**: Settings in ``~/.bunenvrc`` ignored

**Solutions**:

**Check file format**:

.. code-block:: bash

   # Must have [bunenv] section
   cat ~/.bunenvrc

Should look like:

.. code-block:: ini

   [bunenv]
   bun = latest
   github_token = ghp_xxx

**Check file permissions**:

.. code-block:: bash

   ls -la ~/.bunenvrc
   # Should be readable

**Use verbose mode**:

.. code-block:: bash

   bunenv .venv --verbose
   # Shows which configs are loaded

.bun-version File Ignored
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom**: Version from ``.bun-version`` not used

**Solutions**:

.. code-block:: bash

   # Check file exists in current directory
   ls -la .bun-version

   # Check file content (should be just version)
   cat .bun-version
   # 1.3.3

   # Check for typos in filename
   # Must be: .bun-version (with dot, dash)
   # Not: bun-version, .bun_version, etc.

CI/CD Issues
------------

GitHub Actions Failures
~~~~~~~~~~~~~~~~~~~~~~~~

**Token Issues**:

.. code-block:: yaml

   # Use GITHUB_TOKEN secret
   - name: Setup Bun
     env:
       GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
     run: bunenv .venv --github-token=$GITHUB_TOKEN

**PATH Issues**:

.. code-block:: yaml

   # Add to PATH for subsequent steps
   - name: Setup Bun
     run: |
       bunenv .venv --bun=1.3.3
       echo "$GITHUB_WORKSPACE/.venv/bin" >> $GITHUB_PATH

**Cache Issues**:

.. code-block:: yaml

   # Cache bunenv to speed up builds
   - uses: actions/cache@v3
     with:
       path: .venv
       key: bunenv-${{ runner.os }}-${{ hashFiles('.bun-version') }}

Docker Build Failures
~~~~~~~~~~~~~~~~~~~~~

**Permissions**:

.. code-block:: dockerfile

   # Run as non-root
   RUN useradd -m bunuser
   USER bunuser
   RUN bunenv /home/bunuser/.venv --bun=1.3.3

**Network Issues**:

.. code-block:: dockerfile

   # Add token for rate limits
   ARG GITHUB_TOKEN
   RUN bunenv /opt/bunenv --github-token=${GITHUB_TOKEN}

Getting Help
------------

Still stuck? Here's how to get help:

Gather Information
~~~~~~~~~~~~~~~~~~

Before asking for help, collect:

.. code-block:: bash

   # bunenv version
   bunenv --version

   # Python version
   python --version

   # Platform info
   uname -a  # Linux/macOS
   systeminfo  # Windows

   # Verbose output
   bunenv .venv --verbose --bun=1.3.3 2>&1 | tee bunenv.log

Where to Ask
~~~~~~~~~~~~

**GitHub Issues**: https://github.com/JacobCoffee/bunenv/issues

**Include**:
- What you're trying to do
- What you expected
- What actually happened
- Error messages (full output)
- Platform information
- bunenv version

**Search First**: Your issue might already be answered!

**Example Good Issue**:

.. code-block:: text

   Title: bunenv fails on Alpine Linux 3.18

   Description:
   I'm trying to create a Bun environment on Alpine Linux but getting an error.

   Steps to reproduce:
   1. Alpine Linux 3.18 Docker container
   2. pip install bunenv
   3. bunenv .venv --bun=1.3.3

   Expected: Environment created successfully
   Actual: Error: "cannot execute binary file"

   Error output:
   [paste full error]

   Environment:
   - bunenv version: 0.1.0
   - Python version: 3.11.6
   - Platform: Linux alpine 6.1.0-0-virt x86_64
   - Architecture: x86_64

   Verbose log:
   [attach bunenv.log]

Common Error Messages
---------------------

Quick reference for common errors:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Error Message
     - Solution
   * - ``rate limit exceeded``
     - Add GitHub token with ``--github-token``
   * - ``command not found: bunenv``
     - Add Python scripts directory to PATH
   * - ``Environment already exists``
     - Use ``--force`` or remove directory
   * - ``HTTP Error 404``
     - Check version exists, verify platform support
   * - ``cannot execute binary file``
     - Wrong variant; try ``--variant=baseline`` or ``--variant=musl``
   * - ``Segmentation fault``
     - CPU incompatibility; use ``--variant=baseline``
   * - ``Permission denied``
     - Don't use sudo; install with ``--user`` flag
   * - ``IncompleteRead``
     - Network issue; retry or use mirror
   * - ``No such file or directory: activate``
     - Environment creation failed; recreate with ``--verbose``

Preventive Measures
-------------------

Avoid future issues:

**DO:**

✓ Pin Bun versions in ``.bun-version``

✓ Use GitHub token for CI/CD

✓ Test with ``--verbose`` when troubleshooting

✓ Keep bunenv updated: ``pip install --upgrade bunenv``

✓ Read error messages carefully

**DON'T:**

✗ Use ``sudo`` to install bunenv

✗ Mix system Bun with environment Bun

✗ Ignore SSL errors (unless necessary)

✗ Share environments between projects

✗ Commit ``.venv/`` to version control

Next Steps
----------

If you've solved your issue:

- :doc:`workflows` - Learn best practices
- :doc:`contributing` - Help others by improving docs

If still having trouble:

- Open an issue: https://github.com/JacobCoffee/bunenv/issues
- Include diagnostics and error messages
- We're here to help!
