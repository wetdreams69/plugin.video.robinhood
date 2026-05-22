from core.http_client import HttpClient
import re
import base64
from urllib.parse import urlparse
_http = HttpClient()
def resolve(url):
    try:
        url = re.sub(r'streamtpcloud\.com', 'streamtpnew.com', url)
        
        p = urlparse(url)
        origin = f"{p.scheme}://{p.netloc}/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': origin
        }
        resp = _http.get(url, headers=headers, timeout=10)
        html = resp.text if hasattr(resp, 'text') else resp
        arr_match = re.search(
            r'(\w+)\s*=\s*(\[\s*\[\s*\d+\s*,\s*"[A-Za-z0-9+/=]+"\s*\](?:\s*,\s*\[\s*\d+\s*,\s*"[A-Za-z0-9+/=]+"\s*\])*\s*\])',
            html
        )
        if not arr_match:
            m3u8_match = re.search(r'source\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']', html)
            if m3u8_match:
                return m3u8_match.group(1) + "|Referer=" + url
            return url
        arr_str = arr_match.group(2)
        pairs = re.findall(r'\[\s*(\d+)\s*,\s*"([A-Za-z0-9+/=]+)"\s*\]', arr_str)
        if not pairs:
            return url
        fn_returns = re.findall(r'function\s+\w+\s*\(\)\s*\{\s*return\s+(\d+)\s*;\s*\}', html)
        if not fn_returns:
            return url
        k = sum(int(v) for v in fn_returns)
        pairs_sorted = sorted(pairs, key=lambda x: int(x[0]))
        playback_url = ""
        for index_str, v_b64 in pairs_sorted:
            try:
                pad = len(v_b64) % 4
                if pad:
                    v_b64 += "=" * (4 - pad)
                v_decoded = base64.b64decode(v_b64).decode('utf-8', errors='ignore')
                numeric_val = int(re.sub(r'\D', '', v_decoded))
                char_code = numeric_val - k
                playback_url += chr(char_code)
            except Exception:
                pass
        if playback_url and playback_url.startswith("http"):
            return playback_url + "|Referer=" + url
    except Exception:
        pass
    return url
