import inspect
import time
import unittest
from STOCKLAB.agent.ebest  import EBest

class TestEbest(unittest.TestCase):
    def setUp(self) -> None:
        self.ebest = EBest("DEMO")
        self.ebest.login()

    def test_get_code_list(self):
        print(inspect.stack()[0][3])
        result = self.ebest.get_code_list("ALL")
        assert result is not None
        print(len(result))
    
    def tearDown(self):
        self.ebest.logout()
