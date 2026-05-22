from core.http_client import HttpClient
import re
import base64
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
import core.constants as const
HAVE_REFERER = f"{const.URL_MAIN_PAGE}/"
class AngulismoResolver:
    def __init__(self):
        self.http = HttpClient()
        self.headers = {
            'User-Agent': const.HEADERS['user-agent'],
            'Referer': HAVE_REFERER
        }
    def fetch_html(self, url, timeout=8):
        resp = self.http.get(url, headers=self.headers, timeout=timeout)
        return resp.text if hasattr(resp, 'text') else resp
    def _resolve_gigared(self, stream_tpl, cdn_nodes):
        def build_from_node(node):
            try:
                candidate = re.sub(r'\$\{[^}]+\}', node, stream_tpl)
                if candidate.startswith('//'):
                    candidate = 'https:' + candidate
                return candidate
            except Exception:
                return None
        nodes = cdn_nodes or ['cdnlb']
        max_workers = min(6, len(nodes))
        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            future_to_node = {}
            for n in nodes:
                c = build_from_node(n)
                if not c:
                    continue
                future = ex.submit(lambda url_c=c: self.http.head(url_c, headers=self.headers, timeout=2))
                future_to_node[future] = n
            for fut in as_completed(future_to_node, timeout=5):
                node = future_to_node.get(fut)
                try:
                    resp = fut.result()
                    if resp is not None and getattr(resp, 'status_code', None) == 200:
                        return build_from_node(node)
                except Exception:
                    continue
        return build_from_node(nodes[0])
    def parse_patterns(self, html):
        match_v1 = re.search(r"url:\s*['\"]([^'\"]+)['\"][^{}]*keyId:\s*['\"]([^'\"]+)['\"][^{}]*key:\s*['\"]([^'\"]+)['\"]", html)
        match_v2 = re.search(r"nombreBase64:\s*['\"]([^'\"]+)['\"][^{}]*mt:\s*['\"]([^'\"]+)['\"][^{}]*number:\s*(\d+)[^{}]*keyId:\s*['\"]([^'\"]+)['\"][^{}]*key:\s*['\"]([^'\"]+)['\"]", html)
        match_v3 = re.search(r"const\s+(\w+)_CDN\s*=\s*\[(.*?)\].*?const\s+\1_STREAM\s*=\s*`([^`]+)`.*?const\s+\1_KEY_ID\s*=\s*['\"]([^'\"]+)['\"].*?const\s+\1_KEY\s*=\s*['\"]([^'\"]+)['\"]", html, re.DOTALL)
        match_v4 = re.search(r"const\s+STREAM_URL\s*=\s*['\"]([^'\"]+)['\"].*?const\s+KEY_ID\s*=\s*['\"]([^'\"]+)['\"].*?const\s+KEY\s*=\s*['\"]([^'\"]+)['\"]", html, re.DOTALL)
        if match_v1:
            return match_v1.group(1), match_v1.group(2), match_v1.group(3), HAVE_REFERER
        if match_v2:
            name_b64 = match_v2.group(1)
            mt = match_v2.group(2)
            number = match_v2.group(3)
            key_id = match_v2.group(4)
            key = match_v2.group(5)
            pad = len(name_b64) % 4
            if pad:
                name_b64 += '=' * (4 - pad)
            decoded_name = base64.b64decode(name_b64).decode('utf-8')
            mpd_url = f"https://{mt}.cvattv.com.ar/live/c{number}eds/{decoded_name}/SA_Live_dash_enc_C/{decoded_name}.mpd"
            return mpd_url, key_id, key, HAVE_REFERER
        if match_v3:
            cdn_nodes_str = match_v3.group(2)
            stream_tpl = match_v3.group(3)
            key_id = match_v3.group(4)
            key = match_v3.group(5)
            cdn_nodes = re.findall(r"['\"]([^'\"]+)['\"]", cdn_nodes_str)
            mpd_url = self._resolve_gigared(stream_tpl, cdn_nodes)
            return mpd_url, key_id, key, HAVE_REFERER
        if match_v4:
            return match_v4.group(1), match_v4.group(2), match_v4.group(3), HAVE_REFERER
        return None, None, None, HAVE_REFERER
    def resolve(self, url):
        from kodi.api import log
        try:
            html = self.fetch_html(url)
            mpd_url, key_id, key, referer = self.parse_patterns(html)
            if mpd_url and key_id and key:
                if 'stream-proxy' in mpd_url or 'workers.dev' in mpd_url:
                    clean_match = re.search(r"(https://(?:cdn|chromecast|cdnlb|cdn\d+)[\w.-]+/.+)", mpd_url)
                    if clean_match: mpd_url = clean_match.group(1)
                return f"{mpd_url}|Referer={referer}&clearkey={key_id}:{key}"
        except Exception as e:
            log(f'[Robinhood] Resolver error for {url}: {e}')
        return url
_DEFAULT_RESOLVER = AngulismoResolver()
def resolve(url):
    return _DEFAULT_RESOLVER.resolve(url)
