"""Scene class managing all scenes."""

import logging

from aiopvapi.helpers.aiorequest import AioRequest, PvApiMaintenance
from aiopvapi.helpers.api_base import ApiResource
from aiopvapi.helpers.constants import (
    ATTR_ID,
    ATTR_SCENE_ID,
    ATTR_SCHEDULED_EVENT,
    FUNCTION_SCHEDULE,
)
from aiopvapi.helpers.tools import get_base_path, join_path
from aiopvapi.resources.scene import Scene

_LOGGER = logging.getLogger(__name__)


class Automation(ApiResource):
    """Powerview Automation class."""

    def __init__(self, raw_data: dict, request: AioRequest) -> None:
        """Initialize the automation."""
        self.api_endpoint = "scheduledevents"
        if request.api_version >= 3:
            self.api_endpoint = "automations"
        super().__init__(request, self.api_endpoint, raw_data)
        self._name = None
        self._room_id = None
        self._scene: Scene = None

    def is_supported(self, function: str) -> bool:
        """Return if api supports this function."""
        if self.api_version >= 3:
            return False
        if function in FUNCTION_SCHEDULE:
            return True
        return False

    @property
    def enabled(self) -> bool:
        """Return the automation state."""
        return self._raw_data.get("enabled")

    @property
    def id(self) -> int:
        """Return the automation id."""
        return self._raw_data.get(ATTR_ID)

    @property
    def name(self) -> str:
        """Return the automation name."""
        if self._name is not None:
            return self._name
        return self._raw_data.get(ATTR_SCENE_ID)

    @property
    def scene_id(self) -> str:
        """Return the scene id of the automation."""
        return self._raw_data.get(ATTR_SCENE_ID)

    @property
    def room_id(self) -> int | None:
        """Return the room id of the automation."""
        return self._room_id

    def convert_to_12_hour(self, hour: int):
        """Convert 24 hour time to 12 hour."""
        if hour < 0 or hour > 24:
            _LOGGER.error("%s is not a valid 24 hour time", hour)
            return 0
        if hour == 0:
            return 12
        if 0 < hour <= 12:
            return hour
        return hour - 12

    def format_time(self, hour: int, minute: int):
        """Convert hour and minute to friendly text format."""
        meridiem = "AM" if hour < 12 else "PM"
        hour = hour % 12 if hour % 12 != 0 else 12

        if minute >= 60:
            hour += minute // 60
            minute %= 60

        hour = self.convert_to_12_hour(hour)
        return f"{hour}:{str(abs(minute)).zfill(2)} {meridiem}"

    def get_execution_time(self):
        """Return a friendly string, in the same format as hub.

        Indicates when the time the schedule will execute.
        """
        # {'id': 437, 'type': 14, 'enabled': False, 'days': 127, 'hour': 1, 'min': 0, 'bleId': 2, 'sceneId': 220, 'errorShd_Ids': []}
        # {'enabled': True, 'sceneId': 14067, 'daySunday': False, 'dayMonday': True, 'dayTuesday': True, 'dayWednesday': True, 'dayThursday': True, 'dayFriday': True, 'daySaturday': False, 'eventType': 0, 'hour': 7, 'minute': 0, 'id': 38971}

        if self.api_version >= 3:
            # 2 = Before sunrise, 10 = After sunrise
            # 6 = Before sunset, 14 = After sunset
            sunrise = [2, 10]
            valid_events = [2, 6, 10, 14]
        else:
            # - Sunrise = 1, Sunset = 2
            # before and after are caluclated by hour/minute
            sunrise = [1]
            valid_events = [1, 2]

        attr_type = "type" if self.api_version >= 3 else "eventType"
        attr_hour = "hour"
        attr_minute = "min" if self.api_version >= 3 else "minute"

        event_type = self.raw_data.get(attr_type)
        hour = self.raw_data.get(attr_hour)
        minute = self.raw_data.get(attr_minute)

        # event type 0 represents clock based for all generations
        if event_type == 0:
            return self.format_time(hour, minute)

        if event_type in valid_events:
            when = "Sunrise" if event_type in sunrise else "Sunset"

            if hour == 0 and minute == 0:
                return f"At {when}"

            if self.api_version >= 3:
                before_after = "Before" if event_type in [2, 6] else "After"
            else:
                before_after = "Before" if minute < 0 else "After"
                hour = abs(minute) // 60
                minute = abs(minute) % 60
                # hour = floor(abs(minute) / 60)
                # minute = abs(minute) - (hour * 60)
            return f"{hour}h {minute}m {before_after} {when}"
            # return f"{abs(hour)}h {abs(minute)}m {before_after} {when}"

        return f"Unknown Event {event_type}"

    def get_execution_days(self):
        """Return a friendly string, in the same format as hub.

        Indicates when the days the schedule will execute.
        """

        if self.api_version >= 3:
            day_mapping = {
                0x40: "Sun",
                0x01: "Mon",
                0x02: "Tue",
                0x04: "Wed",
                0x08: "Thu",
                0x10: "Fri",
                0x20: "Sat",
            }

            enabled_days = [
                day for bit, day in day_mapping.items() if self.raw_data["days"] & bit
            ]

        else:
            day_mapping = {
                "daySunday": "Sun",
                "dayMonday": "Mon",
                "dayTuesday": "Tue",
                "dayWednesday": "Wed",
                "dayThursday": "Thu",
                "dayFriday": "Fri",
                "daySaturday": "Sat",
            }

            enabled_days = [
                day_mapping[key]
                for key, value in self.raw_data.items()
                if key in day_mapping and value
            ]

        if len(enabled_days) == len(day_mapping):
            output = "Every Day"
        elif set(enabled_days) == {"Sat", "Sun"}:
            output = "Weekends"
        elif set(enabled_days) == {"Mon", "Tue", "Wed", "Thu", "Fri"}:
            output = "Weekdays"
        else:
            output = ", ".join(enabled_days)
        return output

    @property
    def details(self) -> dict[str, str]:
        """Return the specifics of the automation."""
        details = {
            "ID": self.id,
            "Time": self.get_execution_time(),
            "Days": self.get_execution_days(),
        }

        _LOGGER.debug(
            "Automation: %s (Enabled: %s), %s, %s",
            self.name,
            self.enabled,
            details.get("Time"),
            details.get("Days"),
        )
        return details

    async def fetch_associated_scene_data(self) -> None:
        """Update the automation with friendly scene info."""
        scene_url = join_path(
            get_base_path(self.request.hub_ip, self.api_path),
            "scenes",
            str(self.scene_id),
        )
        self._scene: Scene = Scene(
            await self.request.get(scene_url),
            self.request,
        )
        self._name = self._scene.name
        self._room_id = self._scene.room_id

    async def set_state(self, state: bool) -> None:
        """Update the automation enabled status."""
        resource_path = join_path(self.base_path, str(self.id))
        data = self.raw_data
        data["enabled"] = state
        if self.api_version <= 2:
            data = {"scheduledEvent": data}
        await self.request.put(resource_path, data)

    async def refresh(self):
        """Query the hub and for updated automation information."""
        try:
            raw_data = await self.request.get(self._resource_path)
            # Gen <= 2 API has raw data under shade key.  Gen >= 3 API this is flattened.
            self._raw_data = raw_data.get(ATTR_SCHEDULED_EVENT, raw_data)
        except PvApiMaintenance:
            _LOGGER.debug("Hub undergoing maintenance. Please try again")
