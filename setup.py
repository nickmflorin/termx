from setuptools import setup, find_packages

from termx import __NAME__, __FORMAL_NAME__
from termx.config import config


VERSION = config.version()


f = open('README.md', 'r')
LONG_DESCRIPTION = f.read()
f.close()

setup(
    name=__NAME__,
    version=VERSION,
    description=__FORMAL_NAME__,
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
