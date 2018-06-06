# -*- coding: utf-8 -*-

from setuptools import setup

__author__ = "Austin Zadoks"
__license__ = "GPLv3, see LICENSE file"

about = {}
with open('zocrys/version.py') as f:
    exec (f.read(), about)

setup(
    name="zocrys",
    version=about['__version__'],
    description='Austin Zadoks crystal structure tools',
    long_description=open('README.md').read(),
    url='https://github.com/zooks97/structureREST.git',
    author='Austin Zadoks',
    author_email='zooks97@gmail.com',
    license=__license__,
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    # Abstract dependencies.  Concrete versions are listed in
    # requirements.txt
    # See https://caremad.io/2013/07/setup-vs-requirement/ for an explanation
    # of the difference and
    # http://blog.miguelgrinberg.com/post/the-package-dependency-blues
    # for a useful dicussion
    install_requires=[
    ],
    packages=['zocrys', 'zocrys.aiida'],  # , 'zocrys.mongo', 'zocrys.rest'
    test_suite='test'
)
