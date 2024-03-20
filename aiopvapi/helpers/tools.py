"""Tools for converting data from powerview hub."""

import base64

from aiopvapi.helpers.constants import ATTR_ID


def unicode_to_base64(string):
    """Convert unicode to base64."""


def base64_to_unicode(string):
    """Convert base64 to unicode."""


def get_base_path(ip_address, url):
    """Convert url and ip to base path."""
    # Remove scheme if present
    ip_address = ip_address.split("://")[-1].strip("/")
    # clean up url (leading or trailing or multiple '/')
    urls = filter(lambda p: p != "", url.split("/"))
    # Put everything back together
    return "http://{}".format(join_path(ip_address, *urls))


def join_path(base, *parts: str):
    """Create urls from base path and additional parts."""
    _parts = "/".join((_part.strip("/") for _part in parts))
    # _parts = '/'.join(parts)
    if base.endswith("/"):
        url = base + _parts
    else:
        url = base + "/" + _parts
    return url


def get_raw_id(id_):
    """Create a dict with the resource id.

    This can serve as the minimal raw input for ie scene instantiation
    and allows for simple activation of that scene.
    """
    return {ATTR_ID: id_}
