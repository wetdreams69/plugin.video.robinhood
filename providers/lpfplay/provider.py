from datetime import datetime, timezone
import core.constants as const
from core.http_client import HttpClient
from kodi.api import ListItem, add_directory_item, set_content, end_of_directory, log
from providers.lpfplay.constants import (
    LPF_API_BASE, LPF_HEADERS, LPF_MAIN_PAGE_ID,
    LPF_TIMEZONE, COLOR_LIVE, COLOR_FINAL, COLOR_UPCOMING,
)

_http = HttpClient()


def _get(endpoint):
    url = f"{LPF_API_BASE}{endpoint}"
    resp = _http.get(url, headers=LPF_HEADERS, timeout=10)
    resp.raise_for_status()
    return resp.json()


def _utc_ms_to_local(ts_ms):
    try:
        import pytz
        tz = pytz.timezone(LPF_TIMEZONE)
        return datetime.fromtimestamp(ts_ms / 1000.0, tz)
    except Exception:
        return datetime.fromtimestamp(ts_ms / 1000.0, timezone.utc)


def _color(text, color):
    return f"[COLOR={color}]{text}[/COLOR]"


def _format_label(item, entity, title):
    label = title
    date_str = ''
    if entity == 'events':
        start_ts = item.get('eventStartDate')
        if item.get('isStarted'):
            label = f"{_color('[EN VIVO]', COLOR_LIVE)} {title}"
        elif item.get('eventIsOver'):
            label = f"{_color('[FIN]', COLOR_FINAL)} {title}"
        elif start_ts:
            dt = _utc_ms_to_local(start_ts)
            date_str = dt.strftime('%Y-%m-%d')
            label = f"{_color(dt.strftime('%d/%m %H:%M'), COLOR_UPCOMING)} {title}"
    else:
        ts = item.get('date') or item.get('dateUpdate')
        if ts:
            dt = _utc_ms_to_local(ts)
            date_str = dt.strftime('%Y-%m-%d')
            label = f"{_color(dt.strftime('%d/%m'), COLOR_UPCOMING)} {title}"
        dur = item.get('duration')
        if dur and not date_str:
            label = f"[{dur}] {label}"
    return label, date_str


class LPFPlayProvider:
    id = 'lpfplay'
    label = 'LPF Play'
    icon = const.ADDON_PATH + '/resources/lpfplay_icon.png'

    def list_sources(self, build_url):
        try:
            data = _get(f"/interface/pages/{LPF_MAIN_PAGE_ID}")
            for section in data.get('sections', []):
                title = section.get('title', '').strip()
                s_id = section.get('sectionId')
                if not title or not s_id:
                    continue
                list_item = ListItem(label=title)
                list_item.getVideoInfoTag().setTitle(title)
                list_item.getVideoInfoTag().setPlot(f"{len(section.get('items', []))} videos")
                url = build_url({'action': 'lpf_section', 'provider': self.id, 'section_id': s_id, 'page': 1})
                add_directory_item(const.ADDON_HANDLE, url, list_item, isFolder=True)
        except Exception as e:
            log(f"[LPFPlay] Error loading categories: {e}")
        end_of_directory(const.ADDON_HANDLE)

    def list_section(self, section_id_raw, page, build_url):
        section_id = section_id_raw.split('&')[0]
        page = int(page)
        try:
            data = _get(f"/interface/pages/section/{section_id}?page={page}&limit=25")
            for item in data.get('items', []):
                v_url = item.get('videoUrl')
                if not v_url:
                    continue
                title = item.get('title', 'Video').strip()
                thumb = (item.get('optimizedEventImage')
                         or item.get('optimizedImage')
                         or item.get('optimizedPoster') or '')
                desc = item.get('description') or item.get('longDescription') or ''
                entity = item.get('entity', '')
                label, date_str = _format_label(item, entity, title)

                list_item = ListItem(label=label)
                list_item.set_art({'thumb': thumb, 'icon': thumb})
                list_item.set_property('IsPlayable', 'true')
                tag = list_item.getVideoInfoTag()
                tag.setTitle(title)
                tag.setPlot(desc)
                if date_str:
                    tag.setFirstAired(date_str)
                play_url = build_url({'action': 'play', 'url': v_url})
                add_directory_item(const.ADDON_HANDLE, play_url, list_item, isFolder=False)

            if data.get('hasPagination') and len(data.get('items', [])) >= 25:
                next_item = ListItem(label='[B]Página siguiente >>[/B]')
                next_url = build_url({'action': 'lpf_section', 'provider': self.id, 'section_id': section_id, 'page': page + 1})
                add_directory_item(const.ADDON_HANDLE, next_url, next_item, isFolder=True)
        except Exception as e:
            log(f"[LPFPlay] Error loading section: {e}")
        set_content(const.ADDON_HANDLE, 'videos')
        end_of_directory(const.ADDON_HANDLE)

    def route(self, action, params, build_url):
        if action == 'lpf_section':
            self.list_section(
                params.get('section_id', ''),
                params.get('page', 1),
                build_url,
            )
