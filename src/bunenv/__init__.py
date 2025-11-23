#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    bunenv
    ~~~~~~
    Bun.js virtual environment

    Adapted from nodeenv by Eugene Kalinin
    :copyright: (c) 2024 Jacob Coffee
    :license: BSD, see LICENSE for more details.

    Original nodeenv: https://github.com/ekalinin/nodeenv
"""

import contextlib
import io
import json
import sys
import os
import re
import ssl
import stat
import logging
import operator
import argparse
import subprocess
if sys.version_info < (3, 3):
    from pipes import quote as _quote
else:
    from shlex import quote as _quote
import platform
import zipfile
import shutil
import sysconfig

try:  # pragma: no cover (py2 only)
    from ConfigParser import SafeConfigParser as ConfigParser
    # noinspection PyCompatibility
    import urllib2
    iteritems = operator.methodcaller('iteritems')
    import httplib
    IncompleteRead = httplib.IncompleteRead
except ImportError:  # pragma: no cover (py3 only)
    from configparser import ConfigParser
    # noinspection PyUnresolvedReferences
    import urllib.request as urllib2
    iteritems = operator.methodcaller('items')
    import http
    IncompleteRead = http.client.IncompleteRead

bunenv_version = '0.1.0'

join = os.path.join
abspath = os.path.abspath
src_base_url = None  # Will be set to GitHub API base

is_PY3 = sys.version_info[0] >= 3
is_WIN = platform.system() == 'Windows'
is_CYGWIN = platform.system().startswith(('CYGWIN', 'MSYS'))

ignore_ssl_certs = False

# ---------------------------------------------------------
# Utils


# https://github.com/jhermann/waif/blob/master/python/to_uft8.py
def to_utf8(text):
    """Convert given text to UTF-8 encoding (as far as possible)."""
    if not text or is_PY3:
        return text

    try:           # unicode or pure ascii
        return text.encode("utf8")
    except UnicodeDecodeError:
        try:       # successful UTF-8 decode means it's pretty sure UTF-8
            text.decode("utf8")
            return text
        except UnicodeDecodeError:
            try:   # get desperate; and yes, this has a western hemisphere bias
                return text.decode("cp1252").encode("utf8")
            except UnicodeDecodeError:
                pass

    return text    # return unchanged, hope for the best


class Config(object):
    """
    Configuration namespace.
    """

    # Defaults
    bun = 'latest'
    variant = ''  # baseline, profile, musl
    github_token = None  # For GitHub API rate limits
    prebuilt = True  # Always true for Bun (no source builds)
    ignore_ssl_certs = False
    mirror = None  # For GitHub mirrors if needed

    @classmethod
    def _load(cls, configfiles, verbose=False):
        """
        Load configuration from the given files in reverse order,
        if they exist and have a [bunenv] section.
        Additionally, load version from .bun-version if file exists.
        """
        for configfile in reversed(configfiles):
            configfile = os.path.expanduser(configfile)
            if not os.path.exists(configfile):
                continue

            ini_file = ConfigParser()
            ini_file.read(configfile)
            section = "bunenv"
            if not ini_file.has_section(section):
                continue

            for attr, val in iteritems(vars(cls)):
                if attr.startswith('_') or not \
                   ini_file.has_option(section, attr):
                    continue

                if isinstance(val, bool):
                    val = ini_file.getboolean(section, attr)
                else:
                    val = ini_file.get(section, attr)

                if verbose:
                    print('CONFIG {0}: {1} = {2}'.format(
                        os.path.basename(configfile), attr, val))
                setattr(cls, attr, val)

        # Support .bun-version file (like .node-version)
        if os.path.exists(".bun-version"):
            with open(".bun-version", "r") as v_file:
                setattr(cls, "bun", v_file.readline().strip().lstrip("v").lstrip("bun-v"))

    @classmethod
    def _dump(cls):
        """
        Print defaults for the README.
        """
        print("    [bunenv]")
        print("    " + "\n    ".join(
            "%s = %s" % (k, v) for k, v in sorted(iteritems(vars(cls)))
            if not k.startswith('_')))


Config._default = dict(
    (attr, val) for attr, val in iteritems(vars(Config))
    if not attr.startswith('_')
)


def clear_output(out):
    """
    Remove new-lines and decode
    """
    return out.decode('utf-8').replace('\n', '')


def remove_env_bin_from_path(env, env_bin_dir):
    """
    Remove bin directory of the current environment from PATH
    """
    return env.replace(env_bin_dir + ':', '')


def parse_version(version_str):
    """
    Parse version string to a tuple of integer parts
    """
    v = version_str.replace('v', '').replace('bun-v', '').split('.')[:3]
    # remove all after '+' in the PATCH part of the version
    if len(v) >= 3:
        v[2] = v[2].split('+')[0]
    return tuple(map(int, v))


def bun_version_from_args(args):
    """
    Parse the bun version from the argparse args
    """
    if args.bun == 'system':
        out, err = subprocess.Popen(
            ["bun", "--version"], stdout=subprocess.PIPE).communicate()
        return parse_version(clear_output(out))

    return parse_version(args.bun)


def create_logger():
    """
    Create logger for diagnostic
    """
    # create logger
    loggr = logging.getLogger("bunenv")
    loggr.setLevel(logging.INFO)

    # monkey patch
    def emit(self, record):
        msg = self.format(record)
        fs = "%s" if getattr(record, "continued", False) else "%s\n"
        self.stream.write(fs % to_utf8(msg))
        self.flush()
    logging.StreamHandler.emit = emit

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter(fmt="%(message)s")

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    loggr.addHandler(ch)
    return loggr


logger = create_logger()


def make_parser():
    """
    Make a command line argument parser.
    """
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTIONS] DEST_DIR")

    parser.add_argument(
        '--version', action='version', version=bunenv_version)

    parser.add_argument(
        '-b', '--bun', dest='bun', metavar='BUN_VER', default=Config.bun,
        help='The Bun version to use, e.g., '
        '--bun=1.0.0 will use bun-v1.0.0 '
        'to create the new environment. '
        'The default is last stable version (`latest`). '
        'Use `system` to use system-wide bun.')

    parser.add_argument(
        '--variant',
        action="store", dest='variant', default=Config.variant,
        choices=['', 'baseline', 'profile', 'musl'],
        help='Bun variant to install (baseline, profile, musl). '
        'Default is auto-detected based on platform.')

    parser.add_argument(
        '--github-token',
        action="store", dest='github_token', default=Config.github_token,
        help='GitHub API token to avoid rate limits when fetching versions.')

    parser.add_argument(
        '--mirror',
        action="store", dest='mirror', default=Config.mirror,
        help='Set mirror server for Bun downloads (GitHub mirror).')

    parser.add_argument(
        '-v', '--verbose',
        action='store_true', dest='verbose', default=False,
        help="Verbose mode")

    parser.add_argument(
        '-q', '--quiet',
        action='store_true', dest='quiet', default=False,
        help="Quiet mode")

    parser.add_argument(
        '-C', '--config-file', dest='config_file', default=None,
        help="Load a different file than '~/.bunenvrc'. "
        "Pass an empty string for no config (use built-in defaults).")

    parser.add_argument(
        '-r', '--requirements',
        dest='requirements', default='', metavar='FILENAME',
        help='Install all the packages listed in the given requirements file.')

    parser.add_argument(
        '--prompt', dest='prompt',
        help='Provides an alternative prompt prefix for this environment')

    parser.add_argument(
        '-l', '--list', dest='list',
        action='store_true', default=False,
        help='Lists available Bun versions')

    parser.add_argument(
        '--update', dest='update',
        action='store_true', default=False,
        help='Install packages from file without bun')

    parser.add_argument(
        '--python-virtualenv', '-p', dest='python_virtualenv',
        action='store_true', default=False,
        help='Use current python virtualenv')

    parser.add_argument(
        '--clean-src', '-c', dest='clean_src',
        action='store_true', default=False,
        help='Remove "src" directory after installation')

    parser.add_argument(
        '--force', dest='force',
        action='store_true', default=False,
        help='Force installation in a pre-existing directory')

    parser.add_argument(
        '--prebuilt', dest='prebuilt',
        action='store_true', default=Config.prebuilt,
        help='Install Bun from prebuilt package (default and only option)')

    parser.add_argument(
        '--ignore_ssl_certs', dest='ignore_ssl_certs',
        action='store_true', default=Config.ignore_ssl_certs,
        help='Ignore certificates for package downloads. - UNSAFE -')

    parser.add_argument(
        metavar='DEST_DIR', dest='env_dir', nargs='?',
        help='Destination directory')

    return parser


def parse_args(check=True):
    """
    Parses command line arguments.

    Set `check` to False to skip validation checks.
    """
    parser = make_parser()
    args = parser.parse_args()

    if args.config_file is None:
        args.config_file = ["./tox.ini", "./setup.cfg", "~/.bunenvrc"]
    elif not args.config_file:
        args.config_file = []
    else:
        # Make sure that explicitly provided files exist
        if not os.path.exists(args.config_file):
            parser.error("Config file '{0}' doesn't exist!".format(
                args.config_file))
        args.config_file = [args.config_file]

    if not check:
        return args

    if not args.list:
        if not args.python_virtualenv and not args.env_dir:
            parser.error('You must provide a DEST_DIR or '
                         'use current python virtualenv')

    return args


def mkdir(path):
    """
    Create directory
    """
    if not os.path.exists(path):
        logger.debug(' * Creating: %s ... ', path, extra=dict(continued=True))
        os.makedirs(path)
        logger.debug('done.')
    else:
        logger.debug(' * Directory %s already exists', path)


def make_executable(filename):
    mode_0755 = (stat.S_IRWXU | stat.S_IXGRP |
                 stat.S_IRGRP | stat.S_IROTH | stat.S_IXOTH)
    os.chmod(filename, mode_0755)


# noinspection PyArgumentList
def writefile(dest, content, overwrite=True, append=False):
    """
    Create file and write content in it
    """
    content = to_utf8(content)
    if is_PY3 and not isinstance(content, bytes):
        content = bytes(content, 'utf-8')
    if not os.path.exists(dest):
        logger.debug(' * Writing %s ... ', dest, extra=dict(continued=True))
        with open(dest, 'wb') as f:
            f.write(content)
        make_executable(dest)
        logger.debug('done.')
        return
    else:
        with open(dest, 'rb') as f:
            c = f.read()
        if content in c:
            logger.debug(' * Content %s already in place', dest)
            return

        if not overwrite:
            logger.info(' * File %s exists with different content; '
                        ' not overwriting', dest)
            return

        if append:
            logger.info(' * Appending data to %s', dest)
            with open(dest, 'ab') as f:
                f.write(content)
            return

        logger.info(' * Overwriting %s with new content', dest)
        with open(dest, 'wb') as f:
            f.write(content)


def callit(cmd, show_stdout=True, in_shell=False,
           cwd=None, extra_env=None):
    """
    Execute cmd line in sub-shell
    """
    all_output = []
    cmd_parts = []

    for part in cmd:
        if len(part) > 45:
            part = part[:20] + "..." + part[-20:]
        if ' ' in part or '\n' in part or '"' in part or "'" in part:
            part = '"%s"' % part.replace('"', '\\"')
        cmd_parts.append(part)
    cmd_desc = ' '.join(cmd_parts)
    logger.debug(" ** Running command %s" % cmd_desc)

    if in_shell:
        cmd = ' '.join(cmd)

    # output
    stdout = subprocess.PIPE

    # env
    if extra_env:
        env = os.environ.copy()
        if extra_env:
            env.update(extra_env)
    else:
        env = None

    # execute
    try:
        proc = subprocess.Popen(
            cmd, stderr=subprocess.STDOUT, stdin=None, stdout=stdout,
            cwd=cwd, env=env, shell=in_shell)
    except Exception:
        e = sys.exc_info()[1]
        logger.error("Error %s while executing command %s" % (e, cmd_desc))
        raise

    stdout = proc.stdout
    while stdout:
        line = stdout.readline()
        if not line:
            break
        try:
            if is_WIN:
                line = line.decode('mbcs').rstrip()
            else:
                line = line.decode('utf8').rstrip()
        except UnicodeDecodeError:
            line = line.decode('cp866').rstrip()
        all_output.append(line)
        if show_stdout:
            logger.info(line)
    proc.wait()

    # error handler
    if proc.returncode:
        if show_stdout:
            for s in all_output:
                logger.critical(s)
        raise OSError("Command %s failed with error code %s"
                      % (cmd_desc, proc.returncode))

    return proc.returncode, all_output


def is_x86_64_musl():
    """Check if running on musl libc"""
    return sysconfig.get_config_var('HOST_GNU_TYPE') == 'x86_64-pc-linux-musl'


def get_bun_bin_url(version, variant='', mirror=None):
    """
    Construct GitHub releases URL for Bun binary

    Bun provides prebuilt binaries for multiple platforms in the format:
    bun-{platform}-{arch}[-{variant}].zip
    """
    archmap = {
        'x86_64': 'x64',
        'amd64': 'x64',
        'AMD64': 'x64',
        'ARM64': 'aarch64',  # macOS ARM
        'arm64': 'aarch64',
        'aarch64': 'aarch64',
    }

    sysmap = {
        'Darwin': 'darwin',
        'Linux': 'linux',
        'Windows': 'windows',
    }

    arch = archmap.get(platform.machine(), platform.machine().lower())
    sys_name = sysmap.get(platform.system(), platform.system().lower())

    # Handle musl variant for Linux
    variant_str = ''
    if variant:
        variant_str = f'-{variant}'
    elif is_x86_64_musl() and sys_name == 'linux':
        variant_str = '-musl'

    filename = f'bun-{sys_name}-{arch}{variant_str}.zip'
    tag = f'bun-v{version}'

    base_url = mirror if mirror else 'https://github.com/oven-sh/bun/releases/download'
    return f'{base_url}/{tag}/{filename}'


@contextlib.contextmanager
def zipfile_open(*args, **kwargs):
    """Context manager for zipfile."""
    zf = zipfile.ZipFile(*args, **kwargs)
    try:
        yield zf
    finally:
        zf.close()


def _download_bun_file(bun_url, n_attempt=3):
    """Do multiple attempts to avoid incomplete data in case
    of unstable network"""
    while n_attempt > 0:
        try:
            return io.BytesIO(urlopen(bun_url).read())
        except IncompleteRead as e:
            logger.warning(
                'Incomplete read while reading '
                'from {} - {}'.format(bun_url, e)
            )
            n_attempt -= 1
            if n_attempt == 0:
                raise e


def download_bun_bin(bun_url, src_dir, args):
    """
    Download Bun binary zip file
    """
    logger.info('.', extra=dict(continued=True))
    dl_contents = _download_bun_file(bun_url)
    logger.info('.', extra=dict(continued=True))

    with zipfile_open(dl_contents) as archive:
        archive.extractall(src_dir)


def urlopen(url):
    home_url = "https://github.com/JacobCoffee/bunenv/"
    headers = {'User-Agent': 'bunenv/%s (%s)' % (bunenv_version, home_url)}

    # Add GitHub token if provided
    if Config.github_token:
        headers['Authorization'] = f'token {Config.github_token}'

    req = urllib2.Request(url, None, headers)
    if ignore_ssl_certs:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        context.verify_mode = ssl.CERT_NONE
        return urllib2.urlopen(req, context=context)
    return urllib2.urlopen(req)

# ---------------------------------------------------------
# Virtual environment functions


def copy_bun_from_prebuilt(env_dir, src_dir, bun_version):
    """
    Copy prebuilt Bun binary into environment

    Bun zip structure: bun-{platform}-{arch}/bun (or bun.exe on Windows)
    Extract to: env_dir/bin/bun (or env_dir/Scripts/bun.exe on Windows)
    """
    logger.info('.', extra=dict(continued=True))

    if is_WIN:
        dest_dir = join(env_dir, 'Scripts')
        bun_binary = 'bun.exe'
    else:
        dest_dir = join(env_dir, 'bin')
        bun_binary = 'bun'

    mkdir(dest_dir)

    # Find the extracted bun directory
    # It should be something like: bun-linux-x64 or bun-darwin-aarch64
    import glob as glob_module
    bun_folders = glob_module.glob(join(src_dir, 'bun-*'))

    if not bun_folders:
        raise OSError("Could not find extracted Bun directory in %s" % src_dir)

    bun_folder = bun_folders[0]
    src_binary = join(bun_folder, bun_binary)
    dest_binary = join(dest_dir, bun_binary)

    if not os.path.exists(src_binary):
        raise OSError("Could not find Bun binary at %s" % src_binary)

    # Copy the binary
    shutil.copy2(src_binary, dest_binary)

    # Make it executable on Unix-like systems
    if not is_WIN:
        make_executable(dest_binary)

    logger.info('.', extra=dict(continued=True))


def install_bun(env_dir, src_dir, args):
    """
    Download Bun binary and install it in virtual environment.
    Bun only provides prebuilt binaries (no source builds).
    """
    try:
        install_bun_wrapped(env_dir, src_dir, args)
    except BaseException:
        # this restores the newline suppressed by continued=True
        logger.info('')
        raise


def install_bun_wrapped(env_dir, src_dir, args):
    env_dir = abspath(env_dir)

    logger.info(' * Install prebuilt Bun (%s) ' % args.bun,
                extra=dict(continued=True))

    bun_url = get_bun_bin_url(args.bun, args.variant, args.mirror)

    # Download and extract
    try:
        download_bun_bin(bun_url, src_dir, args)
    except urllib2.HTTPError as e:
        logger.error('Failed to download from %s: %s' % (bun_url, e))
        raise

    logger.info('.', extra=dict(continued=True))

    # Copy binary to environment
    copy_bun_from_prebuilt(env_dir, src_dir, args.bun)

    logger.info(' done.')


def install_packages(env_dir, args):
    """
    Install packages via bun add -g
    """
    if not args.requirements:
        return

    logger.info(' * Install packages ... ',
                extra=dict(continued=True))

    bun_bin = join(env_dir, 'bin', 'bun')
    if is_WIN:
        bun_bin = join(env_dir, 'Scripts', 'bun.exe')

    with open(args.requirements) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                callit([bun_bin, 'add', '-g', line],
                       show_stdout=args.verbose, in_shell=False)

    logger.info('done.')


def install_activate(env_dir, args):
    """
    Install virtual environment activation script
    """
    if is_WIN:
        files = {
            'activate.bat': ACTIVATE_BAT,
            "deactivate.bat": DEACTIVATE_BAT,
            "Activate.ps1": ACTIVATE_PS1
        }
        bin_dir = join(env_dir, 'Scripts')
        shim_bun = join(bin_dir, "bun.exe")
    else:
        files = {
            'activate': ACTIVATE_SH,
            'activate.fish': ACTIVATE_FISH,
            'shim': SHIM
        }
        bin_dir = join(env_dir, 'bin')
        shim_bun = join(bin_dir, "bun")

    if is_CYGWIN:
        mkdir(bin_dir)

    if args.bun == "system":
        files["bun"] = SHIM

    prompt = args.prompt or '(%s)' % os.path.basename(os.path.abspath(env_dir))

    if args.bun == "system":
        env = os.environ.copy()
        env.update({'PATH': remove_env_bin_from_path(env['PATH'], bin_dir)})
        which_bun_output, _ = subprocess.Popen(
            ["which", "bun"],
            stdout=subprocess.PIPE, env=env).communicate()
        shim_bun = clear_output(which_bun_output)
        assert shim_bun, "Did not find bun system executable"

    for name, content in files.items():
        file_path = join(bin_dir, name)
        content = content.replace('__BUN_VIRTUAL_PROMPT__', prompt)
        content = content.replace('__BUN_VIRTUAL_ENV__',
                                  os.path.abspath(env_dir))
        content = content.replace('__SHIM_BUN__', shim_bun)
        content = content.replace('__BIN_NAME__', os.path.basename(bin_dir))

        # Bun-specific environment variables
        content = content.replace('__BUN_INSTALL__', '$BUN_VIRTUAL_ENV')
        content = content.replace('__BUN_INSTALL_BIN__', '$BUN_VIRTUAL_ENV/__BIN_NAME__')

        # Handle append for python virtualenv integration
        need_append = False
        if args.python_virtualenv:
            disable_prompt = DISABLE_PROMPT.get(name, '')
            enable_prompt = ENABLE_PROMPT.get(name, '')
            content = disable_prompt + content + enable_prompt
            need_append = bool(disable_prompt)
        writefile(file_path, content, append=need_append)


def set_predeactivate_hook(env_dir):
    if not is_WIN:
        with open(join(env_dir, 'bin', 'predeactivate'), 'a') as hook:
            hook.write(PREDEACTIVATE_SH)


def create_environment(env_dir, args):
    """
    Creates a new Bun environment in ``env_dir``.
    """
    if os.path.exists(env_dir) and not args.python_virtualenv:
        logger.info(' * Environment already exists: %s', env_dir)
        if not args.force:
            sys.exit(2)
    src_dir = to_utf8(abspath(join(env_dir, 'src')))
    mkdir(src_dir)

    if args.bun != "system":
        install_bun(env_dir, src_dir, args)
    else:
        # Create basic directory structure for system bun
        mkdir(join(env_dir, 'bin'))
        # Bun manages its own package cache
        mkdir(join(env_dir, 'install'))
        mkdir(join(env_dir, 'install', 'cache'))

    # activate script install
    install_activate(env_dir, args)

    if args.requirements:
        install_packages(env_dir, args)

    if args.python_virtualenv:
        set_predeactivate_hook(env_dir)

    # Cleanup
    if args.clean_src:
        shutil.rmtree(src_dir)


def _get_versions_json():
    """
    Fetch Bun versions from GitHub Releases API
    """
    headers = {}
    if Config.github_token:
        headers['Authorization'] = f'token {Config.github_token}'

    url = 'https://api.github.com/repos/oven-sh/bun/releases'
    req = urllib2.Request(url, None, headers)

    if ignore_ssl_certs:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        context.verify_mode = ssl.CERT_NONE
        response = urllib2.urlopen(req, context=context)
    else:
        response = urllib2.urlopen(req)

    releases = json.loads(response.read().decode('UTF-8'))

    # Transform to compatible format
    return [{
        'version': r['tag_name'].replace('bun-v', ''),
        'lts': False,  # Bun doesn't have LTS concept
        'tag_name': r['tag_name'],
        'assets': r.get('assets', [])
    } for r in releases if r['tag_name'].startswith('bun-v')]


def get_bun_versions():
    """Return all available Bun versions"""
    return [dct['version'] for dct in _get_versions_json()]


def print_bun_versions():
    """
    Prints into stdout all available Bun versions
    """
    versions = get_bun_versions()
    chunks_of_8 = [
        versions[pos:pos + 8] for pos in range(0, len(versions), 8)
    ]
    for chunk in chunks_of_8:
        logger.info('\t'.join(chunk))


def get_last_stable_bun_version():
    """
    Return last stable Bun version (first in the list from GitHub)
    """
    versions = get_bun_versions()
    if versions:
        return versions[0]
    return None


def get_env_dir(args):
    if args.python_virtualenv:
        if hasattr(sys, 'real_prefix'):
            res = sys.prefix
        elif hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix:
            res = sys.prefix
        elif 'CONDA_PREFIX' in os.environ:
            res = sys.prefix
        else:
            logger.error('No python virtualenv is available')
            sys.exit(2)
    else:
        res = args.env_dir
    return to_utf8(res)


# noinspection PyProtectedMember
def main():
    """
    Entry point
    """
    # quick&dirty way to help update the README
    if "--dump-config-defaults" in sys.argv:
        Config._dump()
        return

    args = parse_args(check=False)
    # noinspection PyProtectedMember
    Config._load(args.config_file, args.verbose)

    args = parse_args()

    if args.bun.lower() == 'system' and is_WIN:
        logger.error('Installing system bun on Windows is not supported!')
        exit(1)

    global ignore_ssl_certs
    ignore_ssl_certs = args.ignore_ssl_certs

    # Set GitHub token from args if provided
    if args.github_token:
        Config.github_token = args.github_token

    # Handle version resolution
    if not args.bun or args.bun.lower() == 'latest':
        args.bun = get_last_stable_bun_version()
        if not args.bun:
            logger.error('Could not determine latest Bun version')
            sys.exit(1)

    if args.list:
        print_bun_versions()
    elif args.update:
        env_dir = get_env_dir(args)
        install_packages(env_dir, args)
    else:
        env_dir = get_env_dir(args)
        create_environment(env_dir, args)


# ---------------------------------------------------------
# Shell scripts content

DISABLE_PROMPT = {
    'activate': """
# disable bunenv's prompt
# (prompt already changed by original virtualenv's script)
BUN_VIRTUAL_ENV_DISABLE_PROMPT=1
""",
    'activate.fish': """
# disable bunenv's prompt
# (prompt already changed by original virtualenv's script)
set BUN_VIRTUAL_ENV_DISABLE_PROMPT 1
""",
}

ENABLE_PROMPT = {
    'activate': """
unset BUN_VIRTUAL_ENV_DISABLE_PROMPT
""",
    'activate.fish': """
set -e BUN_VIRTUAL_ENV_DISABLE_PROMPT
""",
}

SHIM = """#!/usr/bin/env bash
export BUN_INSTALL='__BUN_VIRTUAL_ENV__'
export BUN_INSTALL_BIN='__BUN_VIRTUAL_ENV__/__BIN_NAME__'
exec '__SHIM_BUN__' "$@"
"""

ACTIVATE_BAT = r"""
@echo off
set "BUN_VIRTUAL_ENV=__BUN_VIRTUAL_ENV__"
if not defined PROMPT (
    set "PROMPT=$P$G"
)
if defined _OLD_VIRTUAL_PROMPT (
    set "PROMPT=%_OLD_VIRTUAL_PROMPT%"
)
if defined _OLD_VIRTUAL_BUN_INSTALL (
    set "BUN_INSTALL=%_OLD_VIRTUAL_BUN_INSTALL%"
)
set "_OLD_VIRTUAL_PROMPT=%PROMPT%"
set "PROMPT=__BUN_VIRTUAL_PROMPT__ %PROMPT%"
if defined BUN_INSTALL (
    set "_OLD_VIRTUAL_BUN_INSTALL=%BUN_INSTALL%"
)
set "BUN_INSTALL=%BUN_VIRTUAL_ENV%"
if defined _OLD_VIRTUAL_PATH (
    set "PATH=%_OLD_VIRTUAL_PATH%"
) else (
    set "_OLD_VIRTUAL_PATH=%PATH%"
)
set "PATH=%BUN_VIRTUAL_ENV%\Scripts;%PATH%"
:END

"""

DEACTIVATE_BAT = """\
@echo off
if defined _OLD_VIRTUAL_PROMPT (
    set "PROMPT=%_OLD_VIRTUAL_PROMPT%"
)
set _OLD_VIRTUAL_PROMPT=
if defined _OLD_VIRTUAL_BUN_INSTALL (
    set "BUN_INSTALL=%_OLD_VIRTUAL_BUN_INSTALL%"
    set _OLD_VIRTUAL_BUN_INSTALL=
)
if defined _OLD_VIRTUAL_PATH (
    set "PATH=%_OLD_VIRTUAL_PATH%"
)
set _OLD_VIRTUAL_PATH=
set BUN_VIRTUAL_ENV=
:END
"""

ACTIVATE_PS1 = r"""
function global:deactivate ([switch]$NonDestructive) {
    # Revert to original values
    if (Test-Path function:_OLD_VIRTUAL_PROMPT) {
        copy-item function:_OLD_VIRTUAL_PROMPT function:prompt
        remove-item function:_OLD_VIRTUAL_PROMPT
    }
    if (Test-Path env:_OLD_VIRTUAL_BUN_INSTALL) {
        copy-item env:_OLD_VIRTUAL_BUN_INSTALL env:BUN_INSTALL
        remove-item env:_OLD_VIRTUAL_BUN_INSTALL
    }
    if (Test-Path env:_OLD_VIRTUAL_PATH) {
        copy-item env:_OLD_VIRTUAL_PATH env:PATH
        remove-item env:_OLD_VIRTUAL_PATH
    }
    if (Test-Path env:BUN_VIRTUAL_ENV) {
        remove-item env:BUN_VIRTUAL_ENV
    }
    if (!$NonDestructive) {
        # Self destruct!
        remove-item function:deactivate
    }
}

deactivate -nondestructive
$env:BUN_VIRTUAL_ENV="__BUN_VIRTUAL_ENV__"

# Set the prompt to include the env name
# Make sure _OLD_VIRTUAL_PROMPT is global
function global:_OLD_VIRTUAL_PROMPT {""}
copy-item function:prompt function:_OLD_VIRTUAL_PROMPT
function global:prompt {
    Write-Host -NoNewline -ForegroundColor Green '__BUN_VIRTUAL_PROMPT__ '
    _OLD_VIRTUAL_PROMPT
}

# Set BUN_INSTALL
if (Test-Path env:BUN_INSTALL) {
    copy-item env:BUN_INSTALL env:_OLD_VIRTUAL_BUN_INSTALL
}
$env:BUN_INSTALL = "$env:BUN_VIRTUAL_ENV"

# Add the venv to the PATH
copy-item env:PATH env:_OLD_VIRTUAL_PATH
$env:PATH = "$env:BUN_VIRTUAL_ENV\Scripts;$env:PATH"
"""

ACTIVATE_SH = r"""

# This file must be used with "source bin/activate" *from bash*
# you cannot run it directly

deactivate_bun () {
    # reset old environment variables
    if [ -n "${_OLD_BUN_VIRTUAL_PATH:-}" ] ; then
        PATH="${_OLD_BUN_VIRTUAL_PATH:-}"
        export PATH
        unset _OLD_BUN_VIRTUAL_PATH

        BUN_INSTALL="${_OLD_BUN_INSTALL:-}"
        export BUN_INSTALL
        unset _OLD_BUN_INSTALL

        BUN_INSTALL_BIN="${_OLD_BUN_INSTALL_BIN:-}"
        export BUN_INSTALL_BIN
        unset _OLD_BUN_INSTALL_BIN
    fi

    # This should detect bash and zsh, which have a hash command that must
    # be called to get it to forget past commands.  Without forgetting
    # past commands the $PATH changes we made may not be respected
    if [ -n "${BASH:-}" -o -n "${ZSH_VERSION:-}" ] ; then
        hash -r
    fi

    if [ -n "${_OLD_BUN_VIRTUAL_PS1:-}" ] ; then
        PS1="${_OLD_BUN_VIRTUAL_PS1:-}"
        export PS1
        unset _OLD_BUN_VIRTUAL_PS1
    fi

    unset BUN_VIRTUAL_ENV
    if [ ! "${1:-}" = "nondestructive" ] ; then
    # Self destruct!
        unset -f deactivate_bun
    fi
}

# unset irrelevant variables
deactivate_bun nondestructive

# find the directory of this script
# http://stackoverflow.com/a/246128
if [ "${BASH_SOURCE:-}" ] ; then
    SOURCE="${BASH_SOURCE[0]}"

    while [ -h "$SOURCE" ] ; do SOURCE="$(readlink "$SOURCE")"; done
    DIR="$( command cd -P "$( dirname "$SOURCE" )" > /dev/null && pwd )"

    BUN_VIRTUAL_ENV="$(dirname "$DIR")"
else
    # dash not movable. fix use case:
    #   dash -c " . bun-env/bin/activate && bun -v"
    BUN_VIRTUAL_ENV="__BUN_VIRTUAL_ENV__"
fi

# BUN_VIRTUAL_ENV is the parent of the directory where this script is
export BUN_VIRTUAL_ENV

_OLD_BUN_VIRTUAL_PATH="$PATH"
PATH="$BUN_VIRTUAL_ENV/__BIN_NAME__:$PATH"
export PATH

_OLD_BUN_INSTALL="${BUN_INSTALL:-}"
BUN_INSTALL="$BUN_VIRTUAL_ENV"
export BUN_INSTALL

_OLD_BUN_INSTALL_BIN="${BUN_INSTALL_BIN:-}"
BUN_INSTALL_BIN="$BUN_VIRTUAL_ENV/__BIN_NAME__"
export BUN_INSTALL_BIN

if [ -z "${BUN_VIRTUAL_ENV_DISABLE_PROMPT:-}" ] ; then
    _OLD_BUN_VIRTUAL_PS1="${PS1:-}"
    if [ "x__BUN_VIRTUAL_PROMPT__" != x ] ; then
        PS1="__BUN_VIRTUAL_PROMPT__ ${PS1:-}"
    else
    if [ "`basename \"$BUN_VIRTUAL_ENV\"`" = "__" ] ; then
        # special case for Aspen magic directories
        # see http://www.zetadev.com/software/aspen/
        PS1="[`basename \`dirname \"$BUN_VIRTUAL_ENV\"\``] ${PS1:-}"
    else
        PS1="(`basename \"$BUN_VIRTUAL_ENV\"`) ${PS1:-}"
    fi
    fi
    export PS1
fi

# This should detect bash and zsh, which have a hash command that must
# be called to get it to forget past commands.  Without forgetting
# past commands the $PATH changes we made may not be respected
if [ -n "${BASH:-}" -o -n "${ZSH_VERSION:-}" ] ; then
    hash -r
fi
"""


ACTIVATE_FISH = """

# This file must be used with "source bin/activate.fish" *from fish*
# you cannot run it directly

function deactivate_bun -d 'Exit bunenv and return to normal environment.'
    # reset old environment variables
    if test -n "$_OLD_BUN_VIRTUAL_PATH"
        set -gx PATH $_OLD_BUN_VIRTUAL_PATH
        set -e _OLD_BUN_VIRTUAL_PATH
    end

    if test -n "$_OLD_BUN_INSTALL"
        set -gx BUN_INSTALL $_OLD_BUN_INSTALL
        set -e _OLD_BUN_INSTALL
    else
        set -e BUN_INSTALL
    end

    if test -n "$_OLD_BUN_INSTALL_BIN"
        set -gx BUN_INSTALL_BIN $_OLD_BUN_INSTALL_BIN
        set -e _OLD_BUN_INSTALL_BIN
    else
        set -e BUN_INSTALL_BIN
    end

    if test -n "$_OLD_BUN_FISH_PROMPT_OVERRIDE"
        # Set an empty local `$fish_function_path` to allow the removal of
        # `fish_prompt` using `functions -e`.
        set -l fish_function_path

        # Prevents error when using nested fish instances
        if functions -q _bun_old_fish_prompt
            # Erase virtualenv's `fish_prompt` and restore the original.
            functions -e fish_prompt
            functions -c _bun_old_fish_prompt fish_prompt
            functions -e _bun_old_fish_prompt
        end
        set -e _OLD_BUN_FISH_PROMPT_OVERRIDE
    end

    set -e BUN_VIRTUAL_ENV

    if test (count $argv) = 0 -o "$argv[1]" != "nondestructive"
        # Self destruct!
        functions -e deactivate_bun
    end
end

# unset irrelevant variables
deactivate_bun nondestructive

# find the directory of this script
begin
    set -l SOURCE (status filename)
    while test -L "$SOURCE"
        set SOURCE (readlink "$SOURCE")
    end
    set -l DIR (dirname (realpath "$SOURCE"))

    # BUN_VIRTUAL_ENV is the parent of the directory where this script is
    set -gx BUN_VIRTUAL_ENV (dirname "$DIR")
end

set -gx _OLD_BUN_VIRTUAL_PATH $PATH
set -gx PATH "$BUN_VIRTUAL_ENV/__BIN_NAME__" $PATH

if set -q BUN_INSTALL
    set -gx _OLD_BUN_INSTALL $BUN_INSTALL
end
set -gx BUN_INSTALL "$BUN_VIRTUAL_ENV"

if set -q BUN_INSTALL_BIN
    set -gx _OLD_BUN_INSTALL_BIN $BUN_INSTALL_BIN
end
set -gx BUN_INSTALL_BIN "$BUN_VIRTUAL_ENV/__BIN_NAME__"

if test -z "$BUN_VIRTUAL_ENV_DISABLE_PROMPT"
    # Copy the current `fish_prompt` function as `_bun_old_fish_prompt`.
    functions -c fish_prompt _bun_old_fish_prompt

    function fish_prompt
        # Save the current $status, for fish_prompts that display it.
        set -l old_status $status

        # Prompt override provided?
        # If not, just prepend the environment name.
        if test -n "__BUN_VIRTUAL_PROMPT__"
            printf '%s%s ' "__BUN_VIRTUAL_PROMPT__" (set_color normal)
        else
            printf '%s(%s) ' (set_color normal) (basename "$BUN_VIRTUAL_ENV")
        end

        # Restore the original $status
        echo "exit $old_status" | source
        _bun_old_fish_prompt
    end

    set -gx _OLD_BUN_FISH_PROMPT_OVERRIDE "$BUN_VIRTUAL_ENV"
end
"""  # noqa: E501

PREDEACTIVATE_SH = """
if type -p deactivate_bun > /dev/null; then deactivate_bun;fi
"""

if __name__ == '__main__':
    main()
