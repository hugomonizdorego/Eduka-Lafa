"""Bounded HTTPS requests (Wikipedia, Wikimedia Commons, World Bank, Lafa content updates).

No AI provider is contacted. Redirects are refused so nothing is forwarded."""
import json
import urllib.request
import urllib.error
import urllib.parse
from . import __version__

USER_AGENT = f"Lafa/{__version__} (Edukasaun OS encyclopedia of Timor-Leste; +https://github.com/hugomonizdorego/Eduka-Lafa)"
LOOPBACK = {"127.0.0.1", "localhost", "::1"}

class NetworkError(RuntimeError): pass
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise NetworkError("Redirect refused. Check the official service endpoint.")

OPENER = urllib.request.build_opener(NoRedirect())

def allowed_url(url, loopback_http=False):
    """HTTPS everywhere; plain HTTP only for an open-source model on this computer."""
    parsed = urllib.parse.urlsplit(url)
    if not parsed.hostname or parsed.username or parsed.password: return False
    if parsed.scheme == "https": return True
    return loopback_http and parsed.scheme == "http" and parsed.hostname in LOOPBACK

def request(url, data=None, headers=None, timeout=45, limit=4_000_000, loopback_http=False):
    if not allowed_url(url, loopback_http):
        raise NetworkError("Only HTTPS service URLs are allowed (HTTP only for a local model on this computer).")
    hdr = {"User-Agent": USER_AGENT, **(headers or {})}
    if isinstance(data, dict):
        data = json.dumps(data).encode()
        hdr["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=hdr)
    try:
        with OPENER.open(req, timeout=timeout) as response:
            raw = response.read(limit + 1)
            if len(raw) > limit: raise NetworkError("Response exceeds LAFA's size limit.")
            return raw
    except urllib.error.HTTPError as error:
        # Do not echo remote bodies which can include user text or credentials.
        status = error.code
        messages = {401:"API key rejected.", 403:"Service access denied.", 404:"Endpoint or model not found.", 429:"Rate limit or API credits exhausted."}
        raise NetworkError(messages.get(status, f"Service returned HTTP {status}.")) from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise NetworkError("Connection failed or timed out. Check internet and try again.") from None

def json_request(url, data=None, headers=None, timeout=45, loopback_http=False):
    try: return json.loads(request(url, data, headers, timeout, loopback_http=loopback_http))
    except (ValueError, UnicodeError): raise NetworkError("Service returned an invalid JSON response.") from None

# Public hosts used only to show whether internet sources are reachable. Local
# features never wait for this check; each internet service also handles its
# own failure (one failing site never blocks another).
PROBE_HOSTS = ("https://www.wikipedia.org/", "https://raw.githubusercontent.com/", "https://timor-leste.gov.tl/")

def online_probe(hosts=PROBE_HOSTS, timeout=4):
    """True when at least one public host answers over HTTPS."""
    if isinstance(hosts, str): hosts = PROBE_HOSTS     # old callers passed a provider name
    for url in hosts:
        try:
            req = urllib.request.Request(url, method="HEAD", headers={"User-Agent":USER_AGENT})
            with urllib.request.urlopen(req, timeout=timeout) as response:
                final = urllib.parse.urlsplit(response.url)
                if final.scheme == "https" and 200 <= response.status < 500:
                    return True
        except urllib.error.HTTPError as error:
            # Any HTTP answer (even 403/404/405) proves the network works.
            if urllib.parse.urlsplit(error.url).scheme == "https" and error.code < 600:
                return True
        except Exception:
            continue
    return False
