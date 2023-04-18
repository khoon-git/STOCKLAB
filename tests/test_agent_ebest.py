import inspect
import time
import unittest
from STOCKLAB.agent.ebest  import EBest

class TestEbest(unittest.TestCase):
    def setUp(self) -> None:
        self.ebest = EBest("DEMO")
        self.ebest.login()
    
    def tearDown(self):
        self.ebest.logout()