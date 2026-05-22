from core.http_client import HttpClient
import re
from urllib.parse import urlparse
import urllib3

# Disable insecure warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_http = HttpClient()

def resolve(url):
    try:
        p = urlparse(url)
        origin = f"{p.scheme}://{p.netloc}/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': origin
        }
        
        # Ignoramos validación SSL para dominios problemáticos
        resp = _http.get(url, headers=headers, timeout=10, verify=False)
        if not hasattr(resp, 'text'):
            return url
            
        html = resp.text
        
        # 1. Buscar M3U8 directo
        m3u8_match = re.search(r'source\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']', html)
        if m3u8_match:
            stream_url = m3u8_match.group(1)
            if stream_url.startswith('//'):
                stream_url = 'https:' + stream_url
            return stream_url + f"|Referer={origin}"
            
        # 2. Buscar iframe genérico
        iframe_match = re.search(r'<iframe[^>]+src=["\']([^"\']+)["\']', html, re.IGNORECASE)
        if iframe_match:
            iframe_url = iframe_match.group(1)
            if not iframe_url.startswith('http'):
                if iframe_url.startswith('//'):
                    iframe_url = "https:" + iframe_url
                else:
                    iframe_url = origin.rstrip('/') + '/' + iframe_url.lstrip('/')
            return iframe_url + f"|Referer={url}"
            
    except Exception:
        pass
        
    return url
