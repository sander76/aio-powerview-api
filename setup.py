from distutils.core import setup

with open('README.rst') as f:
    long_description = f.read()

VERSION = "1.1"

setup(
    name='aiopvapi',
    version=VERSION,
    packages=['aiopvapi'],
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
    long_description=long_description,
    install_requires=[
        'async_timeout',
        'aiohttp',
        'yarl'
    ]
)
