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
import itertools
import os
import logging
from typing import List, Dict, Iterable
import shutil

import pendulum
from deepdiff.diff import DeepDiff

from ..base import Traceable
from .model_line import ModelLine
from ..meta import MetaViewer


class Repo(Traceable):
    """
    Base interface for repos of models.

    See also
    --------
    cascade.models.ModelRepo
    """
    root = None

    def add_line(self, *args, **kwargs):
        raise NotImplementedError()

    def __getitem__(self, key):
        raise NotImplementedError()
    
    def __len__(self):
        raise NotImplementedError()


class ModelRepo(Repo):
    """
    An interface to manage experiments with several lines of models.
    When created, initializes an empty folder constituting a repository of model lines.
    
    Stores meta-data in file meta.json in the root folder. With every run if the repo was already
    created earlier, updates its meta and logs changes in human-readable format in file history.log

    Example
    -------
    >>> from cascade.models import ModelRepo
    >>> repo = ModelRepo('repo', _meta_prefix={'description': 'This is a repo with one VGG16 line for the example.'})
    >>> vgg16_line = repo.add_line('vgg16', VGG16Model)
    >>> vgg16 = VGG16Model()
    >>> vgg16.fit()
    >>> vgg16_line.save(vgg16)


    >>> from cascade.models import ModelRepo
    >>> repo = ModelRepo('repo', lines=[dict(name='vgg16', model_cls=VGGModel)])
    >>> vgg16 = VGG16Model()
    >>> vgg16.fit()
    >>> repo['vgg16'].save(vgg16)
    """
    def __init__(self, folder, lines=None, overwrite=False, meta_fmt='.json', **kwargs):
        """
        Parameters
        ----------
        folder:
            Path to a folder where ModelRepo needs to be created or already was created
            if folder does not exist, creates it
        lines: List[Dict]
            A list with parameters of model lines to add at creation or to initialize (alias for `add_model`)
        overwrite: bool
            if True will remove folder that is passed in first argument and start a new repo
            in that place
        meta_fmt: str
            extension of repo's metadata files and that will be assigned to the lines by default
            `.json` and `.yml` are supported
        See also
        --------
        cascade.models.ModelLine
        """
        super().__init__(**kwargs)
        self.root = folder

        supported_formats = ('.json', '.yml')
        assert meta_fmt in supported_formats, f'Only {supported_formats} are supported formats'
        self._meta_fmt = meta_fmt
        if overwrite and os.path.exists(self.root):
            shutil.rmtree(folder)

        self._setup_logger()
        if os.path.exists(self.root):
            assert os.path.isdir(folder)
            # Can create MeV only if path already exists
            self._mev = MetaViewer(self.root)
            self.lines = {name: ModelLine(os.path.join(self.root, name),
                                          meta_prefix=self._meta_prefix,
                                          meta_fmt=self._meta_fmt)
                          for name in sorted(os.listdir(self.root))
                          if os.path.isdir(os.path.join(self.root, name))}
        else:
            os.mkdir(self.root)
            # Here the same with MV
            self._mev = MetaViewer(self.root)
            self.lines = dict()

        if lines is not None:
            for line in lines:
                self.add_line(**line)

        self._update_meta()

    def add_line(self, name, *args, meta_fmt=None, **kwargs):
        """
        Adds new line to repo if it doesn't exist and returns it
        If line exists, defines it in repo

        Supports all the parameters of ModelLine using args and kwargs.

        Parameters:
            name: str
                Name of the line. It is used to name a folder of line.
                Repo prepends it with `self.root` before creating.
            meta_fmt: str
                Format of meta files. Supported values are the same as for repo.
                If omitted, inherits format from repo.
        See also
        --------
            cascade.models.ModelLine
       """

        folder = os.path.join(self.root, name)
        if meta_fmt is None:
            meta_fmt = self._meta_fmt
        line = ModelLine(folder,
                         *args,
                         meta_prefix=self._meta_prefix,
                         meta_fmt=meta_fmt,
                         **kwargs)
        self.lines[name] = line

        self._update_meta()
        return line

    def __getitem__(self, key) -> ModelLine:
        """
        Returns
        -------
        line: ModelLine
           existing line of the name passed in `key`
        """
        return self.lines[key]

    def __iter__(self):
        for line in self.lines:
            yield self.__getitem__(line)

    def __len__(self) -> int:
        """
        Returns
        -------
        num: int
            a number of lines
        """
        return len(self.lines)

    def __repr__(self) -> str:
        rp = f'ModelRepo in {self.root} of {len(self)} lines'
        return ', '.join([rp] + [repr(line) for line in self.lines])

    def _setup_logger(self):
        self.logger = logging.getLogger(self.root)
        hdlr = logging.FileHandler(os.path.join(self.root, 'history.log'))
        hdlr.setFormatter(logging.Formatter('\n%(asctime)s\n%(message)s'))
        self.logger.addHandler(hdlr)
        self.logger.setLevel('DEBUG')

    def _update_meta(self):
        # Reads meta if exists and updates it with new values
        # writes back to disk
        meta_path = os.path.join(self.root, 'meta' + self._meta_fmt)

        meta = {}
        if os.path.exists(meta_path):
            try:
                meta = self._mev.read(meta_path)[0]
            except IOError as e:
                warnings.warn(f'File reading error ignored: {e}')

        self.logger.info(DeepDiff(
            meta,
            self._mev.obj_to_dict(self.get_meta()[0])).pretty()
        )

        meta.update(self.get_meta()[0])
        try:
            self._mev.write(meta_path, [meta])
        except IOError as e:
            warnings.warn(f'File writing error ignored: {e}')

    def get_meta(self) -> List[Dict]:
        meta = super().get_meta()
        meta[0].update({
            'root': self.root,
            'len': len(self),
            'updated_at': pendulum.now(tz='UTC'),
            'type': 'repo'
        })
        return meta

    def __del__(self):
        # Release all files on destruction
        if hasattr(self, 'logger'):
            for handler in self.logger.handlers:
                handler.close()
                self.logger.removeHandler(handler)
    
    def __add__(self, repo):
        return ModelRepoConcatenator([self, repo])


class ModelRepoConcatenator(Repo):
    """
    The class to concatenate different Repos. 
    For the ease of use please, don't use it directly.
    Just do repo = repo_1 + repo_2 to unify repos.
    """
    def __init__(self, repos: Iterable[Repo], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._repos = repos

    def __getitem__(self, key):
        pair = key.split('_')
        if len(pair) <= 2:
            raise KeyError(f'Key {key} is not in required format \
            `<repo_idx>_..._<line_name>`. \
            Please, use the key in this format. For example `0_line_1`')
        idx, line_name = pair[0], '_'.join(pair[1:])
        idx = int(idx)

        return self._repos[idx][line_name]

    def __len__(self):
        return sum([len(repo) for repo in self._repos])

    def __iter__(self):
        # this flattens the list of lines
        for line in itertools.chain(*[[line for line in repo] for repo in self._repos]):
            yield line

    def __add__(self, repo):
        return ModelRepoConcatenator([self, repo])
