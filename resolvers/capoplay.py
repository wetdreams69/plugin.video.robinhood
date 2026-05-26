import re
import urllib.parse
from urllib.parse import urlparse
from core.http_client import HttpClient
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class CapoPlayResolver:
    def __init__(self):
        self.http = HttpClient()

    def resolve(self, url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': url
            }
            resp = self.http.get(url, headers=headers, timeout=8, verify=False)
            html = resp.text if hasattr(resp, 'text') else resp

            fid_match = re.search(r'fid\s*=\s*["\']([^"\']+)["\']', html)
            if fid_match:
                fid = fid_match.group(1)
                capo_url = f"https://capo8play.com/capo.php?player=desktop&live={fid}"
                resp2 = self.http.get(capo_url, headers=headers, timeout=8, verify=False)
                html2 = resp2.text if hasattr(resp2, 'text') else resp2
                pattern = r'\(\s*(\[[^\]]+\])\s*\.join\(["\']["\']'
                for match in re.finditer(pattern, html2):
                    array_str = match.group(1)
                    chars = re.findall(r'["\']([^"\']*)["\']', array_str)
                    cand = ''.join(chars).replace('\\/', '/')
                    if cand.startswith('http') and '.m3u8' in cand:
                        return f"{cand}|Referer={urllib.parse.quote('https://capo8play.com/')}&Origin=https://capo8play.com"

            iframe_match = re.search(r'<iframe[^>]+src=["\']([^"\']+)["\']', html, re.IGNORECASE)
            if iframe_match:
                iframe_src = iframe_match.group(1)
                if not iframe_src.startswith('http'):
                    p = urlparse(url)
                    base = f"{p.scheme}://{p.netloc}"
                    iframe_src = base + iframe_src if iframe_src.startswith('/') else base + '/' + iframe_src
                return iframe_src + f'|Referer={url}'
        except Exception:
            pass
        return url

_DEFAULT = CapoPlayResolver()

def resolve(url):
    return _DEFAULT.resolve(url)
