from setuptools import setup, find_packages
from termx.version import get_version


VERSION = get_version()


f = open('README.md', 'r')
LONG_DESCRIPTION = f.read()
f.close()

setup(
    name='termx',
    version=VERSION,
    description=(
        'Advanced terminal library.'
    ),
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Nick Florin',
    author_email='nickmflorin@gmail.com',
    url='https://github.com/nickmflorin/termx',
    license='unlicensed',
    packages=find_packages(exclude=['ez_setup', 'tests*']),
)
