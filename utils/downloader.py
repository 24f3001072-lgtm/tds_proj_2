import base64
import requests

def download_url_or_datauri(url: str):
    """
    Downloads raw bytes from a URL or a data: URI.
    """
    if url.startswith("data:"):
        header, encoded = url.split(",", 1)
        return base64.b64decode(encoded)

    resp = requests.get(url)
    resp.raise_for_status()
    return resp.content
