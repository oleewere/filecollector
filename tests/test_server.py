import unittest
import os
from filecollector import server
try:
    from unittest.mock import MagicMock
except ImportError as error:
    from mock import MagicMock

script_dir=os.path.dirname(os.path.abspath(__file__))

class TestCollector(unittest.TestCase):

    def test_empty_collector(self):
        try:
            server.main(["--config", os.path.join(script_dir, "files/empty_server.yaml")])
            self.fail("Server startshould fail")
        except Exception: 
            self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()