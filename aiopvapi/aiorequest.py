import asyncio
import aiohttp
import async_timeout
import logging

_LOGGER = logging.getLogger(__name__)


class AioRequest:
    def __init__(self, loop, websession, timeout=10):
        self._timeout = timeout
        self.loop = loop
        self.websession = websession

    @asyncio.coroutine
    def get(self, url, params=None):
        data = None
        response = None
        try:
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
