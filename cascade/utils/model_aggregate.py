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

import warnings
from typing import List, Dict
import pickle
import pandas as pd
from ..models import Model


class ModelAggregate(Model):
    def __init__(self, models=None, agg_func='mean', **kwargs):
        raise RuntimeError('ModelAggregate is not supported since 0.7.0')
