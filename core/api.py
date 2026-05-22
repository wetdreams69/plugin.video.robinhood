import re

import core.constants as const
from core.cache import cache
from core.http_client import HttpClient


_http = HttpClient()


@cache.cached(ttl=72000)
def get_json(url):
    try:
        resp = _http.get(url, headers=const.HEADERS, timeout=15)
        resp.raise_for_status()
        return resp.json() or {}
    except Exception:
        return {}


def update_urls():
    try:
        r = _http.get(const.URL_MAIN_PAGE, headers=const.HEADERS, timeout=10)
        if r.status_code == 200:
            m = re.search(r'src=["\'](scripts/main\.js(?:\?v=[^"\']+)?)["\']', r.text)
            js_path = m.group(1) if m else 'scripts/main.js'
            r2 = _http.get(f'{const.URL_MAIN_PAGE}/{js_path}', headers=const.HEADERS, timeout=10)
            if r2.status_code == 200:
                c = r2.text
                m_ch = re.search(r'channels:\s*[\'"](https?://[^\'"]+)[\'"]', c)
                if m_ch:
                    const.URL_CHANNELS = m_ch.group(1)
                m_lg = re.search(r'logos:\s*[\'"](https?://[^\'"]+)[\'"]', c)
                if m_lg:
                    const.URL_LOGOS = m_lg.group(1)
                m_fb = re.search(r'dataFallback:\s*[\'"](https?://[^\'"]+)[\'"]', c)
                if m_fb:
                    const.URL_FALLBACK = m_fb.group(1)
    except Exception:
        pass


def get_channels():
    update_urls()
    data = get_json(const.URL_CHANNELS)
    if not data or not data.get('channels'):
        data = get_json(const.URL_FALLBACK)
    return data.get('channels', [])


def get_logos():
    try:
        data = get_json(const.URL_LOGOS)
        return data.get('logos', {})
    except Exception:
        return {}
