from typing import NoReturn, Any


class Server:
    def _raise_cannot_import_dash(self) -> NoReturn:
        raise ModuleNotFoundError('''
                    Cannot import dash. It is conditional
                    dependency you can install it
                    using the instructions from https://dash.plotly.com/installation''')

    def serve(self, **kwargs: Any) -> None:
        raise NotImplementedError()
