import sys
from kodi.api import get_addon
ADDON = get_addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_PATH = ADDON.getAddonInfo('path')
ADDON_HANDLE = int(sys.argv[1]) if len(sys.argv) > 1 else 0
BASE_URL = sys.argv[0] if len(sys.argv) > 0 else ''
HEADERS = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9,es-AR;q=0.8,es-US;q=0.7,es;q=0.6',
    'cache-control': 'no-cache',
    'origin': 'https://angulismotv.pages.dev',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://angulismotv.pages.dev/',
    'sec-ch-ua': '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36'
}
URL_MAIN_PAGE = 'https://angulismotv.pages.dev'
URL_CHANNELS = 'https://json.angulismotv.workers.dev/channeIs'
URL_LOGOS = 'https://logos.angulismotv.workers.dev/logos'
URL_FALLBACK = 'https://raw.githubusercontent.com/Aguus467/test/main/json.json'
BAD_LOGO_DOMAINS = ('seeklogo.com', 'hopelife.bestleague.world', 'foromedios.com')
IGNORE_CATEGORIES = {'entretenimiento', 'los simpsons', 'multicam', 'juegos', 'pelicula'}
