"""
Copyright start
MIT License
Copyright (c) 2026 Fortinet Inc
Copyright end
"""

import feedparser
import socket
import ipaddress
from urllib.parse import urlparse

from connectors.core.connector import get_logger, ConnectorError

logger = get_logger('rss-feed')


class RSSFeed(object):
    def __init__(self, config):
        pass


def validate_feed_url(url):
    if not url:
        raise ConnectorError("Feed URL is required")

    parsed = urlparse(url)

    # Allow only HTTP/HTTPS
    if parsed.scheme.lower() not in ["http", "https"]:
        raise ConnectorError("Only HTTP/HTTPS URLs are allowed")

    if not parsed.hostname:
        raise ConnectorError("Invalid URL")

    host = parsed.hostname.lower()

    # Explicit localhost block
    if host in ["localhost"]:
        raise ConnectorError("Localhost URLs are not allowed")

    try:
        resolved_ip = socket.gethostbyname(host)
    except socket.gaierror:
        raise ConnectorError("Unable to resolve target host")

    ip = ipaddress.ip_address(resolved_ip)

    if (
            ip.is_private or
            ip.is_loopback or
            ip.is_link_local or
            ip.is_multicast or
            ip.is_reserved
    ): raise ConnectorError("Internal or restricted IP addresses are not allowed")

    return url


def get_indicators(config, params):
    try:
        url = params.get("url")
        validate_feed_url(url)
        feed = feedparser.parse(url)
        if feed.get("bozo"):
            feed.pop("bozo_exception", None)
        return feed
    except ConnectorError as err:
        raise err

    except Exception as err:
        logger.exception(str(err))
        raise ConnectorError("Unable to fetch RSS feed")


def check_health(config):
    return True


operations = {
    'get_indicators': get_indicators
}
