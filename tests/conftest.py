import pytest


@pytest.fixture
def connect_signal():
    """Connecte un receiver à un signal et le déconnecte automatiquement."""
    connections = []

    def _connect(signal, receiver, **kwargs):
        signal.connect(receiver, **kwargs)
        connections.append((signal, receiver, kwargs.get("dispatch_uid")))
        return receiver

    yield _connect

    for signal, receiver, dispatch_uid in connections:
        signal.disconnect(receiver, dispatch_uid=dispatch_uid)
