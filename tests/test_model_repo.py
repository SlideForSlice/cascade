import os
import sys
import unittest
from unittest import TestCase

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.models import ModelRepo
from cascade.tests.dummy_model import DummyModel


class TestModelRepo(TestCase):
    def test_repo(self):
        import shutil

        repo = ModelRepo('./test_models', DummyModel)

        line1 = repo['dummy_1']
        line2 = repo['00001']

        self.assertTrue(os.path.exists('./test_models/dummy_1'))
        self.assertTrue(os.path.exists('./test_models/00001'))

        shutil.rmtree('./test_models')
        self.assertEqual(2, len(repo))


if __name__ == '__main__':
    unittest.main()
