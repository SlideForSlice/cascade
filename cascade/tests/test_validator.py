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
import pytest

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.tests.number_dataset import NumberDataset
from cascade.meta import DataValidationException, Validator, AggregateValidator, PredicateValidator


def test_modifier_interface():
    ds = NumberDataset([1, 2, 3, 4, 5])
    ds = Validator(ds, lambda x: True)
    assert([1, 2, 3, 4, 5] == [item for item in ds])


def test_aggregate_positive():
    ds = NumberDataset([1, 2, 3, 4, 5])
    ds = AggregateValidator(ds, lambda d: len(d) == 5)


def test_aggregate_negative():
    ds = NumberDataset([1, 2, 3, 4, 5])
    with pytest.raises(DataValidationException):
        ds = AggregateValidator(ds, lambda d: len(d) != 5)


def test_predicate_positive():
    ds = NumberDataset([1, 2, 3, 4, 5])
    ds = PredicateValidator(ds, lambda x: x < 6)


def test_predicate_negative():
    ds = NumberDataset([1, 2, 3, 4, 5])
    with pytest.raises(DataValidationException):
        ds = PredicateValidator(ds, lambda x: x > 3)
