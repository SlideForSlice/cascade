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
from typing import Literal, Any
from .meta_handler import MetaHandler


class HistoryLogger:
    def __init__(self, filepath: str,
                 meta_fmt: Literal['.json', '.yml', '.yaml'] = '.yml') -> None:
        self._mh = MetaHandler()
        self._log_file = filepath
        self._ext = meta_fmt

        if os.path.exists(self._log_file):
            try:
                self._log = self._mh.read(self._log_file )
                if isinstance(self._log, list):
                    raise RuntimeError(
                        f'Failed to initialize history logger due to unexpected object'
                        f' format - log is the instance of list and not dict. Check your {self._log_file} file')
                if 'history' not in self._log:
                    raise RuntimeError(f'Failed to initialize history logger due to unexpected object'
                                       f' format - "history" key is missing. Check your {self._log_file} file')
            except IOError as e:
                raise IOError(f'Failed to read log file: {self._log_file }') from e
        else:
            self._log = {
                'history': [],
                'type': 'history'
            }

    def log(self, obj: Any) -> None:
        self._log['history'].append(obj)

        try:
            self._mh.write(self._log_file, self._log)
        except IOError as e:
            raise IOError(f'Failed to write log file: {self._log_file}') from e
