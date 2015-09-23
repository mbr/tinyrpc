import sys

PY2 = sys.version_info[0] == 2

if PY2:
    import mock
else:
    from unittest import mock
