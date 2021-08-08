import os

from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='tinyrpc',
    version='1.1.0',
    description='A small, modular, transport and protocol neutral RPC '
                'library that, among other things, supports JSON-RPC and zmq.',
    long_description=read('README.rst'),
    long_description_content_type="text/x-rst",
    packages=find_packages(exclude=['tests', 'examples']),
    keywords='json rpc json-rpc jsonrpc 0mq zmq zeromq',
    author='Marc Brinkmann',
    author_email='git@marcbrinkmann.de',
    maintainer='Leo Noordergraaf',
    maintainer_email='leo@noordergraaf.net',
    url='http://github.com/mbr/tinyrpc',
    license='MIT',
    install_requires=['six'],
    extras_require={
        'gevent': ['gevent'],
        'httpclient': ['requests', 'websocket-client', 'gevent-websocket'],
        'msgpack': ['msgpack'],
        'websocket': ['gevent-websocket'],
        'wsgi': ['werkzeug'],
        'zmq': ['pyzmq'],
        'jsonext': ['jsonext'],
        'rabbitmq': ['pika']
    }
)
