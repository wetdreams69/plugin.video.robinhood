import re
import math
import json
import base64
import urllib.parse
from urllib.parse import urlparse
from core.http_client import HttpClient
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ProveSeatResolver:
    def __init__(self):
        self.http = HttpClient()

    def resolve(self, url):
        try:
            base_url = url.split('|')[0]
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': base_url
            }
            resp = self.http.get(url, headers=headers, timeout=8, verify=False)
            html = resp.text if hasattr(resp, 'text') else resp

            m = re.search(r"window\._econfig='([^']+)'", html)
            if m:
                econfig = m.group(1)
                decoded_str = base64.b64decode(econfig).decode('latin1')
                part_len = math.ceil(len(decoded_str) / 4.0)
                parts = [decoded_str[i*part_len : (i+1)*part_len] for i in range(4)]
                indices = [2, 0, 3, 1]
                db9ee2 = [None] * 4

                for i, part in enumerate(parts):
                    modified_part = part[0:3] + part[4:]
                    db9ee2[indices[i]] = base64.b64decode(modified_part).decode('latin1')

                final_str = base64.b64decode(''.join(db9ee2)).decode('utf-8')
                config = json.loads(final_str)
                stream_url = config.get('stream_url_nop2p') or config.get('stream_url')
                if stream_url:
                    p = urlparse(base_url)
                    origin = f"{p.scheme}://{p.netloc}"
                    return f"{stream_url}|Referer={urllib.parse.quote(origin)}/&Origin={origin}"

            iframe_match = re.search(r'<iframe[^>]+src=["\']([^"\']+)["\']', html, re.IGNORECASE)
            if iframe_match:
                iframe_src = iframe_match.group(1)
                if not iframe_src.startswith('http'):
                    p = urlparse(base_url)
                    base = f"{p.scheme}://{p.netloc}"
                    iframe_src = base + iframe_src if iframe_src.startswith('/') else base + '/' + iframe_src
                return iframe_src + f'|Referer={base_url}'
        except Exception:
            pass
        return url

_DEFAULT = ProveSeatResolver()

def resolve(url):
    return _DEFAULT.resolve(url)
