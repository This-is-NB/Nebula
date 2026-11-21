from PySide6.QtCore import QUrl
from PySide6.QtWebEngineCore import (
    QWebEngineProfile,
    QWebEngineUrlRequestInterceptor,
)


class TrackerInterceptor(QWebEngineUrlRequestInterceptor):
    TRACKERS = (
        "doubleclick.net",
        "googlesyndication.com",
        "google-analytics.com",
        "facebook.net",
        "connect.facebook.net",
        "hotjar.com",
        "scorecardresearch.com",
        "advertising.com",
    )

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings

    def interceptRequest(self, info):
        if not self.settings.get("block_trackers", True):
            return
        host = QUrl(info.requestUrl()).host().lower()
        if any(host == item or host.endswith("." + item) for item in self.TRACKERS):
            info.block(True)


def create_profile(settings, parent, private=False):
    if private:
        profile = QWebEngineProfile(parent)
        profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.MemoryHttpCache)
        profile.setPersistentCookiesPolicy(
            QWebEngineProfile.PersistentCookiesPolicy.NoPersistentCookies
        )
    else:
        profile = QWebEngineProfile.defaultProfile()
        profile.setPersistentCookiesPolicy(
            QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies
        )
        profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)

    profile.setUrlRequestInterceptor(TrackerInterceptor(settings, parent))
    return profile
