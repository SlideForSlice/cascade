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
import shutil
import pytest
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

MODULE_PATH = os.path.dirname(
    os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
)
sys.path.append(os.path.dirname(MODULE_PATH))


import cascade as csd
from cascade.utils.sk_model import SkModel


@pytest.mark.parametrize("ext", [".json", ".yml"])
def test_hash_check(tmp_path, ext):
    tmp_path = str(tmp_path)
    repo = csd.models.ModelRepo(tmp_path, overwrite=True, meta_fmt=ext)

    tree = SkModel(blocks=[DecisionTreeClassifier()])

    forest = SkModel(blocks=[RandomForestClassifier()])

    line = repo.add_line("tree", SkModel)
    line.save(tree)
    line.save(forest)

    # This should pass
    tree.load(os.path.join(tmp_path, "tree", "00000", "model"))

    # This should fail
    shutil.move(
        os.path.join(tmp_path, "tree", "00001", "model.pkl"),
        os.path.join(tmp_path, "tree", "00000", "model.pkl"),
    )

    with pytest.raises(RuntimeError):
        tree.load(os.path.join(tmp_path, "tree", "00000", "model"))


@pytest.mark.parametrize("postfix", ["", "model", "model.pkl"])
def test_save_load(tmp_path, postfix):
    tmp_path = str(tmp_path)

    if postfix:
        tmp_path = os.path.join(tmp_path, postfix)

    model = SkModel(blocks=[RandomForestClassifier()])

    model.save(tmp_path)

    model = SkModel.load(tmp_path)
