from core.http_client import HttpClient
import re
class BolalocaResolver:
    def __init__(self):
        self.http = HttpClient()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Upgrade-Insecure-Requests': '1'
        }
    def resolve(self, url):
        try:
            resp = self.http.get(url, headers=self.headers, timeout=8)
            html = resp.text if hasattr(resp, 'text') else resp
            m = re.search(r'<iframe[^>]+src=["\']([^"\']+)["\']', html, re.IGNORECASE)
            if m: return m.group(1)
        except Exception:
            pass
        return url
_DEFAULT = BolalocaResolver()
def resolve(url):
    return _DEFAULT.resolve(url)
