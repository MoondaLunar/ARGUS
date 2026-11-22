"""Bounded, opt-in public-document transport; no probing or biometric tools."""
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import ipaddress
import re
import socket
from urllib.parse import urlsplit, urlunsplit, urljoin, parse_qsl, urlencode
import requests

DEFAULT_HOSTS = frozenset({'fbi.gov', 'www.fbi.gov', 'vault.fbi.gov', 'justice.gov',
    'www.justice.gov', 'www.govinfo.gov', 'api.govinfo.gov', 'www.sec.gov',
    'efts.sec.gov', 'www.courtlistener.com', 'www.uscourts.gov', 'www.archives.gov'})
SECRET_KEYS = frozenset({'api_key', 'apikey', 'token', 'access_token', 'key', 'authorization'})


def canonical_url(url):
    if not isinstance(url, str) or not url or re.search(r'[\s\\\x00-\x1f\x7f]', url):
        raise ValueError('Malformed URL')
    p = urlsplit(url)
    if p.scheme.lower() not in ('http', 'https') or not p.hostname or p.username is not None or p.password is not None:
        raise ValueError('Only absolute HTTP(S) URLs without credentials are accepted')
    host = p.hostname.encode('idna').decode('ascii').lower().rstrip('.')
    if not host or '%' in host:
        raise ValueError('Invalid hostname')
    port = p.port
    if port not in (None, 80 if p.scheme.lower() == 'http' else 443):
        raise ValueError('Nonstandard public-record port')
    authority = '['+host+']' if ':' in host else host
    return urlunsplit((p.scheme.lower(), authority, p.path or '/', p.query, ''))


def public_url(url):
    """Credential-free canonical URL for persisted provenance."""
    p = urlsplit(canonical_url(url))
    query = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True) if k.casefold() not in SECRET_KEYS]
    return urlunsplit((p.scheme, p.netloc, p.path, urlencode(query), ''))


def validate_url(url, hosts=DEFAULT_HOSTS):
    clean = canonical_url(url)
    p = urlsplit(clean)
    if p.hostname not in hosts:
        raise ValueError('Host is not explicitly approved')
    if p.scheme != 'https':
        raise ValueError('Public retrieval requires HTTPS')
    segments = {x.casefold() for x in p.path.split('/')}
    if segments & {'login', 'signin', 'auth', 'payment', 'logout'}:
        raise ValueError('Authenticated/transactional path is outside public-record scope')
    return clean


def require_public_address(host):
    addresses = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    if not addresses or any(not ipaddress.ip_address(a[4][0]).is_global for a in addresses):
        raise ValueError('Destination does not resolve exclusively to public addresses')


@dataclass(frozen=True)
class DocumentResponse:
    body: bytes
    requested_url: str
    final_url: str
    mime_type: str
    retrieved_at: str
    sha256: str
    status: int = 200
    encoding: str = 'utf-8'


class PublicTransport:
    def __init__(self, *, allow_network=False, session=None, allowed_hosts=DEFAULT_HOSTS,
                 max_bytes=20_000_000, timeout=30, max_redirects=4, resolver=require_public_address,
                 credentials=None):
        self.allow_network = allow_network
        self.session = session or requests.Session()
        self.allowed_hosts = frozenset(allowed_hosts)
        self.max_bytes = max_bytes
        self.timeout = timeout
        self.max_redirects = max_redirects
        self.resolver = resolver
        self.credentials = credentials or {}
        self.errors = []

    def fetch(self, url):
        if not self.allow_network:
            raise RuntimeError('Network disabled: use fixtures or obtain approval before enabling live retrieval')
        original = public_url(url)
        current = validate_url(url, self.allowed_hosts)
        for hop in range(self.max_redirects + 1):
            self.resolver(urlsplit(current).hostname)
            # Credentials are selected anew for each validated host; never carried across redirects.
            headers = {'Accept': 'text/html,application/xhtml+xml,application/pdf,text/plain',
                       'User-Agent': 'ARGUS public-record research/1.0'}
            headers.update(self.credentials.get(urlsplit(current).hostname, {}))
            with self.session.get(current, headers=headers, timeout=self.timeout,
                                  stream=True, allow_redirects=False) as response:
                if response.status_code in (301, 302, 303, 307, 308):
                    if hop == self.max_redirects:
                        raise ValueError('Redirect limit exceeded')
                    current = validate_url(urljoin(current, response.headers.get('Location', '')), self.allowed_hosts)
                    continue
                if response.status_code != 200:
                    raise ValueError(f'HTTP status {response.status_code}')
                mime = response.headers.get('Content-Type', '').split(';')[0].strip().lower()
                if mime not in {'text/html', 'application/xhtml+xml', 'application/pdf', 'text/plain'}:
                    raise ValueError('Unsupported document MIME type')
                length = response.headers.get('Content-Length')
                if length and int(length) > self.max_bytes:
                    raise ValueError('Declared document size exceeds limit')
                body = bytearray()
                for chunk in response.iter_content(chunk_size=65536):
                    if len(body) + len(chunk) > self.max_bytes:
                        raise ValueError('Document size exceeds limit')
                    body.extend(chunk)
                return DocumentResponse(bytes(body), original, public_url(current), mime,
                    datetime.now(timezone.utc).isoformat(), hashlib.sha256(body).hexdigest(),
                    encoding=response.encoding or 'utf-8')
        raise ValueError('No document returned')
