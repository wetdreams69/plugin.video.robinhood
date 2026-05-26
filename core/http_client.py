import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import urllib.parse

class HttpClient:
    def __init__(self):
        self.session = requests.Session()
        retries = Retry(total=2, backoff_factor=0.25, status_forcelist=[429, 500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retries, pool_connections=10, pool_maxsize=20)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def _parse_url_headers(self, url):
        hdrs = {}
        if '|' in url:
            url, extra_str = url.split('|', 1)
            for part in extra_str.split('&'):
                if '=' in part:
                    k, v = part.split('=', 1)
                    hdrs[k] = urllib.parse.unquote(v)
        return url, hdrs

    def get(self, url, headers=None, timeout=8, allow_redirects=True, **kwargs):
        url, url_hdrs = self._parse_url_headers(url)
        hdrs = dict(self.headers)
        if headers:
            hdrs.update(headers)
        hdrs.update(url_hdrs)
        return self.session.get(url, headers=hdrs, timeout=timeout, allow_redirects=allow_redirects, **kwargs)

    def head(self, url, headers=None, timeout=2, allow_redirects=True, **kwargs):
        url, url_hdrs = self._parse_url_headers(url)
        hdrs = dict(self.headers)
        if headers:
            hdrs.update(headers)
        hdrs.update(url_hdrs)
        return self.session.head(url, headers=hdrs, timeout=timeout, allow_redirects=allow_redirects, **kwargs)

