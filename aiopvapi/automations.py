"""Scenes class managing all scene data."""

import logging

from aiopvapi.helpers.aiorequest import AioRequest
from aiopvapi.helpers.api_base import ApiEntryPoint
from aiopvapi.helpers.constants import (
    ATTR_ID,
    ATTR_SCHEDULED_EVENT_DATA,
)
from aiopvapi.resources.automation import Automation

from aiopvapi.resources.model import PowerviewData

_LOGGER = logging.getLogger(__name__)


class Automations(ApiEntryPoint):
    """Powerview Automations"""

    def __init__(self, request: AioRequest) -> None:
        self.api_endpoint = "scheduledevents"
        if request.api_version >= 3:
            self.api_endpoint = "automations"
        super().__init__(request, self.api_endpoint)

    def _resource_factory(self, raw):
        return Automation(raw, self.request)

    def _loop_raw(self, raw):
        if self.api_version < 3:
            raw = raw[ATTR_SCHEDULED_EVENT_DATA]

        for _raw in raw:
            yield _raw

    def _get_to_actual_data(self, raw):
        if self.api_version >= 3:
            return raw
        return raw.get("scene")

    async def get_automations(self, fetch_scene_data: bool = True) -> PowerviewData:
        """Get a list of automations.

        :returns PowerviewData object
        :raises PvApiError when an error occurs.
        """
        resources = await self.get_resources()
        if self.api_version < 3:
            resources = resources[ATTR_SCHEDULED_EVENT_DATA]

        processed = {entry[ATTR_ID]: Automation(entry, self.request) for entry in resources}

        if fetch_scene_data is True:
            for automation in processed.values():
                await automation.fetch_associated_scene_data()

        _LOGGER.debug("Raw automation data: %s", resources)
        return PowerviewData(raw=resources, processed=processed)
