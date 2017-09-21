import base64


def unicode_to_base64(string):
    """converts unicode to base64"""

    bts = string.encode() #encode to a bytes object
    _val = base64.b64encode(bts)
    return _val.decode('utf-8')


def base64_to_unicode(string):
    """
    Converts base64 to unicode
    """
    return base64.b64decode(string).decode('utf-8')


def get_base_path(ip_address, url):
    return 'http://{}/{}'.format(ip_address, url)


def join_path(base,*parts):
    _parts = '/'.join(parts)
    if base.endswith("/"):
        url = base + _parts
    else:
        url = base + '/' + _parts
    return url