import base64


def decode_base64(string):
    """
    Converts base64 to unicode
    """
    return base64.b64decode(string).decode('utf-8')