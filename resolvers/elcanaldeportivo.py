from core.http_client import HttpClient
import re
import base64
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
_http = HttpClient()
def get_base_url(url):
    parsed_url = urlparse(url)
    return parsed_url.scheme + "://" + parsed_url.netloc
def resolve(url_base):
    base_ref = get_base_url(url_base)
    headers = {
        'Referer': base_ref,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }
    try:
        resp = _http.get(url_base, headers=headers, timeout=10)
        html = resp.text if hasattr(resp, 'text') else resp
        soup = BeautifulSoup(html, "html.parser")
        iframe = soup.find('iframe')
        if iframe and iframe.get("src"):
            url = iframe.get("src")
            resp = _http.get(url, headers=headers, timeout=10)
            html2 = resp.text if hasattr(resp, 'text') else resp
            soup = BeautifulSoup(html2, "html.parser")
        else:
            url = None
        iframe2 = soup.find('iframe')
        if iframe2 and iframe2.get("src"):
            url2 = iframe2.get("src")
            parsed_url = urlparse(url2)
            url_parameters = parse_qs(parsed_url.query)
            if "url" in url_parameters and 'http' not in url_parameters["url"][0]:
                return base64.b64decode(url_parameters["url"][0]).decode('utf-8')
            elif "get" in url_parameters and 'http' in url_parameters["get"][0]:
                return url_parameters["get"][0]
        else:
            script_fid = soup.find('script', text=lambda text: text and 'fid' in text)
            if script_fid:
                fid = script_fid.text.split('"')[1]
                script_tag = None
                for s in soup.find_all('script', src=True):
                    src = s.get('src') or ''
                    if src.startswith('//') and ('deep' in src.lower() or 'deport' in src.lower() or 'player' in src.lower()):
                        script_tag = s
                        break
                if not script_tag:
                    for s in soup.find_all('script', src=True):
                        src = s.get('src') or ''
                        if src.startswith('//'):
                            script_tag = s
                            break
                if script_tag:
                    url2 = "https:" + script_tag["src"].replace(".js", '.php') + '?player=desktop&live=' + fid
                    resp2 = _http.get(url2, headers=headers, timeout=10)
                    text2 = resp2.text if hasattr(resp2, 'text') else resp2
                    pattern = re.compile(r'return\(\[(.*?)\]\)', re.DOTALL)
                    match = pattern.search(text2)
                    if match:
                        raw = match.group(1)
                        try:
                            parts = [p.strip().strip("\"' ") for p in raw.split(',') if p.strip()]
                            url_video = ''.join(parts)
                            url_video = url_video.replace('\\/', '/')
                            if 'http' in url_video and ('.m3u8' in url_video or '.mpd' in url_video):
                                return url_video + "|Referer=" + url2
                        except Exception:
                            pass
                    func_arr = re.search(r'return\(\[([^\]]+)\]\.join\(""\)', text2, re.DOTALL)
                    if func_arr:
                        try:
                            arr = func_arr.group(1)
                            parts = [p.strip().strip("\"' ") for p in arr.split(',') if p.strip()]
                            url_video = ''.join(parts)
                            url_video = url_video.replace('\\/', '/')
                            if 'http' in url_video and ('.m3u8' in url_video or '.mpd' in url_video):
                                return url_video + "|Referer=" + url2
                        except Exception:
                            pass
                    for s in soup.find_all('script', src=True):
                        try:
                            src = s.get('src') or ''
                            if not src.startswith('//') and not src.startswith('http'):
                                continue
                            candidate = src if src.startswith('http') else ('https:' + src)
                            candidate_php = candidate.replace('.js', '.php')
                            candidate_url = candidate_php + '?player=desktop&live=' + fid
                            resp3 = _http.get(candidate_url, headers=headers, timeout=8)
                            t3 = resp3.text if hasattr(resp3, 'text') else resp3
                            m2 = re.search(r'return\(\[(.*?)\]\)', t3, re.DOTALL)
                            if m2:
                                raw2 = m2.group(1)
                                parts2 = [p.strip().strip('"\'') for p in raw2.split(',') if p.strip()]
                                url_video2 = ''.join(parts2)
                                url_video2 = url_video2.replace('\\/', '/')
                                if 'http' in url_video2 and ('.m3u8' in url_video2 or '.mpd' in url_video2):
                                    return url_video2 + "|Referer=" + candidate_url
                        except Exception:
                            continue
    except Exception:
        pass
    return url_base
