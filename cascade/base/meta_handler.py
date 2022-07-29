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
import json
from typing import Union, Dict, List
import datetime
from typing import List, Dict
from json import JSONEncoder

import yaml
import numpy as np


class CustomEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, type):
            return str(obj)
        if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
            return obj.isoformat()

        elif isinstance(obj, datetime.timedelta):
            return (datetime.datetime.min + obj).time().isoformat()

        elif isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
                              np.int16, np.int32, np.int64, np.uint8,
                              np.uint16, np.uint32, np.uint64)):
            return int(obj)

        elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
            return float(obj)

        elif isinstance(obj, (np.complex_, np.complex64, np.complex128)):
            return {'real': obj.real, 'imag': obj.imag}

        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()

        elif isinstance(obj, np.bool_):
            return bool(obj)

        elif isinstance(obj, np.void):
            return None

        return super(CustomEncoder, self).default(obj)

    def obj_to_dict(self, obj):
        return json.loads(self.encode(obj))


class BaseHandler:
    def read(self, path) -> List[Dict]:
        raise NotImplementedError()

    def write(self, path, obj, overwrite=True) -> None:
        raise NotImplementedError()


class JSONHandler(BaseHandler):
    """
    Handles the logic of dumping and loading json files
    """
    def read(self, path) -> Union[Dict, List[Dict]]:
        """
        Reads json from path

        Parameters
        ----------
        path:
            Path to the file. If no extension provided, then .json will be added
        """
        _, ext = os.path.splitext(path)
        if ext == '':
            path += '.json'

        with open(path, 'r') as meta_file:
            meta = json.load(meta_file)
            if isinstance(meta, str):
                meta = json.loads(meta)
            return meta

    def write(self, name, obj:List[Dict], overwrite=True) -> None:
        """
        Writes json to path using custom encoder
        """
        if not overwrite and os.path.exists(name):
            return

        with open(name, 'w') as f:
            json.dump(obj, f, cls=CustomEncoder, indent=4)


class YAMLHandler(BaseHandler):
    def read(self, path) -> Union[Dict, List[Dict]]:
        """
        Reads yaml from path

        Parameters
        ----------
        path:
            Path to the file. If no extension provided, then .yml will be added
        """
        _, ext = os.path.splitext(path)
        if ext == '':
            path += '.yml'

        with open(path, 'r') as meta_file:
            meta = yaml.safe_load(meta_file)
            return meta

    def write(self, path, obj, overwrite=True) -> None:
        if not overwrite and os.path.exists(path):
            return

        obj = CustomEncoder().obj_to_dict(obj)
        with open(path, 'w') as f:
            yaml.safe_dump(obj, f)


class TextHandler(BaseHandler):
    def read(self, path) -> Dict:
        """
        Reads text file from path and returns dict in the form {path: 'text from file'}

        Parameters
        ----------
        path:
            Path to the file
        """

        with open(path, 'r') as meta_file:
            meta = {path: ''.join(meta_file.readlines())}
            return meta

    def write(self, path, obj, overwrite=True) -> None:
        raise NotImplementedError('MetaHandler does not write text files, only reads')       


class MetaHandler:
    def read(self, path) -> List[Dict]:
        handler = self._get_handler(path)
        return handler.read(path)

    def write(self, path, obj, overwrite=True) -> None:
        handler = self._get_handler(path)
        return handler.write(path, obj, overwrite=overwrite)

    def _get_handler(self, path) -> BaseHandler:
        ext = os.path.splitext(path)[-1]
        if ext == '.json':
            return JSONHandler()
        elif ext == '.yml':
            return YAMLHandler()
        else:
            return TextHandler()
