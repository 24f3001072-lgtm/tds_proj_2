# utils/downloader.py
import base64
import requests

def download_url_or_datauri(link, base_url=None):
    """Returns bytes, no exceptions."""
    try:
        if isinstance(link, dict) and "atob" in link:
            return base64.b64decode(link["atob"])

        if isinstance(link, str) and link.startswith("data:"):
            header, b64 = link.split(",", 1)
            return base64.b64decode(b64)

        if isinstance(link, str) and not link.startswith("http"):
            link = requests.compat.urljoin(base_url, link)

        r = requests.get(link, timeout=20)
        r.raise_for_status()
        return r.content

    except:
        return None
