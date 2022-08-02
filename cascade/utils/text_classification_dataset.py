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
from typing import List, Dict

import numpy as np
from ..data import Dataset


class TextClassificationDataset(Dataset):
    """
    Dataset to simplify loading of data for text classification.
    Texts of different classes should be placed in different folders.
    """
    def __init__(self, path, encoding='utf-8', *args, **kwargs):
        """
        Parameters
        ----------
        path:
            Path to the folder with folders of text files.
            In each folder should be only one class of texts.
        """
        super().__init__(**kwargs)
        self._encoding = encoding
        self._root = os.path.abspath(path)
        folders = os.listdir(self._root)
        self._paths = []
        self._labels = []
        for i, folder in enumerate(folders):
            files = [name for name in os.listdir(os.path.join(self._root, folder))]
            self._paths += [os.path.join(self._root, folder, f) for f in files]
            self._labels += [i for _ in range(len(files))]

        print(f'Found {len(folders)} classes: \
            {[(folder, len(os.listdir(os.path.join(self._root, folder)))) for folder in folders]}')

    def __getitem__(self, index):
        with open(self._paths[index], 'r', encoding=self._encoding) as f:
            text = ' '.join(f.readlines())
            label = self._labels[index]
        return text, label

    def __len__(self):
        return len(self._paths)

    def get_meta(self) -> List[Dict]:
        meta = super().get_meta()
        meta[0].update({
                'name': repr(self),
                'size': len(self),
                'root': self._root,
                'labels': np.unique(self._labels).tolist()
            })
        return meta
