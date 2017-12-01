from distutils.core import setup
from setuptools import find_packages

VERSION = "1.5.7"

setup(
    name='aiopvapi',
    version=VERSION,
    packages=find_packages(exclude='tests'),
    download_url='https://github.com/sander76/aio-powerview-api/archive/' + VERSION + '.tar.gz',
    url="https://github.com/sander76/aio-powerview-api",
    license='BSD License',
    author='Sander Teunissen',
    classifiers=[
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    author_email='',
    description='Powerview blinds api',
    install_requires=[
        'async_timeout',
        'aiohttp',
        'yarl'
    ]
)
