"""Run Python regressions with real DNS and socket connections prohibited."""
import pathlib
import socket
import sys
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

def blocked(*args, **kwargs):
    raise AssertionError('Real network access is prohibited during fixture tests')

if __name__ == '__main__':
    with patch.object(socket, 'getaddrinfo', blocked), \
         patch.object(socket.socket, 'connect', blocked), \
         patch.object(socket.socket, 'connect_ex', blocked):
        suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'))
        result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(not result.wasSuccessful())
