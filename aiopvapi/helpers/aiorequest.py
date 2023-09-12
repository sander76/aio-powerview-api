"""Class containing the async http methods."""

import asyncio
import logging

import aiohttp
import async_timeout

from aiopvapi.helpers.constants import FWVERSION
from aiopvapi.helpers.tools import join_path, get_base_path

_LOGGER = logging.getLogger(__name__)


class PvApiError(Exception):
    """General Api error. Means we have a problem communication with
    the PowerView hub."""


class PvApiResponseStatusError(PvApiError):
    """Wrong http response error."""


class PvApiMaintenance(PvApiError):
    """Hub is undergoing maintenance."""


class PvApiConnectionError(PvApiError):
    """Problem connecting to PowerView hub."""


class AioRequest:
    """Request class managing hub connection."""

    def __init__(
        self,
        hub_ip,
        loop=None,
        websession=None,
        timeout: int = 15,
        api_version: int | None = None,
    ) -> None:
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
        self.api_version: int | None = api_version
        self._last_request_status: int = 0
        _LOGGER.debug("Powerview api version: %s", self.api_version)

    @property
    def api_path(self) -> str:
        """Returns the initial api call path"""
        if self.api_version and self.api_version >= 3:
            return "home"
        return "api"

    async def check_response(self, response, valid_response_codes):
        """Check the response for correctness."""
        _val = None
        if response.status == 403 and self._last_request_status == 423:
            # if last status was hub undergoing maint then it is common
            # on reboot for a 403 response. Generally this should raise
            # PvApiResponseStatusError but as this is unavoidable we
            # class this situation as still undergoing maintenance
            _val = False
        elif response.status in [204, 423]:
            # 423 hub under maintenance, returns data, but not shade
            _val = True
        elif response.status in valid_response_codes:
            _val = await response.json()

        # store the status for next check
        self._last_request_status = response.status

        # raise a maintenance error
        if isinstance(_val, bool):
            raise PvApiMaintenance("Powerview Hub is undergoing maintenance")

        # if none of the above checks passed, raise a response error
        if _val is None:
            raise PvApiResponseStatusError(response.status)

        # finally, return the result
        return _val

    async def get(self, url: str, params: str = None) -> dict:
        """
        Get a resource.

        :param url:
        :param params:
        :return:
        """
        response = None
        try:
            _LOGGER.debug("Sending GET request to: %s params: %s", url, params)
            with async_timeout.timeout(self._timeout):
                response = await self.websession.get(url, params=params)
                return await self.check_response(response, [200, 204])
        except (asyncio.TimeoutError, aiohttp.ClientError) as error:
            raise PvApiConnectionError(
                "Failed to communicate with PowerView hub"
            ) from error
        finally:
            if response is not None:
                await response.release()

    async def post(self, url: str, data: dict = None):
        """
        Post a resource update.

        :param url:
        :param data: a Dict. later converted to json.
        :return:
        """
        response = None
        try:
            _LOGGER.debug("Sending POST request to: %s data: %s", url, data)
            with async_timeout.timeout(self._timeout):
                response = await self.websession.post(url, json=data)
                return await self.check_response(response, [200, 201])
        except (asyncio.TimeoutError, aiohttp.ClientError) as error:
            raise PvApiConnectionError(
                "Failed to communicate with PowerView hub"
            ) from error
        finally:
            if response is not None:
                await response.release()

    async def put(self, url: str, data: dict = None, params=None):
        """
        Do a put request.

        :param url: string
        :param data: a Dict. later converted to json.
        :return:
        """
        response = None
        try:
            _LOGGER.debug(
                "Sending PUT request to: %s params: %s data: %s",
                url,
                params,
                data,
            )
            with async_timeout.timeout(self._timeout):
                response = await self.websession.put(url, json=data, params=params)
                return await self.check_response(response, [200, 204])
        except (asyncio.TimeoutError, aiohttp.ClientError) as error:
            raise PvApiConnectionError(
                "Failed to communicate with PowerView hub"
            ) from error
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
            _LOGGER.debug("Sending DELETE request to: %s with param %s", url, params)
            with async_timeout.timeout(self._timeout):
                response = await self.websession.delete(url, params=params)
                return await self.check_response(response, [200, 204])
        except (asyncio.TimeoutError, aiohttp.ClientError) as error:
            raise PvApiConnectionError(
                "Failed to communicate with PowerView hub"
            ) from error
        finally:
            if response is not None:
                await response.release()
