import re
import core.constants as const
from core.http_client import HttpClient
from core.cache import cache
from kodi.api import ListItem, add_directory_item, set_content, end_of_directory, log
from providers.rojadirecta.constants import MAIN_URL, BASE_URL, HEADERS, CACHE_KEY, CACHE_TTL

_http = HttpClient()

def _fetch_html():
    resp = _http.get(MAIN_URL, headers=HEADERS, timeout=10, verify=False)
    return resp.text if hasattr(resp, 'text') else resp

def _parse_html(html):
    events = {}
    pattern = r'<tr><td>(.*?)<a href=[\'"]([^\'"]+)[\'"][^>]*><b>(.*?)</b></a>.*?<span class=[\'"]t[\'"]>([^<]+)</span>'
    matches = re.findall(pattern, html, re.IGNORECASE)
    
    for comp, link_url, title, time_str in matches:
        comp = comp.strip().strip(':')
        title = f"{comp}: {title.strip()}"
        time_str = time_str.strip()
        
        if link_url.startswith('/'):
            link_url = BASE_URL + link_url
            
        key = f"{time_str} - {title}"
        if key not in events:
            events[key] = {'title': title, 'time': time_str, 'options': []}
            
        channel_name = link_url.split('/')[-1].replace('.php', '').replace('.html', '').replace('-', ' ').title()
        if not channel_name:
            channel_name = 'Link'
            
        events[key]['options'].append({'name': channel_name, 'url': link_url})
        
    return list(events.values())

def _get_events():
    cached_data = cache.get(CACHE_KEY)
    if cached_data:
        return cached_data

    html = _fetch_html()
    events_list = _parse_html(html)
    
    if events_list:
        cache.set(CACHE_KEY, events_list, ttl=CACHE_TTL)
        
    return events_list

class RojaDirectaProvider:
    id = 'rojadirecta'
    label = 'Roja Directa TV'
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
                    'action': 'rojadirecta_options', 
                    'provider': self.id, 
                    'event_idx': idx
                })
                add_directory_item(const.ADDON_HANDLE, url, list_item, isFolder=True)
                
        except Exception as e:
            log(f"[RojaDirecta] Error loading events: {e}")
            
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
            log(f"[RojaDirecta] Error loading options: {e}")
            
        end_of_directory(const.ADDON_HANDLE)

    def route(self, action, params, build_url):
        if action == 'rojadirecta_options':
            self.list_options(params.get('event_idx', 0), build_url)
        elif action == 'reload_provider':
            cache.clear(CACHE_KEY)
            import xbmc
            import xbmcgui
            xbmcgui.Dialog().notification(self.label, 'Provider recargado', xbmcgui.NOTIFICATION_INFO, 2000)
            xbmc.executebuiltin('Container.Refresh')
