import urllib.parse

from PySide6.QtCore import QUrl

from .config import HOME_PAGE, SEARCH_URL


def resolve_address(text, home=HOME_PAGE, search_url=SEARCH_URL):
    text = text.strip()
    if not text:
        return QUrl(home)
    if "://" in text:
        return QUrl.fromUserInput(text)
    if text.startswith(("localhost", "127.0.0.1")) or "/" in text:
        return QUrl.fromUserInput("http://" + text)
    if "." in text and " " not in text:
        return QUrl.fromUserInput("https://" + text)
    return QUrl(search_url.format(urllib.parse.quote_plus(text)))
