"""Class containing the async http methods."""

import asyncio
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


async def check_response(response, valid_response_codes):
    if response.status == 204:
        return True
    if response.status in valid_response_codes:
        _js = await response.json()
        return _js
    else:
        raise PvApiResponseStatusError


class AioRequest:
    def __init__(self, hub_ip, loop=None, websession=None, timeout=15):
        self.hub_ip = hub_ip
        self._timeout = timeout
        if loop:
            self.loop = loop
        else:
            self.loop = asyncio.get_event_loop()
        if websession:
            self.websession = websession
        else:
            self.websession = aiohttp.ClientSession(loop=self.loop)

    async def get(self, url: str, params: str = None) -> dict:
        _LOGGER.debug("Sending a get request")
        response = None
        try:
            _LOGGER.debug('Sending GET request to: %s' % url)
            with async_timeout.timeout(self._timeout, loop=self.loop):
                response = await self.websession.get(url, params=params)
                return await check_response(response, [200, 204])
        except (asyncio.TimeoutError, aiohttp.ClientError) as error:
            _LOGGER.error('Failed to communicate with PowerView hub: %s',
                          error)
            raise PvApiConnectionError
        finally:
            if response is not None:
                await response.release()

    async def post(self, url: str, data: dict = None):
        response = None
        try:
            with async_timeout.timeout(self._timeout, loop=self.loop):
                response = await self.websession.post(url, json=data)
                return await check_response(response, [200, 201])
        except (asyncio.TimeoutError, aiohttp.ClientError) as error:
            _LOGGER.error('Failed to communicate with PowerView hub: %s',
                          error)
            raise PvApiConnectionError
        finally:
            if response is not None:
                await response.release()

    async def put(self, url: str, data: dict = None):
        """
        Do a put request.

        :param url: string
        :param data: a Dict. later converted to json.
        :return:
        """
        response = None
        try:
            with async_timeout.timeout(self._timeout, loop=self.loop):
                response = await self.websession.put(url, json=data)
            return await check_response(response, [200, 204])
        except (asyncio.TimeoutError, aiohttp.ClientError) as error:
            _LOGGER.error('Failed to communicate with PowerView hub: %s',
                          error)
            raise PvApiConnectionError
        finally:
            if response is not None:
                await response.release()

    async def delete(self, url: str, params: str = None):
        response = None
        try:
            with async_timeout.timeout(self._timeout, loop=self.loop):
                response = await self.websession.delete(url)
            return await check_response(response, [200, 204])
        except (asyncio.TimeoutError, aiohttp.ClientError) as error:
            _LOGGER.error('Failed to communicate with PowerView hub: %s',
                          error)
            raise PvApiConnectionError
        finally:
            if response is not None:
                await response.release()
