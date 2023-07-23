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

import glob
import os
import shutil
import sys

import pytest

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.tests.conftest import DummyModel, ModelLine


@pytest.mark.parametrize("only_meta", [True, False])
def test_save_load(model_line, dummy_model, only_meta):
    dummy_model.a = 0
    dummy_model.params.update({"b": "test"})

    model_line.save(dummy_model, only_meta=only_meta)
    model = model_line[0]

    assert len(model_line) == 1
    assert model.a == 0
    assert model.params["b"] == "test"


def test_meta(model_line, dummy_model):
    model_line.save(dummy_model)
    meta = model_line.get_meta()

    assert meta[0]["model_cls"] == repr(DummyModel)
    assert meta[0]["len"] == 1


@pytest.mark.parametrize("ext", [".json", ".yml", ".yaml"])
def test_change_of_format(tmp_path, ext):
    tmp_path = str(tmp_path)
    ModelLine(tmp_path, meta_fmt=ext)

    assert os.path.exists(os.path.join(tmp_path, "meta" + ext))

    ModelLine(tmp_path)

    # Check that no other meta is created
    assert len(glob.glob(os.path.join(tmp_path, "meta.*"))) == 1


def test_same_index_check(model_line, dummy_model):
    for _ in range(5):
        dummy_model.evaluate()
        model_line.save(dummy_model)

    shutil.rmtree(os.path.join(model_line.get_root(), "00001"))
    shutil.rmtree(os.path.join(model_line.get_root(), "00002"))
    shutil.rmtree(os.path.join(model_line.get_root(), "00003"))

    model_line.save(dummy_model)

    assert os.path.exists(os.path.join(model_line.get_root(), "00005"))


@pytest.mark.parametrize("arg", ["num", "slug"])
def test_load_model_meta(model_line, dummy_model, arg):
    slug = dummy_model.slug
    dummy_model.evaluate()
    model_line.save(dummy_model)

    if arg == "num":
        meta = model_line.load_model_meta(0)
    elif arg == "slug":
        meta = model_line.load_model_meta(slug)
    else:
        raise RuntimeError(arg)

    assert len(meta) == 1
    assert "metrics" in meta[0]
    assert "acc" in meta[0]["metrics"]
