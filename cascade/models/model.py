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

import warnings
from typing import Any, Union

import pendulum

from ..base import PipeMeta, Traceable, raise_not_implemented
from ..base.utils import generate_slug


class Model(Traceable):
    """
    Base class for any model.
    Used to provide unified interface to any model, store metadata including metrics.
    """

    def __init__(
        self, *args: Any, meta_prefix: Union[PipeMeta, str, None] = None, **kwargs: Any
    ) -> None:
        """
        Should be called in any successor - initializes default meta needed.

        Successors may pass all of their parameters to superclass for it to be able to
        log them in meta. Everything that is worth to document about model and data
        it was trained on can be put either in params or meta_prefix.
        """
        self.slug = generate_slug()
        self.metrics = {}
        self.params = kwargs
        self.created_at = pendulum.now(tz="UTC")
        # Model accepts meta_prefix explicitly to not to record it in 'params'
        super().__init__(*args, meta_prefix=meta_prefix, **kwargs)

    def fit(self, *args: Any, **kwargs: Any) -> None:
        """
        Method to encapsulate training loops.
        May be provided with any training-related arguments.
        """
        raise_not_implemented("cascade.models.Model", "fit")

    def predict(self, *args: Any, **kwargs: Any) -> Any:
        """
        Method to encapsulate inference.
        May include preprocessing steps to make model self-sufficient.
        """
        raise_not_implemented("cascade.models.Model", "predict")

    def evaluate(self, *args: Any, **kwargs: Any) -> None:
        """
        Evaluates model against any metrics. Should not return any value, just populate self.metrics dict.
        """
        raise_not_implemented("cascade.models.Model", "evaluate")

    @classmethod
    def load(cls, path: str, *args: Any, **kwargs: Any) -> "Model":
        """
        Loads model from provided path
        """
        raise_not_implemented("cascade.models.Model", "load")

    def save(self, path: str, *args: Any, **kwargs: Any) -> None:
        """
        Saves model's state using provided filepath.
        """
        raise_not_implemented("cascade.models.Model", "save")

    def get_meta(self) -> PipeMeta:
        # Successors may not call super().__init__
        # they may not have these default fields

        meta = super().get_meta()
        meta[0]["type"] = "model"

        all_default_exist = True
        for attr in ("slug", "created_at", "metrics", "params"):
            if hasattr(self, attr):
                meta[0][attr] = self.__getattribute__(attr)
            else:
                all_default_exist = False

        if not all_default_exist:
            warnings.warn(
                "Model's meta is incomplete, "
                "maybe you haven't call super().__init__ in subclass?"
            )

        return meta


class ModelModifier(Model):
    """
    Analog of dataset's Modifier. Can be used to chain
    two models in one.
    """

    def __init__(self, model: Model, *args: Any, **kwargs: Any) -> None:
        """
        Parameters
        ----------
        model: Model
            A model to modify.
        """
        self._model = model
        super().__init__(*args, **kwargs)

    def get_meta(self) -> PipeMeta:
        prev_meta = self._model.get_meta()
        return super().get_meta() + prev_meta
