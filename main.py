import sys
from core.router import router
from core.cache import cache
from kodi.api import log

if __name__ == '__main__':
    try:
        query = sys.argv[2][1:] if len(sys.argv) > 2 and sys.argv[2].startswith('?') else ''
        router(query)
    except Exception as e:
        log(f'[Robinhood] Critical Error: {str(e)}')
    finally:
        cache.close()
