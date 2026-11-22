"""Preserve legacy parsing/analysis APIs without permitting legacy network I/O."""
import requests

class OfflineSession(requests.Session):
    def request(self, *args, **kwargs):
        raise RuntimeError('Legacy network execution is disabled; use the bounded PublicTransport pipeline')
