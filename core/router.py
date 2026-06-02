import sys
import urllib.parse
import xbmc
import xbmcgui
from urllib.parse import urlparse

import core.constants as const
from core.cache import cache
from core.http_client import HttpClient
from core.player import PlaybackTracker, setup_item
from kodi.api import ListItem, add_directory_item, set_content, end_of_directory, set_resolved_url, log
from resolvers import resolve_url
from providers import PROVIDERS


def build_url(query):
    return const.BASE_URL + '?' + urllib.parse.urlencode(query)


def list_main_menu():
    for provider in PROVIDERS:
        list_item = ListItem(label=provider.label)
        list_item.getVideoInfoTag().setTitle(provider.label)
        url = build_url({'action': 'source', 'provider': provider.id})
        add_directory_item(const.ADDON_HANDLE, url, list_item, isFolder=True)
    end_of_directory(const.ADDON_HANDLE)


def _get_provider(provider_id):
    return next((p for p in PROVIDERS if p.id == provider_id), None)


def play_video(url):
    log(f'[Robinhood] Play request: {url}')
    tracker = PlaybackTracker(url)
    tracker.record_attempt()

    resolved = resolve_url(url)
    if not resolved:
        set_resolved_url(const.ADDON_HANDLE, False, listitem=ListItem(path=''))
        return

    real_url, headers, clearkey = _parse_resolved_url(resolved)
    log(f'[Robinhood] Resolved -> {real_url}')

    if not headers and not clearkey:
        headers = _probe_and_fix_headers(real_url, _generate_default_headers(url))

    setup_item(real_url, headers, clearkey)
    tracker.monitor()


def _parse_resolved_url(resolved):
    real_url = resolved
    headers = ''
    clearkey = ''

    if '&clearkey=' in resolved:
        parts = resolved.rsplit('&clearkey=', 1)
        url_part, clearkey = parts[0], parts[1]
        if '|' in url_part:
            real_url, headers = url_part.split('|', 1)
        else:
            real_url = url_part
    elif '|clearkey=' in resolved:
        real_url, clearkey = resolved.split('|clearkey=', 1)
    elif '|' in resolved:
        real_url, headers = resolved.split('|', 1)

    return real_url, headers, clearkey


def _generate_default_headers(original_url):
    try:
        p = urlparse(original_url)
        ref = f"{p.scheme}://{p.netloc}/"
        ua = HttpClient().headers.get('User-Agent')
        return f'Referer={urllib.parse.quote(ref)}&User-Agent={urllib.parse.quote(ua)}'
    except Exception:
        return ''


def _probe_and_fix_headers(url, current_headers):
    client = HttpClient()
    probe_hdrs = _header_str_to_dict(current_headers)

    try:
        if client.head(url, headers=probe_hdrs).status_code == 200:
            return current_headers

        p = urlparse(url)
        origin = f"{p.scheme}://{p.netloc}"
        candidates = [
            {'Referer': const.HEADERS['referer']},
            {'Referer': origin, 'Origin': origin}
        ]

        ua = client.headers.get('User-Agent')
        for cand in candidates:
            hdrs = dict(cand)
            hdrs['User-Agent'] = ua
            if client.head(url, headers=hdrs).status_code == 200:
                return '&'.join([f'{k}={v}' for k, v in hdrs.items()])
    except Exception:
        pass

    return current_headers


def _header_str_to_dict(headers_str):
    d = {}
    if not headers_str:
        return d
    for part in headers_str.split('&'):
        if '=' in part:
            k, v = part.split('=', 1)
            d[k] = urllib.parse.unquote(v)
    return d


def router(paramstring):
    params = dict(urllib.parse.parse_qsl(paramstring))
    action = params.get('action')

    if action is None:
        list_main_menu()
    elif action == 'source':
        provider = _get_provider(params.get('provider', ''))
        if provider:
            provider.list_sources(build_url)
    elif action == 'options':
        provider = _get_provider(params.get('provider', 'angulismo'))
        if provider:
            provider.list_options(params.get('channel_idx', 0), build_url)
    elif action == 'play':
        play_video(params.get('url', ''))
    elif action == 'clear_cache':
        cache.clear()
        xbmcgui.Dialog().notification('Robinhood', 'Cache limpiado correctamente', xbmcgui.NOTIFICATION_INFO, 3000)
        xbmc.executebuiltin('Container.Refresh')
    else:
        provider = _get_provider(params.get('provider', ''))
        if provider and hasattr(provider, 'route'):
            provider.route(action, params, build_url)
