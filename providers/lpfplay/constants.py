LPF_API_BASE = "https://insight-api-shared.univtec.com"
LPF_DOMAIN = "https://www.lpfplay.com"
LPF_TENANT_ID = "lpf"
LPF_PLATFORM = "web"
LPF_DEVICE_TYPE = "web"
LPF_MAIN_PAGE_ID = "684743a8b6b14151aae96cad"
LPF_TIMEZONE = "America/Argentina/Buenos_Aires"
LPF_UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
LPF_HEADERS = {
    'accept': '*/*',
    'platform': LPF_PLATFORM,
    'origin': LPF_DOMAIN,
    'referer': f"{LPF_DOMAIN}/",
    'user-agent': LPF_UA,
    'x-device-type': LPF_DEVICE_TYPE,
    'x-tenant-id': LPF_TENANT_ID,
}
COLOR_UPCOMING = 'FFD2D2D2'
COLOR_LIVE = 'FFF69E20'
COLOR_FINAL = 'FF666666'
