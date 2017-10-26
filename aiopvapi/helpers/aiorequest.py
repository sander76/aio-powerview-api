"""Class containing the async http methods."""

import asyncio
import json
import logging
import aiohttp
import async_timeout

_LOGGER = logging.getLogger(__name__)


class AioRequest:
    def __init__(self, loop, websession, timeout=15):
        self._timeout = timeout
        self.loop = loop
        self.websession = websession

    @asyncio.coroutine
    def get(self, url: str, params: str = None) -> dict:
        _LOGGER.debug("Sending a get request")
        data = None
        response = None
        try:
            _LOGGER.info('Sending GET request to: %s' % url)
            with async_timeout.timeout(self._timeout, loop=self.loop):
                response = yield from self.websession.get(url, params=params)
                if response.status == 200:
                    data = yield from response.json()
        except ValueError:
            _LOGGER.error("Error parsing Json message")
        except (asyncio.TimeoutError, aiohttp.ClientError) as error:
            _LOGGER.error('Failed to communicate with PowerView hub: %s',
                          error)
        finally:
            if response is not None:
                yield from response.release()
        return data

    @asyncio.coroutine
    def post(self, url: str, data: dict = None):
        resp = None
        _json = None  # empty result
        _status = None
        if data:
            data = json.dumps(data, ensure_ascii=True)
        try:
            with async_timeout.timeout(self._timeout, loop=self.loop):
                resp = yield from self.websession.post(url, json=data)
                _status = resp.status
                if _status in [200, 201]:
                    _json = yield from resp.json()
                else:
                    _LOGGER.error("Error %s on %s", resp.status, url)
        except ValueError:
            _LOGGER.error("Error parsing Json message")
        except (asyncio.TimeoutError, aiohttp.ClientError):
            _LOGGER.error("Client connection error")
        except Exception as e:
            _LOGGER.exception(e)
        finally:
            if resp is not None:
                yield from resp.release()

            return _json, _status

    @asyncio.coroutine
    def put(self, url: str, data: dict = None):
        """
        Do a put request.

        :param url: string
        :param data: a Dict. later converted to json.
        :return:
        """
        resp = None
        _json = None  # empty result
        _status = None
        try:
            with async_timeout.timeout(self._timeout, loop=self.loop):
                resp = yield from self.websession.put(url, json=data)
                _status = resp.status
                if _status == 200:
                    _json = yield from resp.json()
                else:
                    _LOGGER.error("Error %s on %s", resp.status, url)
        except ValueError:
            _LOGGER.error("Error parsing Json message")
        except (asyncio.TimeoutError, aiohttp.ClientError):
            _LOGGER.error("Client connection error")
        finally:
            if resp is not None:
                yield from resp.release()

        return _json, _status

    @asyncio.coroutine
    def delete(self, url: str, params: str = None):
        resp = None
        _status = False
        try:
            with async_timeout.timeout(self._timeout, loop=self.loop):
                resp = yield from self.websession.delete(url, params=params)
                _status = resp.status
                if resp.status in [200, 204]:
                    _LOGGER.debug("Delete responded with code %d", resp.status)
                else:
                    _LOGGER.error("Error %s on %s", resp.status, url)
        except (asyncio.TimeoutError, aiohttp.ClientError):
            _LOGGER.error("Client connection error")
        finally:
            if resp is not None:
                yield from resp.release()
        return _status
