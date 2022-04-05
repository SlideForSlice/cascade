from typing import Dict, Generic, Iterable, List, TypeVar

T = TypeVar('T')


class Dataset(Generic[T]):
    """
    Base class of any module that constitues a data-pipeline.
    In its basic idea is similar to torch.utils.data.Dataset.
    It does not define `__len__` for similar reasons.
    See `pytorch/torch/utils/data/sampler.py` note on this topic.
    """
    def __getitem__(self, index) -> T:
        """
        Abstract method - should be defined in every successor
        """
        raise NotImplementedError

    def get_meta(self) -> List[Dict]:
        """
        Base method that should be called using super() in every successor.

        Returns
        -------
        meta: List[Dict]
            A list with one element, which is this dataset's metadata.
            Meta can be anything that is worth to document about the dataset and its data.
            This is done in form of list to enable cascade-like calls in Modifiers and Samplers.
        """
        return [{'name': repr(self)}]


class Iterator(Generic[T]):
    def __init__(self, data: Iterable):
        self._data = data

    def __iter__(self):
        for item in self._data:
            yield item


class Wrapper(Dataset):
    """
    Wraps Dataset around any list-like object.
    """
    def __init__(self, obj) -> None:
        self._data = obj

    def __getitem__(self, index) -> T:
        return self._data[index]

    def __len__(self) -> int:
        return len(self._data)


class Modifier(Dataset):
    """
    Basic pipeline building block in Cascade. Every block which is not a data source should be a successor
    of Sampler or Modifier.
    This structure enables a workflow, when we have a data pipeline which consists of uniform blocks
    each of them has a reference to the previous one in its `_dataset` field. See get_meta method for example.

    Basically Modifier defines an arbitrary transformation on every dataset's item that is applied
    in a lazy manner on each `__getitem__` call.
    Applies no transformation if `__getitem__` is not overridden.
    """
    def __init__(self, dataset: Dataset) -> None:
        """
        Constructs a Modifier. Makes no transformations in initialization.

        Parameters
        ----------
        dataset: Dataset
            a dataset to modify
        """
        self._dataset = dataset
        self._index = -1

    def __getitem__(self, index) -> T:
        return self._dataset[index]

    def __iter__(self):
        self._index = -1
        return self

    def __next__(self) -> T:
        if self._index < len(self) - 1:
            self._index += 1
            return self[self._index]
        else:
            self._index = -1
            raise StopIteration()

    def __len__(self) -> int:
        return len(self._dataset)

    def __repr__(self) -> str:
        rp = super().__repr__()
        return f'{rp} of size: {len(self)}'

    def get_meta(self) -> List[Dict]:
        """
        Overrides base method enabling cascade-like calls to previous datasets.
        The metadata of a pipeline that consist of several modifiers can be easily
        obtained with `get_meta` of the last block.
        """
        self_meta = super().get_meta()
        self_meta += self._dataset.get_meta()
        return self_meta


class Sampler(Modifier):
    """
    Defines certain sampling over a Dataset. Its distinctive feature is that it changes the number of
    items in dataset. It can constitute a batch sampler or random sampler or sample in cycling manner.

    See also:
    ---------
    cascade.data.CyclicSampler
    """
    def __init__(self, dataset: Dataset, num_samples: int) -> None:
        assert num_samples > 0
        super(Sampler, self).__init__(dataset)
        self._num_samples = num_samples

    def __len__(self) -> int:
        return self._num_samples

    def __repr__(self) -> str:
        rp = super().__repr__()
        return f'{rp} num_samples: {self._num_samples}'
