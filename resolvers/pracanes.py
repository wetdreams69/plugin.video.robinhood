from core.http_client import HttpClient
import re
from urllib.parse import urlparse, parse_qs
from kodi.api import log

_http = HttpClient()

def resolve(url):
    try:
        p = urlparse(url)
        qs = parse_qs(p.query)
        target_id = qs.get('id', [None])[0] or qs.get('stream', [None])[0]
        if not target_id:
            return url
            
        resp = _http.get(url, timeout=10)
        html = resp.text if hasattr(resp, 'text') else resp
        
        # Grupo con nombre 'block' para evitar errores de indice
        pattern = r'["\']?' + re.escape(target_id) + r'["\']?\s*:\s*\{(?P<block>[^}]+)\}'
        match = re.search(pattern, html, re.DOTALL)
        if not match:
            log(f"[pracanes] ID {target_id} no encontrado en el HTML")
            return url
            
        block = match.group("block")
        
        # Buscamos la URL y las llaves de forma independiente y flexible
        url_parts = re.findall(r'["\']([^"\']+)["\']', block)
        if "mt_gigared" in block and len(url_parts) >= 2:
            res_url = url_parts[0] + "cdn03" + url_parts[1]
        elif url_parts:
            res_url = url_parts[0]
        else:
            return url
            
        k1_match = re.search(r'k1\s*:\s*["\']([^"\']+)["\']', block)
        k2_match = re.search(r'k2\s*:\s*["\']([^"\']+)["\']', block)
        
        if k1_match and k2_match:
            return f"{res_url}|clearkey={k1_match.group(1)}:{k2_match.group(1)}"
            
        return res_url
    except Exception as e:
        log(f"[pracanes] Error critico en {target_id}: {e}")
        return url
