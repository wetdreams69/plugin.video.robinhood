import time
import core.constants as const
from core.http_client import HttpClient
from core.cache import cache
from kodi.api import ListItem, add_directory_item, set_content, end_of_directory, log
from providers.streamx550.constants import AGENDA_URL, HEADERS, CACHE_KEY, CACHE_TTL

_http = HttpClient()

def _fetch_agenda():
    nocache = int(time.time() * 1000)
    url = f"{AGENDA_URL}?nocache={nocache}"
    resp = _http.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return resp.json()

def _parse_agenda(data):
    events = {}
    for item in data:
        title = item.get('title', 'Unknown').strip()
        time_str = item.get('time', '').strip()
        link = item.get('link', '')
        status = item.get('status', '')
        
        if not link:
            continue
            
        key = f"{time_str} - {title}"
        if key not in events:
            events[key] = {
                'title': title,
                'time': time_str,
                'status': status,
                'options': []
            }
            
        channel = link.split('channel=')[-1] if 'channel=' in link else 'Source'
        events[key]['options'].append({'name': channel, 'url': link})

    return list(events.values())

def _get_events():
    cached_data = cache.get(CACHE_KEY)
    if cached_data:
        return cached_data
        
    data = _fetch_agenda()
    events = _parse_agenda(data)
    
    if events:
        cache.set(CACHE_KEY, events, ttl=CACHE_TTL)
        
    return events

class StreamX550Provider:
    id = 'streamx550'
    label = 'StreamX550'
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
            for event in events:
                title = event['title']
                time_str = event['time']
                status = event['status']
                
                label = f"[{time_str}] {title}"
                if status:
                    if status.lower() == 'en vivo':
                        label = f"[COLOR green][{status}][/COLOR] {label}"
                    else:
                        label = f"[COLOR yellow][{status}][/COLOR] {label}"

                list_item = ListItem(label=label)
                list_item.getVideoInfoTag().setTitle(title)
                
                url = build_url({
                    'action': 'streamx550_options', 
                    'provider': self.id, 
                    'title': title, 
                    'time': time_str
                })
                add_directory_item(const.ADDON_HANDLE, url, list_item, isFolder=True)

        except Exception as e:
            log(f"[StreamX550] Error loading agenda: {e}")
            
        set_content(const.ADDON_HANDLE, 'videos')
        end_of_directory(const.ADDON_HANDLE)

    def list_options(self, target_title, target_time, build_url):
        try:
            events = _get_events()
            for event in events:
                if event['title'] == target_title and event['time'] == target_time:
                    for option in event['options']:
                        name = option['name']
                        url = option['url']
                        list_item = ListItem(label=f"[COLOR white]{name}[/COLOR]")
                        list_item.getVideoInfoTag().setTitle(f"{event['title']} - {name}")
                        list_item.set_property('IsPlayable', 'true')
                        play_url = build_url({'action': 'play', 'url': url})
                        add_directory_item(const.ADDON_HANDLE, play_url, list_item, isFolder=False)
                    break
                    
        except Exception as e:
            log(f"[StreamX550] Error loading options: {e}")
            
        end_of_directory(const.ADDON_HANDLE)

    def route(self, action, params, build_url):
        if action == 'streamx550_options':
            self.list_options(
                params.get('title', ''),
                params.get('time', ''),
                build_url
            )
        elif action == 'reload_provider':
            cache.clear(CACHE_KEY)
            import xbmc
            import xbmcgui
            xbmcgui.Dialog().notification(self.label, 'Provider recargado', xbmcgui.NOTIFICATION_INFO, 2000)
            xbmc.executebuiltin('Container.Refresh')
