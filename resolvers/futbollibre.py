from core.http_client import HttpClient
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from kodi.api import log
_http = HttpClient()
def get_base_url(url):
    parsed_url = urlparse(url)
    return parsed_url.scheme + "://" + parsed_url.netloc
def get_iframe_url(url, referer):
    headers = {
        'Referer': referer,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }
    try:
        resp = _http.get(url, headers=headers, timeout=8)
        html = resp.text if hasattr(resp, 'text') else resp
        soup = BeautifulSoup(html, 'html.parser')
        iframe = soup.find('iframe', {"class": "embed-responsive-item"})
        if iframe:
            return iframe.get("src")
        iframe_fallback = soup.find('iframe')
        if iframe_fallback:
            return iframe_fallback.get("src")
    except Exception as e:
        log(f'[futbollibre] Network error in iframe discovery: {str(e)}')
    return None
def resolve(url):
    base_url = get_base_url(url)
    iframe_url = get_iframe_url(url, base_url)
    if not iframe_url:
        return None
    if not iframe_url:
        return None
    headers = {
        'Referer': base_url,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }
    try:
        resp = _http.get(iframe_url, headers=headers, timeout=10)
        html = resp.text if hasattr(resp, 'text') else resp
        if 'Acceso Bloqueado' in html or 'Este contenido se est' in html:
            log(f'[futbollibre] Detected bloqueo overlay for {iframe_url}')
            parsed_iframe = urlparse(iframe_url)
            stream_candidates = []
            if 'stream.php' in parsed_iframe.path:
                stream_candidates.append(iframe_url)
            for m in re.finditer(r'https?://[^\'\"\s>]+(?:\.m3u8|stream\.php[^\'\"\s>]*)', html):
                stream_candidates.append(m.group(0))
            js_m = re.search(r'(https?://[^"\s]+\.m3u8[^"\s]*)', html)
            if js_m:
                stream_candidates.append(js_m.group(1))
            stream_candidates = list(dict.fromkeys(stream_candidates))
            iframe_referer = iframe_url
            iframe_origin = get_base_url(iframe_url)
            for cand in stream_candidates:
                try:
                    log(f'[futbollibre] probing candidate {cand} with Referer={iframe_referer}')
                    r2 = _http.get(cand, headers={'Referer': iframe_referer, 'Origin': iframe_origin}, timeout=8, allow_redirects=True)
                    status = getattr(r2, 'status_code', 200)
                    if status == 200:
                        text = getattr(r2, 'text', '')
                        if '.m3u8' in cand or '.m3u8' in text or 'EXTM3U' in text:
                            return cand + f'|Referer={iframe_referer}&Origin={iframe_origin}&User-Agent={_http.headers.get("User-Agent")}'
                        if hasattr(r2, 'url') and r2.url and r2.url.endswith('.m3u8'):
                            return r2.url + f'|Referer={iframe_referer}&Origin={iframe_origin}&User-Agent={_http.headers.get("User-Agent")}'
                except Exception:
                    continue
            return iframe_url + f'|Referer={base_url}&Origin={base_url}&User-Agent={_http.headers.get("User-Agent")}'
        iframe_origin = get_base_url(iframe_url)
        ua = _http.headers.get('User-Agent')
        for m in re.finditer(r'https?://[^\'"\s>]+(?:stream\.php[^\'"\s>]*)', html):
            cand = m.group(0)
            try:
                r2 = _http.get(cand, headers={'Referer': iframe_url, 'Origin': iframe_origin, 'User-Agent': ua}, timeout=6, allow_redirects=True)
                status = getattr(r2, 'status_code', 200)
                text = getattr(r2, 'text', '')
                if status == 200 and ('.m3u8' in cand or '.m3u8' in text or 'EXTM3U' in text):
                    return cand + f'|Referer={iframe_url}&Origin={iframe_origin}&User-Agent={ua}'
                if status == 200:
                    return cand + f'|Referer={iframe_url}&Origin={iframe_origin}&User-Agent={ua}'
            except Exception:
                continue
        # Try to find playbackURL or other patterns
        playback_match = re.search(r'playbackURL\s*=\s*["\']([^"\']+)["\']', html)
        if playback_match:
            return playback_match.group(1) + "|Referer=" + iframe_url
            
        pattern_setup = r'setupPlayer\s*\(\s*["\']([^"\']+)["\']\s*\)'
        setup_match = re.search(pattern_setup, html)
        if setup_match:
            return setup_match.group(1).strip() + "|Referer=" + iframe_url
            
        pattern = r'var\s+src\s*=\s*"([^\"]+)"'
        stream_url_match = re.search(pattern, html)
        if not stream_url_match:
            pattern2 = r'source\s*:\s*[\'\"]([^\'\"]+m3u8[^\'\"]*)[\'\"]'
            stream_url_match = re.search(pattern2, html)
        if stream_url_match:
            stream_url = stream_url_match.group(1).strip().replace("'", "").replace('"', '')
            return stream_url + '|Referer=' + get_base_url(iframe_url)
            
        # If we are already in stream.php and didn't find anything new, return None to stop loop
        if 'stream.php' in url:
            return None
            
        return iframe_url + "|Referer=" + url
    except Exception as e:
        log(f'[futbollibre] resolver error: {e}')
        return None
