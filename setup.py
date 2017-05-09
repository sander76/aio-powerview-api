from distutils.core import setup

setup(
    name='aiopvapi',
    version='1.0',
    packages=['aiopvapi'],
    url='https://github.com/sander76/aio-powerview-api',
    license='BSD License',
    author='Sander Teunissen',
    author_email='',
    description='Powerview blinds api',
    install_requires=[
        'async_timeout',
        'aiohttp',
        'yarl'
    ]
)
