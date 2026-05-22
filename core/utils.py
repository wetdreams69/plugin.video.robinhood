def get_better_logo(name, logos_dict):
    name_lower = name.lower()
    for key, entry in logos_dict.items():
        keywords = [k.lower() for k in entry.get('keywords', [])]
        if name_lower in keywords or name_lower == key.lower():
            return entry.get('url', '')
    return None
def should_ignore_channel(chan, ignore_categories):
    cat = (chan.get('category') or chan.get('type') or chan.get('group') or '')
    if isinstance(cat, str) and cat.strip().lower() in ignore_categories:
        return True
    tags = chan.get('tags') or chan.get('categories') or []
    try:
        for t in tags:
            if isinstance(t, str) and t.strip().lower() in ignore_categories:
                return True
    except Exception:
        pass
    name = (chan.get('name') or '').lower()
    for ignore in ignore_categories:
        if ignore in name:
            return True
    return False
