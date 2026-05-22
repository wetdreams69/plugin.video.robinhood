from core.http_client import HttpClient
import re
import base64
from urllib.parse import urlparse, parse_qs
import core.constants as const
_http = HttpClient()
def resolve(url):
    try:
        parsed_url = urlparse(url)
        get_val = parse_qs(parsed_url.query).get('get', [''])[0]
        if not get_val:
            return url
        get_val_clean = get_val.rstrip('=')
        headers = {
            'User-Agent': const.HEADERS['user-agent'],
            'Referer': f"{parsed_url.scheme}://{parsed_url.netloc}/"
        }
        resp = _http.get(url, headers=headers, timeout=10)
        html = resp.text if hasattr(resp, 'text') else resp
        pattern = r'(?:if\s*\(\s*getURL\s*==\s*["\']' + re.escape(get_val) + r'["\']\s*\)|\(\s*getURL\s*==\s*["\']' + re.escape(get_val_clean) + r'["\']\s*\))[^}]+keyId\s*=\s*["\']([^"\']+)["\'][^}]+key\s*=\s*["\']([^"\']+)["\']'
        match = re.search(pattern, html)
        key_id = ""
        key = ""
        if match:
            key_id = match.group(1)
            key = match.group(2)
        else:
            pattern2 = r'if\s*\(\s*getURL\s*==\s*["\']' + re.escape(get_val_clean) + r'["\']\s*\)[^{]*(?:{[^{}]*(?:{[^{}]*}[^{}]*)*})*keyId["\']?\s*:\s*["\']([^"\']+)["\'][^}]+key["\']?\s*:\s*["\']([^"\']+)["\']'
            match2 = re.search(pattern2, html)
            if match2:
                key_id = match2.group(1)
                key = match2.group(2)
        mpd_url = ""
        pad = len(get_val) % 4
        base64_val = get_val + ('=' * (4 - pad) if pad else '')
        nombre_decodificado = base64.b64decode(base64_val).decode('utf-8')
        if key_id and key:
            mpd_fallback = f"https://cdn.cvattv.com.ar/live/c3eds/{nombre_decodificado}/SA_Live_dash_enc_C/{nombre_decodificado}.mpd"
            mpd_url = mpd_fallback
            if nombre_decodificado == 'ESPN2_Arg':
                match_espn2 = re.search(r'var\s+espn2\s*=\s*["\']([^"\']+)["\']', html)
                if match_espn2:
                    mpd_url = match_espn2.group(1)
            return f"{mpd_url}|clearkey={key_id}:{key}"
    except Exception:
        pass
    return url
