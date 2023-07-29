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
from cascade.models import ModelRepo, Workspace


def test(tmp_path):
    tmp_path = str(tmp_path)
    for i in range(10):
        ModelRepo(os.path.join(tmp_path, f"repo-{i}"))

    wp = Workspace(tmp_path, default_repo="repo-1")

    assert len(wp) == 10
    assert wp.get_repo_names() == [f"repo-{i}" for i in range(10)]
    assert wp.get_default().get_root() == os.path.join(tmp_path, "repo-1")
    wp.set_default("repo-2")
    assert wp.get_default().get_root() == os.path.join(tmp_path, "repo-2")


def test_meta(tmp_path):
    tmp_path = str(tmp_path)

    for i in range(10):
        ModelRepo(os.path.join(tmp_path, f"repo-{i}"))

    wp = Workspace(tmp_path)

    meta = wp.get_meta()
    assert meta[0]["root"] == tmp_path
    assert meta[0]["len"] == 10
    assert meta[0]["type"] == "workspace"


@pytest.mark.parametrize("ext", [".json", ".yml", ".yaml"])
@pytest.mark.parametrize("arg", ["path", "slug"])
def test_load_model_meta(tmp_path, dummy_model, arg, ext):
    tmp_path = str(tmp_path)

    for i in range(2):
        ModelRepo(os.path.join(tmp_path, f"repo-{i}"))

    repo = ModelRepo(os.path.join(tmp_path, "repo"), meta_fmt=ext)
    repo.add_line()
    repo.add_line()
    line = repo.add_line()

    wp = Workspace(tmp_path)

    slug = dummy_model.slug
    dummy_model.evaluate()
    line.save(dummy_model)

    if arg == "path":
        meta = wp.load_model_meta("repo/00002/00000")
    elif arg == "slug":
        meta = wp.load_model_meta(slug)
    else:
        raise RuntimeError(arg)

    assert len(meta) == 1
    assert "metrics" in meta[0]
    assert "acc" in meta[0]["metrics"]
    assert slug == meta[0]["slug"]
