import sys

collect_ignore = ["setup.py"]
if sys.version_info.major == 3 and 4 <= sys.version_info.minor <= 5:
    collect_ignore.append("tests/test_asyncio_dispatch.py")
elif sys.version_info.major == 3 and sys.version_info.minor >= 6:
    collect_ignore.append("tests/test_asyncio_dispatch_34.py")