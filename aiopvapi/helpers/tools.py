import base64

from aiopvapi.helpers.constants import ATTR_ID


def unicode_to_base64(string):
    """converts unicode to base64"""
    return base64.b64encode(string.encode()).decode("utf-8")


def base64_to_unicode(string):
    """Converts base64 to unicode."""
    return base64.b64decode(string).decode("utf-8")


def get_base_path(ip_address, url):
    # Remove scheme if present
    ip_address = ip_address.split("://")[-1].strip("/")
    # clean up url (leading or trailing or multiple '/')
    urls = filter(lambda p: p != "", url.split("/"))
    # Put everything back together
    return "http://{}".format(join_path(ip_address, *urls))


def join_path(base, *parts: str):
    """Creates urls from base path and additional parts."""
    _parts = "/".join((_part.strip("/") for _part in parts))
    # _parts = '/'.join(parts)
    if base.endswith("/"):
        url = base + _parts
    else:
        url = base + "/" + _parts
    return url


def get_raw_id(id_):
    """Creates a dict with the resource id.

    This can serve as the minimal raw input for ie scene instantiation
    and allows for simple activation of that scene."""
    return {ATTR_ID: id_}
