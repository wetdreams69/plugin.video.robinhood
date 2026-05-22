import re
import urllib.parse
import base64
import core.constants as const
from core.http_client import HttpClient
from core.cache import cache
from kodi.api import ListItem, add_directory_item, set_content, end_of_directory, log
from providers.tarjetaroja.constants import MAIN_URL, BASE_URL, HEADERS, CACHE_KEY, CACHE_TTL

_http = HttpClient()

def _fetch_html():
    resp = _http.get(MAIN_URL, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return resp.text

def _parse_html(html):
    events = []
    matches = re.findall(r'<li class="[^"]*"><a href="#">(.*?)(?:<span class="t">([^<]+)</span>)?</a>\s*<ul>(.*?)</ul></li>', html, re.DOTALL)
    for title, time_str, ul_content in matches:
        title = title.strip()
        time_str = time_str.strip() if time_str else ''
        
        options = []
        option_matches = re.findall(r'<a href="([^"]+)">([^<]+)</a>', ul_content)
        for opt_url, opt_name in option_matches:
            if opt_url.startswith('/'):
                opt_url = BASE_URL + opt_url
                
            if '/deportes/eventos.php?r=' in opt_url:
                try:
                    encoded = opt_url.split('?r=')[1].split('&')[0]
                    opt_url = base64.b64decode(encoded).decode('utf-8')
                except Exception:
                    pass
                    
            options.append({'name': opt_name.strip(), 'url': opt_url})
            
        events.append({'title': title, 'time': time_str, 'options': options})
    return events

def _get_events():
    cached_data = cache.get(CACHE_KEY)
    if cached_data:
        return cached_data

    html = _fetch_html()
    events = _parse_html(html)
    
    if events:
        cache.set(CACHE_KEY, events, ttl=CACHE_TTL)
        
    return events

class TarjetaRojaProvider:
    id = 'tarjetaroja'
    label = 'Tarjeta Roja'
    icon = const.ADDON_PATH + '/icon.png'

    def list_sources(self, build_url):
        try:
            reload_item = ListItem(label="[COLOR blue]Recargar Provider[/COLOR]")
            reload_url = build_url({
                'action': 'reload_provider',
                'provider': self.id
            })
            add_directory_item(const.ADDON_HANDLE, reload_url, reload_item, isFolder=False)

            events = _get_events()
            for idx, event in enumerate(events):
                title = event['title']
                time_str = event['time']
                
                label = f"[{time_str}] {title}" if time_str else title
                list_item = ListItem(label=label)
                list_item.getVideoInfoTag().setTitle(title)
                
                url = build_url({
                    'action': 'tarjetaroja_options', 
                    'provider': self.id, 
                    'event_idx': idx
                })
                add_directory_item(const.ADDON_HANDLE, url, list_item, isFolder=True)
                
        except Exception as e:
            log(f"[TarjetaRoja] Error loading events: {e}")
            
        set_content(const.ADDON_HANDLE, 'videos')
        end_of_directory(const.ADDON_HANDLE)

    def list_options(self, event_idx, build_url):
        try:
            events = _get_events()
            idx = int(event_idx)
            if idx < len(events):
                event = events[idx]
                for option in event['options']:
                    name = option['name']
                    url = option['url']
                    
                    list_item = ListItem(label=f"[COLOR white]{name}[/COLOR]")
                    list_item.getVideoInfoTag().setTitle(f"{event['title']} - {name}")
                    list_item.set_property('IsPlayable', 'true')
                    
                    play_url = build_url({'action': 'play', 'url': url})
                    add_directory_item(const.ADDON_HANDLE, play_url, list_item, isFolder=False)
        except Exception as e:
            log(f"[TarjetaRoja] Error loading options: {e}")
            
        end_of_directory(const.ADDON_HANDLE)

    def route(self, action, params, build_url):
        if action == 'tarjetaroja_options':
            self.list_options(params.get('event_idx', 0), build_url)
        elif action == 'reload_provider':
            cache.clear(CACHE_KEY)
            import xbmc
            import xbmcgui
            xbmcgui.Dialog().notification(self.label, 'Provider recargado', xbmcgui.NOTIFICATION_INFO, 2000)
            xbmc.executebuiltin('Container.Refresh')
