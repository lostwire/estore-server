from setuptools import setup, find_packages

setup(name='estore',
    version='0.0.1',
    description='Event Store',
    author='Jnxy',
    author_email='jnxy@lostwire.net',
    license='BSD',
    zip_safe=False,
    include_package_data=True,
    entry_points = { 'console_scripts': 'estore=estore.cli:cli'},
    install_requires = [
        'aiopg',
        'asyncio',
        'aiohttp',
        'Click',
        'aio-pika',
        'cryptography',
        'aiohttp-session',
        'configparser2',
    ],
    packages=find_packages())
