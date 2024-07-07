import os
from collections import defaultdict
from hashlib import md5
from typing import Any, Literal, Type

import pendulum

from ..base import Meta, MetaHandler
from ..base.utils import Version, skeleton
from ..data.dataset import Dataset
from .disk_line import DiskLine


class DataLine(DiskLine):
    def __init__(
        self,
        root: str,
        ds_cls: Type[Any] = Dataset,
        meta_fmt: Literal[".json", ".yml", ".yaml"] = ".json",
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(root, item_cls=ds_cls, meta_fmt=meta_fmt, *args, **kwargs)
        self._hashes = defaultdict(dict)
        for name in self._item_names:
            with open(os.path.join(self._root, name, "HASHES"), "r") as f:
                skel_hash, meta_hash = f.read().split("\n")
                self._hashes[skel_hash] = defaultdict(dict)
                self._hashes[skel_hash][meta_hash] = Version(name)

    def load(self, num: int) -> None:
        raise NotImplementedError()

    def save(self, ds: Dataset, only_meta: bool = True) -> None:
        meta = ds.get_meta()
        obj_type = meta[0].get("type")
        if obj_type != "dataset":
            raise ValueError(
                f"Can only save meta of type `dataset` into a DataLine, got {obj_type}"
            )

        skel = skeleton(meta)

        skel_str = str(skel)
        meta_str = str(meta)

        skel_hash = md5(str.encode(skel_str, "utf-8")).hexdigest()
        meta_hash = md5(str.encode(meta_str, "utf-8")).hexdigest()

        if skel_hash in self._hashes:
            if meta_hash in self._hashes[skel_hash]:
                version = self._hashes[skel_hash][meta_hash]
            else:
                max_version = max(list(self._hashes[skel_hash].values()))
                version = max_version.bump_minor()
        else:
            if len(self._hashes):
                max_version = Version("0.1")
                for sh in self._hashes:
                    for mh in self._hashes[sh]:
                        if self._hashes[sh][mh] > max_version:
                            max_version = self._hashes[sh][mh]
                version = max_version.bump_major()
            else:
                version = Version("0.1")

        version_str = str(version)

        self._hashes[skel_hash][meta_hash] = version
        full_path = os.path.join(self._root, version_str)

        meta[0]["path"] = full_path
        meta[0]["saved_at"] = pendulum.now(tz="UTC")

        os.makedirs(full_path, exist_ok=True)
        MetaHandler.write(os.path.join(full_path, "meta" + self._meta_fmt), meta)

        with open(os.path.join(self._root, version_str, "HASHES"), "w") as f:
            f.write("\n".join([skel_hash, meta_hash]))

        self._item_names.append(version_str)
        self.sync_meta()

    def __getitem__(self, num: int) -> Any:
        raise NotImplementedError()

    def get_meta(self) -> Meta:
        meta = super().get_meta()
        meta[0].update({"type": "data_line"})
        return meta
