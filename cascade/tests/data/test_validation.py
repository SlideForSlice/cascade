"""
Copyright 2022-2023 Ilia Moiseev

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

from cascade.data import validate, ValidationError


def test_no_annot():
    def add(a, b):
        return a + b

    validate(add)(1, 2)
    validate(add)("a", "b")


def test_default_types():
    def add_int(a: int, b: int):
        return a + b

    validate(add_int)(1, 2)

    with pytest.raises(ValidationError):
        validate(add_int)("a", 2)

    with pytest.raises(ValidationError):
        validate(add_int)(1, "b")

    with pytest.raises(ValidationError):
        validate(add_int)("a", "b")

    with pytest.raises(ValidationError):
        validate(add_int)(1.2, 3.4)