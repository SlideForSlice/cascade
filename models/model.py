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

from datetime import datetime
from typing import List, Dict


class Model:
    """
    Base class for any model.
    Used to provide unified interface to any model, store metadata including metrics.
    """
    def __init__(self, meta_prefix=None, **kwargs) -> None:
        """
        Should be called in any successor - initializes default meta needed.
        Arguments passed in it should be related to model's hyperparameters, architecture.
        All additional arguments should have defaults.
        Successors should pass all of their parameters to superclass for it to be able to
        log them in meta
        """
        if meta_prefix is None:
            meta_prefix = {}
        self.meta_prefix = meta_prefix
        self.metrics = {}
        self.params = kwargs
        self.created_at = datetime.now()

    def fit(self, *args, **kwargs):
        """
        Method to encapsulate training loops.
        May be provided with any training-related arguments.
        """
        raise NotImplementedError()

    def predict(self, *args, **kwargs):
        """
        Method to encapsulate inference.
        May include preprocessing steps to make model self-sufficient.
        """
        raise NotImplementedError()

    def evaluate(self, *args, **kwargs) -> None:
        """
        Evaluates model against any metrics. Should not return any values, just populating self.metrics dict.
        """
        raise NotImplementedError()

    def load(self, filepath) -> None:
        """
        Loads model from provided filepath. May be unpickling process or reading json configs.
        Does not return any model, just restores internal state.
        """
        raise NotImplementedError()

    def save(self, filepath) -> None:
        """
        Saves model's state using provided filepath.
        """
        raise NotImplementedError()

    def get_meta(self) -> List[Dict]:
        meta = {
            'created_at': self.created_at,
            'metrics': self.metrics,
            'params': self.params
        }
        meta.update(self.meta_prefix)
        return [meta]
