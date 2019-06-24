import os
from setuptools import setup, find_packages


"""
[x] NOTE:
--------
Once any import from termx is performed, simple_settings are lazily initialized
with the `TERMX_SIMPLE_SETTINGS` ENV variable.  If `TERMX_SIMPLE_SETTINGS` is not
set, it uses `dev` by default.

This means that if we want to use another settings file, we have to specify the
ENV variable before any import from termx is performed.
"""

os.environ['TERMX_SIMPLE_SETTINGS'] = 'prod'

from termx.core.config import settings  # noqa
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
        cleanroot = termx.main:cleanroot
    """,
)
