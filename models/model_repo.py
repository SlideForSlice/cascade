import os
import datetime
import glob
from hashlib import md5

from .model import Model
from ..meta import MetaHandler


class ModelRepo:
    def __init__(self, folder, model_csl=Model, meta_prefix=None):
        self.meta_prefix = meta_prefix if meta_prefix is not None else {}

        self.root = folder
        self.model_cls = model_csl
        if os.path.exists(self.root):
            assert os.path.isdir(folder)
            self.lines = {name: ModelLine(os.path.join(self.root, name),
                                          model_csl=model_csl,
                                          meta_prefix=self.meta_prefix)
                          for name in os.listdir(self.root) if os.path.isdir(os.path.join(self.root, name))}
            print(f'Found {len(self.lines)}' + ' lines')
        else:
            os.mkdir(self.root)
            self.lines = dict()

    def _new_line(self, name=None):
        if name is None:
            name = f'{len(self.lines):05d}'
        else:
            name = str(name)

        folder = os.path.join(self.root, name)
        line = ModelLine(folder, self.model_cls, meta_prefix=self.meta_prefix)
        self.lines[name] = line
        return line

    def __getitem__(self, key):
        if key in self.lines:
            return self.lines[key]
        else:
            return self._new_line(key)

    def __len__(self):
        return len(self.lines)


class ModelLine:
    def __init__(self, folder, model_csl=Model, meta_prefix=None):
        self.meta_prefix = meta_prefix if meta_prefix is not None else {}

        self.model_csl = model_csl
        self.root = folder
        if os.path.exists(self.root):
            assert os.path.isdir(folder)
            self.models = {i: name for i, name in enumerate(os.listdir(self.root)) if not name.endswith('.json')}
            print(f'Found {len(self.models)}' + ' models')
        else:
            os.mkdir(self.root)
            self.models = {}

    def __getitem__(self, name) -> Model:
        model = self.model_csl()
        model.load(os.path.join(self.root, self.models[name]))
        return model

    def __len__(self):
        return len(self.models)

    def save(self, model: Model) -> None:
        idx = len(self.models)
        name = os.path.join(self.root, f'{idx:0>5d}')
        self.models[idx] = name
        model.save(name)

        exact_filename = glob.glob(f'{name}*')[0]
        with open(exact_filename, 'rb') as f:
            md5sum = md5(f.read()).hexdigest()

        meta = model.get_meta()

        meta.update(self.meta_prefix)
        meta['name'] = exact_filename
        meta['md5sum'] = md5sum
        meta['saved_at'] = datetime.datetime.now()

        mh = MetaHandler()
        mh.write(os.path.join(self.root, f'{idx:0>5d}.json'), meta)
