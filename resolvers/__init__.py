from kodi.api import log
from core.cache import cache
from .bolaloca import resolve as resolve_bolaloca
from .futbollibre import resolve as resolve_futbollibre
from .hoca6 import resolve as resolve_hoca6
from .nebunexa import resolve as resolve_nebunexa
from .streamtp import resolve as resolve_streamtp
from .pracanes import resolve as resolve_pracanes
from .angulismo import resolve as resolve_angulismo
from .elcanaldeportivo import resolve as resolve_elcanaldeportivo
from .la14hd import resolve as resolve_la14hd
from .generic_extract import resolve as resolve_generic
from .proveseat import resolve as resolve_proveseat
from .capoplay import resolve as resolve_capoplay

RESOLVER_REGISTRY = [
    (lambda u: "angulismo" in u or "cvattv" in u or "gigared" in u, resolve_angulismo),
    (lambda u: "bolaloca" in u, resolve_bolaloca),
    (lambda u: "la14hd" in u, resolve_la14hd),
    (lambda u: "elcanaldeportivo" in u, resolve_elcanaldeportivo),
    (lambda u: "tucanaldeportivo" in u or "canales.php" in u or "ksdjugfsddeports" in u, resolve_futbollibre),
    (lambda u: "hoca6" in u or "hoca8" in u or "cdn" in u, resolve_hoca6),
    (lambda u: "nebunexa" in u or "bestleague.world" in u, resolve_nebunexa),
    (lambda u: "capoplay.net" in u or "capo8play" in u, resolve_capoplay),
    (lambda u: "streamtp" in u or "streamx" in u or "domainmy" in u or "domainplayer" in u or "streamvv" in u or "streamzs" in u, resolve_streamtp),
    (lambda u: "proveseat" in u or "18zone" in u, resolve_proveseat),
    (lambda u: "github.io" in u, resolve_pracanes),
    (lambda u: "welivesports" in u or "streamfree" in u or "embedsports" in u or "deporte-libre" in u or "tarjetarojatv" in u or "rojadirecta.re" in u, resolve_generic),
]

def resolve_url(url, max_hops=3):
    original_url = url
    for _ in range(max_hops):
        url = _strip_proxies(url)
        base_url = url.split('|')[0]
        if ".m3u8" in base_url or ".mpd" in base_url:
            break
        cached = cache.get(f'resolve:{base_url}')
        if cached:
            log(f'[Robinhood] Using cached resolution: {base_url}')
            return cached

        inherited_headers = url[len(base_url):] if '|' in url else ''

        resolved = base_url
        for matcher, resolver_func in RESOLVER_REGISTRY:
            if matcher(base_url):
                try:
                    resolved = resolver_func(url)
                except Exception as e:
                    log(f'[Robinhood] Resolver error ({resolver_func.__name__}): {str(e)}')
                    resolved = None
                break
        else:
            break

        if not resolved or resolved == base_url:
            if inherited_headers:
                url = base_url + inherited_headers
            break

        if '|' in resolved and resolved.split('|')[0] == base_url:
            url = resolved
            break

        log(f'[Robinhood] Hop {_+1}: {resolved}')
        url = resolved

    cache.set(f'resolve:{original_url}', url, ttl=300)
    return url

def _strip_proxies(url):
    if "proxy" in url.lower() or url.count("http") > 1:
        headers_sep = url.find('|')
        second_http = url.find("http", 8)
        if second_http != -1 and (headers_sep == -1 or second_http < headers_sep):
            prefix = url[:second_http]
            if prefix.endswith('/') or prefix.endswith('='):
                new_url = url[second_http:]
                log(f'[Robinhood] Proxy stripped: {new_url}')
                return new_url
    return url