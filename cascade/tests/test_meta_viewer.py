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
import json

MODULE_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(MODULE_PATH))

from cascade.meta import MetaViewer
from cascade.models import ModelRepo
from cascade.tests import DummyModel


def test(tmp_path):
    tmp_path = str(tmp_path)
    os.mkdir(os.path.join(tmp_path, 'model'))

    with open(os.path.join(tmp_path, 'test.json'), 'w') as f:
        json.dump({'name': 'test0'}, f)

    # Write also using mv
    mv = MetaViewer(tmp_path)
    mv.write(os.path.join(tmp_path, 'model', 'test.json'), {'name': 'test1'})    

    mv = MetaViewer(tmp_path)

    assert(len(mv) == 2)
    assert('name' in mv[0])
    assert('name' in mv[1])
    assert(mv[0]['name'] == 'test0')
    assert(mv[1]['name'] == 'test1')


def test_order(tmp_path):
    tmp_path = str(tmp_path)
    repo = ModelRepo(tmp_path)
    repo.add_line('line1', DummyModel)

    for i in range(3):
        model = DummyModel(real_num=i)
        repo['line1'].save(model)

    mv = MetaViewer(tmp_path)
    k = 0

    # This checks that models were read in exactly same order as they were saved
    # real_num should be [0, 1, 2]
    for meta in mv:
        if meta[0]['type'] == 'model':
            assert meta[0]['params']['real_num'] == k
            k += 1
