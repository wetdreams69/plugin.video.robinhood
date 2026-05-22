from core.http_client import HttpClient
import re
from urllib.parse import urlparse
_http = HttpClient()
def get_base_url(url):
    parsed_url = urlparse(url)
    return parsed_url.scheme + "://" + parsed_url.netloc
def resolve(url):
    headers = {
        'Referer': get_base_url(url),
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }
    try:
        resp = _http.get(url, headers=headers, timeout=10)
        if not hasattr(resp, 'status_code') or getattr(resp, 'status_code', 200) == 200:
            html = resp.text if hasattr(resp, 'text') else resp
            match = re.search(r'playbackURL\s*=\s*"([^\"]+)"', html)
            if match:
                stream_url = match.group(1)
                return stream_url + '|Referer=' + get_base_url(url)
    except Exception:
        pass
    return url
