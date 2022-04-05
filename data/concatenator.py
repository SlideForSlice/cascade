from typing import List, Dict, Iterable

import numpy as np
from .dataset import Dataset, T


class Concatenator(Dataset):
    """
    Unifies several Datasets under one, calling them sequentially in the provided order.
    """
    def __init__(self, datasets: Iterable[Dataset]) -> None:
        """
        Creates concatenated dataset from the list of datasets provided

        Parameters:
        -----------
        datasets: Iterable[Dataset]
            a list or tuple of datasets to concatenate
        """
        self._datasets = datasets
        lengths = [len(ds) for ds in self._datasets]
        self.shifts = np.cumsum([0] + lengths)

    def __getitem__(self, index) -> T:
        ds_index = 0
        for sh in self.shifts[1:]:
            if index >= sh:
                ds_index += 1
        return self._datasets[ds_index][index - self.shifts[ds_index]]

    def __len__(self) -> int:
        """
        Length of Concatenator is a sum of lengths of its datasets
        """
        return sum([len(ds) for ds in self._datasets])

    def __repr__(self) -> str:
        """
        Mentions joined datasets in its repr in form:
        Concatenator of
        Dataset1
        Dataset2
        ...
        """
        rp = super().__repr__()
        return f'{rp} of\n' + '\n'.join(repr(ds) for ds in self._datasets)

    def get_meta(self) -> List[Dict]:
        """
        Concatenator calls `get_meta()` of all its datasets and appends to its own meta
        """
        meta = super().get_meta()
        for ds in self._datasets:
            meta += ds.get_meta()
        return meta
