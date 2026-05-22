import xbmc
import core.constants as const
from core.cache import cache
from kodi.api import log, get_info_label, set_resolved_url, ListItem


class PlaybackTracker:
    def __init__(self, url):
        self.url = url

    def record_attempt(self):
        stats = self._get_stats()
        stats['t'] += 1
        cache.set(f'stats:{self.url}', stats, ttl=None)

    def monitor(self):
        monitor = xbmc.Monitor()
        player = xbmc.Player()
        for _ in range(30):
            if monitor.waitForAbort(0.5):
                break
            if player.isPlayingVideo():
                stats = self._get_stats()
                stats['s'] += 1
                cache.set(f'stats:{self.url}', stats, ttl=None)
                log(f'[Robinhood] Playback success: {self.url}')
                break
                
    def _get_stats(self):
        return cache.get(f'stats:{self.url}') or {'s': 0, 't': 0}


def setup_item(real_url, extra_headers=None, clearkey=None):
    if clearkey:
        log(f'[Robinhood] Playing (DRM): {real_url}')
        list_item = ListItem(path=real_url)
        _configure_drm(list_item, real_url, extra_headers, clearkey)
    else:
        full_url = f'{real_url}|{extra_headers}' if extra_headers else real_url
        log(f'[Robinhood] Playing: {full_url}')
        list_item = ListItem(path=full_url)
        list_item.set_mime_type('application/x-mpegURL')
        list_item.set_content_lookup(False)
        
    set_resolved_url(const.ADDON_HANDLE, True, listitem=list_item)


def _configure_drm(list_item, url, extra_headers, clearkey):
    list_item.set_property('inputstream', 'inputstream.adaptive')
    list_item.set_property('inputstream.adaptive.manifest_type', 'mpd')
    
    if extra_headers:
        list_item.set_property('inputstream.adaptive.manifest_headers', extra_headers)
        
    maj_version = _get_kodi_major_version()
    
    if maj_version >= 21:
        list_item.set_property('inputstream.adaptive.drm_legacy', f'org.w3.clearkey|{clearkey}')
    else:
        list_item.set_property('inputstream.adaptive.license_type', 'clearkey')
        if ':' in clearkey:
            kid, key = clearkey.split(':', 1)
            clearkey = f'{{"{kid}":"{key}"}}'
        list_item.set_property('inputstream.adaptive.license_key', clearkey)


def _get_kodi_major_version():
    ver = get_info_label("System.BuildVersion")
    try:
        return int(ver.split(".")[0])
    except Exception:
        return 19
