import sys

if 4 <= sys.version_info.minor <= 5:
    from ._asyncio_34 import *
else:
    assert sys.version_info.minor >= 6
    from ._asyncio import *