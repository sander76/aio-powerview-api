"""Class containing the async http methods."""

import asyncio
import json
import logging
import aiohttp
import async_timeout

_LOGGER = logging.getLogger(__name__)


class PvApiError(Exception):
    pass


class PvApiResponseStatusError(PvApiError):
    pass


class PvApiConnectionError(PvApiError):
    pass


@asyncio.coroutine
def check_response(response, valid_reponse_codes):
    if response.status == 204:
        return True
    if response.status in valid_reponse_codes:
        _js = yield from response.json()
        return _js
    else:
        raise PvApiResponseStatusError


class AioRequest:
    def __init__(self, loop, websession, timeout=15):
        self._timeout = timeout
        self.loop = loop
        self.websession = websession

    @asyncio.coroutine
    def get(self, url: str, params: str = None) -> dict:
        _LOGGER.debug("Sending a get request")
        response = None
        try:
            _LOGGER.debug('Sending GET request to: %s' % url)
            with async_timeout.timeout(self._timeout, loop=self.loop):
                response = yield from self.websession.get(url, params=params)
                return (yield from check_response(response, [200, 204]))
        except (asyncio.TimeoutError, aiohttp.ClientError) as error:
            _LOGGER.error('Failed to communicate with PowerView hub: %s',
                          error)
            raise PvApiConnectionError
        finally:
            if response is not None:
                yield from response.release()

    @asyncio.coroutine
    def post(self, url: str, data: dict = None):
        response = None
        #todo: do I need to convert to json or can the post method handle dicts?
        # if data:
        #     data = json.dumps(data, ensure_ascii=True)
        try:
            with async_timeout.timeout(self._timeout, loop=self.loop):
                response = yield from self.websession.post(url, json=data)
                return (yield from check_response(response, [200, 201]))
        except (asyncio.TimeoutError, aiohttp.ClientError) as error:
            _LOGGER.error('Failed to communicate with PowerView hub: %s',
                          error)
            raise PvApiConnectionError
        finally:
            if response is not None:
                yield from response.release()

    @asyncio.coroutine
    def put(self, url: str, data: dict = None):
        """
        Do a put request.

        :param url: string
        :param data: a Dict. later converted to json.
        :return:
        """
        response = None
        try:
            with async_timeout.timeout(self._timeout, loop=self.loop):
                response = yield from self.websession.put(url, json=data)
                return (yield from check_response(response, [200, 204]))
        except (asyncio.TimeoutError, aiohttp.ClientError) as error:
            _LOGGER.error('Failed to communicate with PowerView hub: %s',
                          error)
            raise PvApiConnectionError
        finally:
            if response is not None:
                yield from response.release()

    @asyncio.coroutine
    def delete(self, url: str, params: str = None):
        response = None
        try:
            with async_timeout.timeout(self._timeout, loop=self.loop):
                response = yield from self.websession.delete(url, params=params)
                return (yield from check_response(response, [200, 204]))
        except (asyncio.TimeoutError, aiohttp.ClientError) as error:
            _LOGGER.error('Failed to communicate with PowerView hub: %s',
                          error)
            raise PvApiConnectionError
        finally:
            if response is not None:
                yield from response.release()