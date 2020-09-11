import setuptools

setuptools.setup(
    name='estore-server',
    version='0.0.1',
    description='Event Store Server',
    author='Jnxy',
    author_email='jnxy@lostwire.net',
    license='BSD',
    zip_safe=False,
    include_package_data=True,
    entry_points = { 'console_scripts': 'estore=estore.server.cli:cli'},
    install_requires = [
        'Click',
        'aiopg',
        'asyncio',
        'aiohttp',
        'aio-pika',
        'configparser2',
        'aiohttp-session',
    ],
    packages=setuptools.find_namespace_packages(include=['estore.*']))
