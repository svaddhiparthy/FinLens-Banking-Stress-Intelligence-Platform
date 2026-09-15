import json

from streamlit_app.lib import public_identity as identity_module


class _Response:
    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


def test_loads_central_portfolio_identity(monkeypatch) -> None:
    payload = {
        "identity": {
            "display_name": "Sri Vaddhiparthy",
            "portfolio_url": "https://srivaddhiparthy.com/",
            "github_url": "https://github.com/svaddhiparthy/",
        }
    }
    monkeypatch.setattr(identity_module, "urlopen", lambda *_args, **_kwargs: _Response(payload))

    identity = identity_module._load_public_identity("http://portfolio/data/site-content.json")

    assert identity.display_name == "Sri Vaddhiparthy"
    assert identity.portfolio_url == "https://srivaddhiparthy.com/"
    assert identity.github_url == "https://github.com/svaddhiparthy/"
