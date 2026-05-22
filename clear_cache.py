from core.cache import cache
import xbmcgui
cache.clear()
xbmcgui.Dialog().notification('Robinhood', 'Cache limpiado correctamente', xbmcgui.NOTIFICATION_INFO, 3000)
