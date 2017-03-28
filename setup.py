"""

"""
import os
from pip.req import parse_requirements
from setuptools import find_packages, setup

# parse_requirements() returns generator of pip.req.InstallRequirement objects
INSTALL_REQS = parse_requirements('requirements.txt')

# reqs is a list of requirements
# e.g. ['django==1.5.1', 'mezzanine==1.4.6']
REQUIREMENTS = [str(ir.req) for ir in INSTALL_REQS]

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='cyphon',
    version='1.0.1',
    install_requires=REQUIREMENTS,
    packages=find_packages(),
    include_package_data=True,
    license='GNU General Public License v3 (GPLv3)',
    description='Cyphon Engine',
    long_description=README,
    url='https://cyphon.io/',
    author='Dunbar Cybersecurity',
    author_email='leila.hadj-chikh@dunbarsecured.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.10',  # replace "X.Y" as appropriate
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
)
