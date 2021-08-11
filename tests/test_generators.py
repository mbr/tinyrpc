#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tinyrpc.generators as generators
import re
import uuid

def test_decimal_generator():
	g = generators.decimal_generator(1)
	assert next(g) == 1
	assert next(g) == 2
	assert next(g) == 3

def test_hexadecimal_generator():
	g = generators.hexadecimal_generator()
	assert next(g) == "1"
	g = generators.hexadecimal_generator(9)
	assert next(g) == "9"
	assert next(g) == "a"


def test_random_generator():
	g = generators.random_generator()
	assert re.match("^[0-9,a-z]{8}$", next(g))

def test_uuid_generator():
	g = generators.uuid_generator()
	# verify using regex
	pattern = "^[0-9,a-z]{8}-[0-9,a-z]{4}-[0-9,a-z]{4}-[0-9,a-z]{4}-[0-9,a-z]{12}$"
	assert re.match(pattern, next(g))
	# Raise ValueError if badly formed hexadecimal UUID string
	uuid.UUID(next(g), version=4)