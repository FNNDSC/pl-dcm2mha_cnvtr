from os import path
from setuptools import setup

with open(path.join(path.dirname(path.abspath(__file__)), 'README.rst')) as f:
    readme = f.read()

setup(
    name             = 'dcm2mha_cnvtr',
    version          = '1.2.25',
    description      = 'An app to convert dcm files to mha and vice-versa',
    long_description = readme,
    author           = 'FNNDSC',
    author_email     = 'dev@babyMRI.org',
    url              = 'https://github.com/FNNDSC/pl-dcm2mha_cnvtr#readme',
    packages         = ['dcm2mha_cnvtr'],
    install_requires = ['chrisapp'],
    test_suite       = 'nose.collector',
    tests_require    = ['nose'],
    license          = 'MIT',
    zip_safe         = False,
    python_requires  = '>=3.6',
    entry_points     = {
        'console_scripts': [
            'dcm2mha_cnvtr = dcm2mha_cnvtr.__main__:main'
            ]
        }
)
