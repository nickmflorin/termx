import os
from pathlib import Path
from setuptools import setup, find_packages
from simple_settings import settings

"""
[x] NOTE:
--------
Once any import from termx is performed, simple_settings tries to load and
configure the settings.  Since we cannot pass in settings as a command line
argument for setuptools, nor should we require that, we need to set the
ENV variable SIMPLE_SETTINGS.

All of this needs to be done before any import from the main package.

We set this ENV variable to 'termx.<settings_file_dir>.<settings_file>',
where settings_file is extensionless.  We should use a settings file that only
contains the minimum, if anything.

i.e. termx.config.setup (if the settings file is in ./termx/config/setup.py)
"""

SETUP_SETTINGS = ('config', 'settings', 'prod.py')


def get_simple_settings_path():
    """
    Validates whether or not the setup settings file exists at the location
    given by SETUP_SETTINGS and formats the filepath into a suitable string
    for simple_settings.

    [x] NOTE:
    --------
    A logical question might be why not just hardcode in (termx.config.settings.base.py).
    For starters, we want to get the full path to raise a more helpful exception
    if the settings are missing.  Second, we are forward thinking a little bit
    in the sense that we might want to use this logic for more than once use
    case.

    Ideally, since __NAME__ is specified in the settings module, which
    we cannot load yet, we would want to write this as if we have no knowledge
    of the app name.  The only issue with that is getting the `app_root`, but
    if we move the settings file to the top level, we can avoid that.
    """
    cwd = os.getcwd()
    app_root = os.path.join(cwd, 'termx')
    settings_file = os.path.join(app_root, *SETUP_SETTINGS)

    settings_path = Path(settings_file)
    if not settings_path.is_file():
        raise RuntimeError('Installation settings file missing at %s.' % settings_file)

    # Get Path Parts Starting with `term` (i.e. [termx, ..., ...])
    app_index = settings_path.parts.index('config') - 1
    parts = list(settings_path.parts[-app_index:])

    # Last Component is Extension-less for simple_settings
    parts[-1] = settings_path.name.replace(settings_path.suffix, '')
    return '.'.join(parts)


simple_settings_file = get_simple_settings_path()
os.environ['SIMPLE_SETTINGS'] = simple_settings_file

from termx.library import get_version  # noqa

f = open('README.md', 'r')
LONG_DESCRIPTION = f.read()
f.close()

setup(
    name=settings.NAME,
    version=get_version(settings.VERSION),
    description=settings.FORMAL_NAME,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Nick Florin',
    author_email='nickmflorin@gmail.com',
    url='https://github.com/nickmflorin/termx',
    license='unlicensed',
    packages=find_packages(exclude=['ez_setup', 'tests*']),
    entry_points="""
        [console_scripts]
        playground = termx.main:run_playground
        clean = termx.main:clean
    """,
)
