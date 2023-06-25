from typing import Any
import json

from deepdiff import DeepDiff

from ...base import JSONEncoder
from ..meta_viewer import MetaViewer
from ..server import Server


class BaseDiffViewer(Server):
    def __init__(self, path) -> None:
        super().__init__()

        self._check_path(path)  # TODO: comment this
        self._path = path

        self._style = {"color": "#084c61", "font-family": "Open Sans, Montserrat"}

        self._json_theme = {
            "base00": "#fefefe",  # background
            "base03": "#cccccc",  # inactive key counter
            "base09": "#FF5F9E",  # numeric values
            "base0B": "#084c61",  # values text
            "base0D": "#C92C6D",  # keys text
        }

    def _check_path(self, path, meta_type):
        if not os.path.exists(path):
            raise FileNotFoundError(path)

    def _read_objects(self, path):
        raise NotImplementedError()

    def _layout(self):
        try:
            import dash
        except ModuleNotFoundError:
            self._raise_cannot_import_dash()
        else:
            from dash import dcc, html

        try:
            import dash_renderjson
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                "Cannot import dash_renderjson. It is optional dependency for DiffViewer"
                " and can be installed via `pip install dash_renderjson`"
            )
        else:
            from dash_renderjson import DashRenderjson

        self._objs = self._read_objects(self._path)

        return html.Div(
            [
                html.H1(
                    children=f"DiffViewer in {self._path}",
                    style={"textAlign": "center", **self._style},
                ),
                dcc.Dropdown(id="left-dropdown", options=list(self._objs.keys())),
                dcc.Dropdown(id="rigth-dropdown", options=list(self._objs.keys())),
                DashRenderjson(
                    id="diff-json",
                    data={"Nothing": "Nothing is selected!"},
                    theme=self._json_theme,
                    max_depth=self._default_diff_depth,
                ),
                html.Div(
                    id="display",
                    children=[
                        html.Details(
                            children=[
                                html.Summary(name),
                                DashRenderjson(
                                    id=f"data_{i}",
                                    data={"": self._objs[name]},
                                    theme=self._json_theme,
                                    max_depth=self._default_depth,
                                ),
                            ]
                        )
                        for i, name in enumerate(self._objs)
                    ],
                ),
            ],
            style={"margin": "5%", **self._style},
        )

    def serve(self, **kwargs: Any) -> None:
        """
        Runs dash server

        Parameters
        ----------
        **kwargs
            Arguments for run_server for example port
        """
        try:
            import dash
        except ModuleNotFoundError:
            self._raise_cannot_import_dash()

        app = dash.Dash()
        self._update_diff_callback(app)
        app.layout = self._layout
        app.run_server(use_reloader=False, **kwargs)

        mev = MetaViewer(path, filt={"type": "model"})
        objs = [meta for meta in mev]
        objs = {f"Model {i:0>5d}": meta for i, meta in enumerate(objs)}
        return objs

    def _update_diff_callback(self, _app) -> None:
        try:
            from dash import Input, Output
        except ModuleNotFoundError:
            self._raise_cannot_import_dash()

        @_app.callback(
            Output(component_id="diff-json", component_property="data"),
            Input(component_id="left-dropdown", component_property="value"),
            Input(component_id="rigth-dropdown", component_property="value"),
        )
        def _update_diff(x, y):
            if x is not None and y is not None:
                diff = DeepDiff(self._objs[x], self._objs[y]).to_dict()
                diff = JSONEncoder().encode(diff)
                diff = json.loads(diff)
                return diff
