#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generators which yield an id to include in an RPC request."""

import itertools
from random import choice
from string import ascii_lowercase, digits
from typing import Generator
from uuid import uuid4


def decimal_generator(start: int = 1) -> Generator[int, None, None]:
    """Generates sequential integers from `start`.

    e.g. 1, 2, 3, .. 9, 10, 11, ...

    :param start: The first value to start with.
    :type start: int
    :return: A generator that yields a sequence of integers.
    :rtype: :py:class:`Generator[int, None, None]`
    """
    return itertools.count(start)


def hexadecimal_generator(start: int = 1) -> Generator[str, None, None]:
    """Generates sequential hexadecimal values from `start`.

    e.g. 1, 2, 3, .. 9, a, b, ...

    :param start: The first value to start with.
    :type start: int
    :return: A generator that yields a sequence of integers in hex format.
    :rtype: :py:class:`Generator[int, None, None]`
    """
    while True:
        yield "%x" % start
        start += 1


def random_generator(length: int = 8, chars: str = digits + ascii_lowercase) -> Generator[str, None, None]:
    """Generates a random string.

    Not unique, but has around 1 in a million chance of collision (with the default 8
    character length). e.g. 'fubui5e6'

    :param length: Length of the random string.
    :type length: int
    :param chars: The characters to randomly choose from.
    :type chars: str
    :return: A generator that yields a random string.
    :rtype: :py:class:`Generator[int, None, None]`
    """
    while True:
        yield "".join([choice(chars) for _ in range(length)])


def uuid_generator() -> Generator[str, None, None]:
    """Generates unique uuid4 ids.

    For example, '9bfe2c93-717e-4a45-b91b-55422c5af4ff'

    :return: A generator that yields a uuid4.
    :rtype: :py:class:`Generator[int, None, None]`
    """
    while True:
        yield str(uuid4())
