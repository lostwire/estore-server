from setuptools import setup, find_packages

setup(name='estore',
    version='0.0.1',
    description='Event Store',
    author='Jnxy',
    author_email='jnxy@lostwire.net',
    license='BSD',
    zip_safe=False,
    include_package_data=True,
    install_requires = [
        'asynctio',
        'aiohttp'
    ],
    packages=find_packages())
