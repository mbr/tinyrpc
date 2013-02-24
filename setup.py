import os

from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='tinyrpc',
    version='0.6dev',
    description='A small, modular, transport and protocol neutral RPC '
                'library that, among other things, supports JSON-RPC and zmq.',
    long_description=read('README.rst'),
    packages=find_packages(exclude=['test', 'examples']),
    keywords='json rpc json-rpc jsonrpc 0mq zmq zeromq',
    author='Marc Brinkmann',
    author_email='git@marcbrinkmann.de',
    url='http://github.com/mbr/tinyrpc',
    license='MIT',
)
