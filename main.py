import sys
import urllib.parse
import json
import requests
import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon
import time

addon = xbmcaddon.Addon()
BASE_URL = addon.getSetting("base_url").strip().rstrip("/")
HANDLE = int(sys.argv[1])
ARGS = urllib.parse.parse_qs(sys.argv[2][1:])

def fetch_metadata():
    try:
        response = requests.get(f'{BASE_URL}/assets/metadata', timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        xbmcgui.Dialog().notification("Timeout", "The server did not respond in time", xbmcgui.NOTIFICATION_ERROR)
    except requests.exceptions.ConnectionError:
        xbmcgui.Dialog().notification("Connection failed", "Could not connect to the backend", xbmcgui.NOTIFICATION_ERROR)
    except Exception as e:
        xbmcgui.Dialog().notification("Error", f"Error fetching metadata: {e}", xbmcgui.NOTIFICATION_ERROR)
    return []

def fetch_m3u8(endpoint):
    try:
        response = requests.get(f'{BASE_URL}/assets/{endpoint}', timeout=5)
        response.raise_for_status()
        return response.text
    except requests.exceptions.Timeout:
        xbmcgui.Dialog().notification("Timeout", "The server did not respond when requesting the stream", xbmcgui.NOTIFICATION_ERROR)
    except requests.exceptions.ConnectionError:
        xbmcgui.Dialog().notification("Connection failed", "Could not connect to the backend", xbmcgui.NOTIFICATION_ERROR)
    except Exception as e:
        xbmcgui.Dialog().notification("Error", f"Could not fetch the stream: {e}", xbmcgui.NOTIFICATION_ERROR)
    return ""

def refresh_sources():
    try:
        response = requests.post(f'{BASE_URL}/assets/refresh', timeout=5)
        if response.status_code == 202:
            xbmcgui.Dialog().notification("Update started", "Scraping in progress...", xbmcgui.NOTIFICATION_INFO)

            wait = xbmcgui.Dialog().yesno("Wait for completion", "Do you want to wait until scraping finishes?")
            if wait:
                for _ in range(15):
                    status = requests.get(f"{BASE_URL}/status", timeout=5).json()
                    if not status.get("scraping", {}).get("running", False):
                        xbmcgui.Dialog().notification("Scraping complete", "Sources have been updated", xbmcgui.NOTIFICATION_INFO)
                        return
                    time.sleep(2)
                xbmcgui.Dialog().notification("Scraping in progress", "Still not finished after 30s", xbmcgui.NOTIFICATION_WARNING)

        elif response.status_code == 409:
            xbmcgui.Dialog().notification("Already running", "A scraping job is already in progress", xbmcgui.NOTIFICATION_WARNING)
        else:
            xbmcgui.Dialog().notification("Error", f"Unexpected code: {response.status_code}", xbmcgui.NOTIFICATION_ERROR)
    except requests.exceptions.Timeout:
        xbmcgui.Dialog().notification("Timeout", "The server did not respond", xbmcgui.NOTIFICATION_ERROR)
    except requests.exceptions.ConnectionError:
        xbmcgui.Dialog().notification("Connection failed", "Could not connect to the backend", xbmcgui.NOTIFICATION_ERROR)
    except Exception as e:
        xbmcgui.Dialog().notification("Error", str(e), xbmcgui.NOTIFICATION_ERROR)

def list_sites():
    url = f"{sys.argv[0]}?refresh=1"
    li = xbmcgui.ListItem(label="[Refresh sources 📡]")
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=li, isFolder=False)

    data = fetch_metadata()
    for site in data:
        name = site.get("site")
        url = f"{sys.argv[0]}?site={urllib.parse.quote(name)}"
        li = xbmcgui.ListItem(label=name)
        xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(HANDLE)

def list_channels(site_name):
    data = fetch_metadata()
    site_data = next((s for s in data if s["site"] == site_name), None)
    if not site_data:
        xbmcgui.Dialog().notification("Error", f"Site not found: {site_name}")
        return

    for ch in site_data["channels"]:
        label = ch["channel"].replace(f"{site_name}-", "").replace("_", " ").title()
        url = f"{sys.argv[0]}?stream={urllib.parse.quote(ch['endpoint'])}&channel={urllib.parse.quote(label)}"
        li = xbmcgui.ListItem(label=label)
        xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(HANDLE)

def list_stream_options(endpoint, label):
    content = fetch_m3u8(endpoint)
    lines = content.strip().splitlines()
    options = []

    current_title = ""
    for line in lines:
        if line.startswith("#EXTINF"):
            current_title = line.split(",", 1)[-1]
        elif line.startswith("http"):
            options.append((current_title, line))

    for title, url in options:
        li = xbmcgui.ListItem(label=title or "Stream")
        li.setInfo('video', {'title': f"{label} - {title}"})
        li.setPath(url)
        xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=li, isFolder=False)

    xbmcplugin.endOfDirectory(HANDLE)

if 'refresh' in ARGS:
    refresh_sources()
elif 'stream' in ARGS and 'channel' in ARGS:
    list_stream_options(ARGS['stream'][0], ARGS['channel'][0])
elif 'site' in ARGS:
    list_channels(ARGS['site'][0])
else:
    list_sites()
