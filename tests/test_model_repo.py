"""
Copyright 2022 Ilia Moiseev

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

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
