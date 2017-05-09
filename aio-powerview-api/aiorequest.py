import asyncio
import json

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
    def get(self, url, params):
        data = None
        try:
            with async_timeout.timeout(self._timeout, loop=self.loop):
                response = yield from self.websession.get(url, params=params)

                if response.status == 200:
                    data = yield from response.json()

        except (asyncio.TimeoutError, aiohttp.ClientError) as error:
            _LOGGER.error('Failed to communicate with IP Webcam: %s', error)
            return

        return data

        # @asyncio.coroutine
        # def post(self,url,data):
        #     data = json.dumps(data)
        #     try:
        #         with async_timeout(self._timeout,loop=self.loop):
        #             response =yield from self.websession.post()
