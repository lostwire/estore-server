import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='estore-server',
    version='0.0.1',
    description='Event Store Server',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Jnxy',
    author_email='jnxy@lostwire.net',
    license='BSD',
    url='https://github.com/lostwire/estore-server',
    entry_points = { 'console_scripts': 'estore=estore.server.cli:cli'},
    install_requires = [
        'Click',
        'aiopg',
        'pypika',
        'asyncio',
        'aiohttp',
        'asyncstdlib',
        'configparser2',
        'aiohttp-session',
        'estore-base',
    ],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Framework :: AsyncIO",
        "Environment :: Web Environment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Database" ],
    packages=setuptools.find_namespace_packages(include=['estore.*']))
