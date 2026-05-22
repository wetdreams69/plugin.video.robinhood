import urllib.parse
from core.api import get_channels, get_logos
from core.cache import cache
from core.utils import get_better_logo, should_ignore_channel
import core.constants as const
from kodi.api import ListItem, add_directory_item, set_content, end_of_directory


class AngulismoProvider:
    id = 'angulismo'
    label = 'Angulismo TV'
    icon = const.ADDON_PATH + '/icon.png'

    def list_sources(self, build_url):
        channels = get_channels()
        logos_dict = get_logos()
        for idx, channel in enumerate(channels):
            if not channel.get('show', True) or should_ignore_channel(channel, const.IGNORE_CATEGORIES):
                continue
            name = channel.get('name', 'Unknown Channel')
            logo = channel.get('logo', '')
            if any(bad in logo for bad in const.BAD_LOGO_DOMAINS):
                logo = ''
            better_logo = get_better_logo(name, logos_dict)
            if better_logo:
                logo = better_logo
            list_item = ListItem(label=name)
            list_item.set_art({'thumb': logo, 'icon': logo, 'poster': logo})
            list_item.getVideoInfoTag().setTitle(name)
            url = build_url({'action': 'options', 'provider': self.id, 'channel_idx': idx})
            add_directory_item(const.ADDON_HANDLE, url, list_item, isFolder=True)
        set_content(const.ADDON_HANDLE, 'videos')
        end_of_directory(const.ADDON_HANDLE)

    def list_options(self, channel_idx, build_url):
        channels = get_channels()
        idx = int(channel_idx)
        if idx >= len(channels):
            return
        options = channels[idx].get('options', [])
        for option in options:
            name = option.get('name', 'Source')
            url = option.get('iframe') or option.get('url', '')
            if not url:
                continue
            stats = cache.get(f'stats:{url}') or {'s': 0, 't': 0}
            color = _get_status_color(stats)
            list_item = ListItem(label=f'[COLOR {color}]{name}[/COLOR]')
            list_item.getVideoInfoTag().setTitle(name)
            list_item.set_property('IsPlayable', 'true')
            play_url = build_url({'action': 'play', 'url': url})
            add_directory_item(const.ADDON_HANDLE, play_url, list_item, isFolder=False)
        end_of_directory(const.ADDON_HANDLE)


def _get_status_color(stats):
    if stats['t'] == 0:
        return 'white'
    if stats['s'] == 0:
        return 'red'
    if stats['s'] == stats['t']:
        return 'green'
    return 'yellow'
