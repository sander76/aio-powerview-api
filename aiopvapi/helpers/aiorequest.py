"""Class containing the async http methods."""

import asyncio
import logging

import aiohttp
import async_timeout

_LOGGER = logging.getLogger(__name__)


class PvApiError(Exception):
    """General Api error. Means we have a problem communication with
    the PowerView hub."""

    pass


class PvApiResponseStatusError(PvApiError):
    """Wrong http response error."""


class PvApiConnectionError(PvApiError):
    """Problem connecting to PowerView hub."""


async def check_response(response, valid_response_codes):
    """Check the response for correctness."""
    if response.status in [204, 423]:
        return True
    if response.status in valid_response_codes:
        _js = await response.json()
        return _js
    else:
        raise PvApiResponseStatusError(response.status)


class AioRequest:
    """Request class managing hub connection."""

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
            self.websession = aiohttp.ClientSession()

    async def get(self, url: str, params: str = None) -> dict:
        """
        Get a resource.

        :param url:
        :param params:
        :return:
        """
        _LOGGER.debug("Sending a get request")
        response = None
        try:
            _LOGGER.debug("Sending GET request to: %s" % url)
            with async_timeout.timeout(self._timeout):
                response = await self.websession.get(url, params=params)
                return await check_response(response, [200, 204])
        except (asyncio.TimeoutError, aiohttp.ClientError) as error:
            _LOGGER.error("Failed to communicate with PowerView hub: %s", error)
            raise PvApiConnectionError
        finally:
            if response is not None:
                await response.release()

    async def post(self, url: str, data: dict = None):
        response = None
        try:
            with async_timeout.timeout(self._timeout):
                _LOGGER.debug("url: %s", url)
                _LOGGER.debug("data: %s", data)
                response = await self.websession.post(url, json=data)
                return await check_response(response, [200, 201])
        except (asyncio.TimeoutError, aiohttp.ClientError) as error:
            _LOGGER.error("Failed to communicate with PowerView hub: %s", error)
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
            with async_timeout.timeout(self._timeout):
                _LOGGER.debug("url: %s", url)
                _LOGGER.debug("data: %s", data)
                response = await self.websession.put(url, json=data)
            return await check_response(response, [200, 204])
        except (asyncio.TimeoutError, aiohttp.ClientError) as error:
            _LOGGER.error("Failed to communicate with PowerView hub: %s", error)
            raise PvApiConnectionError
        finally:
            if response is not None:
                await response.release()

    async def delete(self, url: str, params: dict = None):
        """
        Delete a resource.

        :param url: Endpoint
        :param params: parameters
        :return: Response body

        :raises PvApiError when something is wrong.
        """
        response = None
        try:
            with async_timeout.timeout(self._timeout):
                response = await self.websession.delete(url, params=params)
            return await check_response(response, [200, 204])
        except (asyncio.TimeoutError, aiohttp.ClientError) as error:
            _LOGGER.error("Failed to communicate with PowerView hub: %s", error)
            raise PvApiConnectionError
        finally:
            if response is not None:
                await response.release()
