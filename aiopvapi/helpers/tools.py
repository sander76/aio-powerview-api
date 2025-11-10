"""Tools for converting data from powerview hub."""

import base64
import logging

from aiopvapi.helpers.constants import ATTR_ID

from collections.abc import Iterable
from typing import Any

_LOGGER = logging.getLogger(__name__)


def unicode_to_base64(string):
    """Convert unicode to base64."""
    try:
        return base64.b64encode(string.encode()).decode("utf-8")
    except (base64.binascii.Error, UnicodeDecodeError) as e:
        # Handle the error and return the string
        _LOGGER.debug("Error encoding string '%s': %s", string, e)
        return string


def base64_to_unicode(string):
    """Convert base64 to unicode."""
    try:
        return base64.b64decode(string).decode("utf-8")
    except (base64.binascii.Error, UnicodeDecodeError) as e:
        # Handle the error and return the base64
        _LOGGER.debug("Error decoding base64 string '%s': %s", string, e)
        return string


def get_base_path(ip_address, url):
    """Convert url and ip to base path."""
    # Remove scheme if present
    ip_address = ip_address.split("://")[-1].strip("/")
    # clean up url (leading or trailing or multiple '/')
    urls = filter(lambda p: p != "", url.split("/"))
    # Put everything back together
    return f"http://{join_path(ip_address, *urls)}"


def join_path(base, *parts: str):
    """Create urls from base path and additional parts."""
    _parts = "/".join(_part.strip("/") for _part in parts)
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


def map_data_by_id(data: Iterable[dict[str | int, Any]]):
    """Return a dict with the key being the id for a list of entries."""
    return {entry[ATTR_ID]: entry for entry in data}


def deep_update_dict(original: dict, updates: dict) -> dict:
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(original.get(key), dict):
            deep_update_dict(original[key], value)
        else:
            original[key] = value
    return original
