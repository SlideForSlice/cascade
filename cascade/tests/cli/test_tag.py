"""
Copyright 2022-2024 Ilia Moiseev

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

from click.testing import CliRunner

SCRIPT_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from cascade.base import MetaHandler
from cascade.cli.cli import cli
from cascade.repos import Repo


def test_add(tmp_path_str):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path_str) as td:
        mh = MetaHandler()
        repo = Repo(td)

        init_meta = mh.read_dir(td)

        result = runner.invoke(cli, args=["tag", "add", "hello"])

        assert result.exit_code == 0

        meta = mh.read_dir(td)

        assert "tags" in meta[0]
        assert len(meta[0]["tags"]) == 1
        assert "hello" in meta[0]["tags"]

        meta[0]["tags"] = []
        del meta[0]["updated_at"]
        del init_meta[0]["updated_at"]
        assert meta == init_meta


def test_ls(tmp_path_str):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path_str) as td:
        mh = MetaHandler()
        repo = Repo(td)

        init_meta = mh.read_dir(td)

        result = runner.invoke(cli, args=["tag", "add", "hello"])
        assert result.exit_code == 0

        result = runner.invoke(cli, args=["tag", "ls"])
        assert result.exit_code == 0

        assert "hello" in result.output


def test_rm(tmp_path_str):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path_str) as td:
        mh = MetaHandler()
        Repo(td)

        init_meta = mh.read_dir(td)

        result = runner.invoke(cli, args=["tag", "add", "hello"])
        assert result.exit_code == 0

        result = runner.invoke(cli, args=["tag", "rm", "hello"])
        assert result.exit_code == 0

        meta = mh.read_dir(td)

        assert "tags" in meta[0]
        assert len(meta[0]["tags"]) == 0

        del meta[0]["updated_at"]
        del init_meta[0]["updated_at"]
        assert meta == init_meta

        # Test of removing nonexisting tag
        result = runner.invoke(cli, args=["tag", "rm", "hello"])
        assert result.exit_code == 0
