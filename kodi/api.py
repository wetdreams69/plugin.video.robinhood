import os
import errno
try:
    import xbmc
    import xbmcgui
    import xbmcplugin
    import xbmcaddon
    import xbmcvfs
except Exception:
    xbmc = None
    xbmcgui = None
    xbmcplugin = None
    xbmcaddon = None
    xbmcvfs = None
PLUGIN_ID = 'plugin.video.robinhood'
class _FallbackAddon:
    def __init__(self):
        self._info = {
            'id': PLUGIN_ID,
            'profile': os.path.join('/tmp', PLUGIN_ID)
        }
    def getAddonInfo(self, key):
        return self._info.get(key, '')
def get_addon():
    if xbmcaddon:
        return xbmcaddon.Addon()
    return _FallbackAddon()
def translate_path(path):
    try:
        if xbmcvfs:
            return xbmcvfs.translatePath(path)
        if xbmc:
            return xbmc.translatePath(path)
    except Exception:
        pass
    if path.endswith('profile'):
        p = os.path.join('/tmp', 'plugin.video.robinhood')
        try:
            os.makedirs(p, exist_ok=True)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        return p
    return path
def log(msg, level=None):
    try:
        if xbmc:
            xbmc.log(msg, level if level is not None else xbmc.LOGINFO)
            return
    except Exception:
        pass
    print(f"[kodi.log] {msg}")
class ListItem:
    def __init__(self, label=None, path=None):
        if xbmcgui:
            if path is not None:
                self._item = xbmcgui.ListItem(path=path)
            else:
                self._item = xbmcgui.ListItem(label=label)
        else:
            self._item = {'label': label, 'path': path, 'art': {}, 'info': {}, 'props': {}}
    def set_mime_type(self, mime_type):
        if xbmcgui:
            self._item.setMimeType(mime_type)
        else:
            self._item['mime_type'] = mime_type
    def set_content_lookup(self, enable):
        if xbmcgui:
            self._item.setContentLookup(enable)
        else:
            self._item['content_lookup'] = enable
    def set_art(self, art):
        if xbmcgui:
            self._item.setArt(art)
        else:
            self._item['art'] = art
    def set_info(self, media_type, info):
        if xbmcgui:
            self._item.setInfo(media_type, info)
        else:
            self._item['info'] = info
    def set_property(self, key, value):
        if xbmcgui:
            self._item.setProperty(key, value)
        else:
            self._item['props'][key] = value
    def getVideoInfoTag(self):
        if xbmcgui:
            return self._item.getVideoInfoTag()
        return self

    def setTitle(self, title):
        if not xbmcgui:
            self._item['info']['title'] = title

    @property
    def native(self):
        return self._item
def add_directory_item(handle, url, list_item, isFolder=True):
    try:
        if xbmcplugin:
            xbmcplugin.addDirectoryItem(handle, url, list_item._item if hasattr(list_item, '_item') else list_item.native, isFolder=isFolder)
            return
    except Exception:
        pass
    print(f"ADD DIR [{handle}] {url} folder={isFolder} label={getattr(list_item, '_item', list_item).get('label','')}")
def set_content(handle, content_type):
    try:
        if xbmcplugin:
            xbmcplugin.setContent(handle, content_type)
            return
    except Exception:
        pass
def end_of_directory(handle):
    try:
        if xbmcplugin:
            xbmcplugin.endOfDirectory(handle)
            return
    except Exception:
        pass
def set_resolved_url(handle, succeeded, listitem=None):
    try:
        if xbmcplugin:
            xbmcplugin.setResolvedUrl(handle, succeeded, listitem=listitem._item if hasattr(listitem, '_item') else listitem)
            return
    except Exception:
        pass
    print(f"RESOLVE [{handle}] success={succeeded} item={listitem}")
def get_info_label(label):
    try:
        if xbmc:
            return xbmc.getInfoLabel(label)
    except Exception:
        pass
    return ''
