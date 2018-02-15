from distutils.core import setup
from setuptools import find_packages


def readme():
    with open('README.rst') as f:
        return f.read()


VERSION = "1.6.0"

setup(
    name='aiopvapi',
    version=VERSION,
    packages=find_packages(exclude='tests'),
    long_description=readme(),
    download_url='https://github.com/sander76/aio-powerview-api/archive/' + VERSION + '.tar.gz',
    url="https://github.com/sander76/aio-powerview-api",
    license='Apache License 2.0',
    author='Sander Teunissen',
    classifiers=[
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    author_email='',
    description='Powerview blinds api',
    install_requires=[
        'async_timeout',
        'aiohttp'
    ]
)
