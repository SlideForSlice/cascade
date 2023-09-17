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

import datetime
import os
import sys

import pytest

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))
from cascade.base import HistoryLogger, MetaHandler


@pytest.mark.parametrize("ext", [".json", ".yml", ".yaml"])
def test_repo(tmp_path, ext):
    tmp_path = str(tmp_path)
    tmp_path = os.path.join(tmp_path, "history" + ext)
    hl = HistoryLogger(tmp_path)

    obj = {"a": 0, "b": datetime.datetime.now()}

    hl.log(obj)
    obj_from_file = MetaHandler.read(tmp_path)

    assert "history" in obj_from_file
    assert "type" in obj_from_file
    assert len(obj_from_file["history"]) == 0
    assert obj_from_file["type"] == "history"

    obj = {"a": 1, "b": datetime.datetime.now()}

    hl.log(obj)
    obj_from_file = MetaHandler.read(tmp_path)

    assert "history" in obj_from_file
    assert "type" in obj_from_file
    assert len(obj_from_file["history"]) == 1
    assert obj_from_file["history"][0]["id"] == 0


def test_get_state(tmp_path):
    tmp_path = str(tmp_path)
    from cascade.base import HistoryLogger
    from cascade.data import Wrapper, Modifier

    hl = HistoryLogger(os.path.join(tmp_path, "diff_history.yml"))

    ds = Wrapper([1, 2])
    meta1 = ds.get_meta()
    hl.log(meta1)

    ds = Modifier(ds)
    meta2 = ds.get_meta()
    hl.log(meta2)

    assert hl.get(0) == meta1
    assert hl.get(1) == meta2
