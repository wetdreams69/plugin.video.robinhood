import re
import urllib.parse
from urllib.parse import urlparse
from core.http_client import HttpClient
class Hoca6Resolver:
    def __init__(self):
        self.http = HttpClient()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Referer': 'https://hoca6.com/',
            'Origin': 'https://hoca6.com'
        }
    def resolve(self, url):
        try:
            p = urlparse(url)
            origin = f"{p.scheme}://{p.netloc}"
            self.headers['Referer'] = origin + '/'
            self.headers['Origin'] = origin
            resp = self.http.get(url, headers=self.headers, timeout=8)
            html = resp.text if hasattr(resp, 'text') else resp
            from kodi.api import log
            log(f'[Hoca6] Resolved {url} - Status: {getattr(resp, "status_code", "unknown")} - Length: {len(html)}')
            pattern = r'\(\s*(\[[^\]]+\])\s*\.join\(["\']["\']'
            for match in re.finditer(pattern, html):
                array_str = match.group(1)
                chars = re.findall(r'["\']([^"\']*)["\']', array_str)
                cand = ''.join(chars).replace('\\/', '/')
                if cand.startswith('http') and '.m3u8' in cand:
                    return f"{cand}|Referer={urllib.parse.quote(origin + '/')}&Origin={urllib.parse.quote(origin)}"
        except Exception:
            pass
        return url
_DEFAULT = Hoca6Resolver()
def resolve(url):
    return _DEFAULT.resolve(url)