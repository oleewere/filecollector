import unittest
from filecollector import collector
try:
    from unittest.mock import MagicMock
except ImportError as error:
    from mock import MagicMock

class TestCollector(unittest.TestCase):

    def test_main(self):
        #collector.main(["--config", "myconfig"])
        pass

if __name__ == '__main__':
    unittest.main()