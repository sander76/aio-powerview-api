"""Shade class managing all shade types."""

import logging
from dataclasses import dataclass
from typing import Any

from aiopvapi.helpers.aiorequest import AioRequest, PvApiMaintenance
from aiopvapi.helpers.api_base import ApiResource
from aiopvapi.helpers.tools import join_path
from aiopvapi.helpers.constants import (
    ATTR_CAPABILITIES,
    ATTR_POSITIONS,
    ATTR_SHADE,
    ATTR_TYPE,
    ATTR_ID,
    ATTR_ROOM_ID,
    ATTR_POSKIND1,
    ATTR_POSITION1,
    ATTR_POSITION2,
    ATTR_POSKIND2,
    ATTR_PRIMARY,
    ATTR_SECONDARY,
    ATTR_TILT,
    ATTR_BATTERY_KIND,
    ATTR_POWER_TYPE,
    FIRMWARE,
    FIRMWARE_REVISION,
    FIRMWARE_SUB_REVISION,
    FIRMWARE_BUILD,
    MAX_POSITION,
    MID_POSITION,
    MIN_POSITION,
    MAX_POSITION_V2,
    MOTION_STOP,
    POSKIND_PRIMARY,
    POSKIND_SECONDARY,
    POSKIND_TILT,
    ATTR_SIGNAL_STRENGTH,
    ATTR_SIGNAL_STRENGTH_MAX,
    POWERTYPE_BATTERY,
    POWERTYPE_HARDWIRED,
    POWERTYPE_MAP_V2,
    POWERTYPE_MAP_V3,
    POWERTYPE_RECHARGABLE,
    SHADE_BATTERY_STATUS,
    SHADE_BATTERY_STRENGTH,
    POSITIONS_V2,
    POSITIONS_V3,
    BATTERY_KIND_HARDWIRED,
    MOTION_VELOCITY,
    MOTION_JOG,
    MOTION_CALIBRATE,
    MOTION_FAVORITE,
    FUNCTION_SET_POWER,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class PowerviewCapabilities:
    """Capabilities available from Powerview."""

    primary: bool = False
    secondary: bool = False
    tilt_90: bool = False
    tilt_180: bool = False
    tilt_onclosed: bool = False
    tilt_anywhere: bool = False
    tilt_onsecondaryclosed: bool = False
    primary_inverted: bool = False
    secondary_inverted: bool = False
    secondary_overlapped: bool = False
    vertical: bool = False


@dataclass
class ShadeLimits:
    """Limits of a shade."""

    primary_min: int = MIN_POSITION
    primary_max: int = MAX_POSITION
    secondary_min: int = MIN_POSITION
    secondary_max: int = MAX_POSITION
    tilt_min: int = MIN_POSITION
    tilt_max: int = MAX_POSITION


@dataclass
class ShadePosition:
    """Positions for a powerview shade."""

    primary: int | float | None = None
    secondary: int | float | None = None
    tilt: int | float | None = None
    velocity: float | None = None  # float only a v3 only property


@dataclass
class ShadeType:
    """Shade information based on type and description"""

    type: int | str
    description: str


@dataclass
class ShadeCapability:
    """Shade capability information"""

    type: int | str
    capabilities: PowerviewCapabilities
    description: str


class BaseShade(ApiResource):
    """Basic shade class."""

    api_endpoint = "shades"

    shade_types: tuple[ShadeType] = (ShadeType(0, "undefined type"),)
    capability: ShadeCapability = ShadeCapability(
        "-1", PowerviewCapabilities(primary=True), "undefined"
    )
    _open_position: ShadePosition = ShadePosition(primary=MAX_POSITION)
    _close_position: ShadePosition = ShadePosition(primary=MIN_POSITION)
    _open_position_tilt: ShadePosition = ShadePosition()
    _close_position_tilt: ShadePosition = ShadePosition()

    shade_limits: ShadeLimits = ShadeLimits()

    def __init__(
        self, raw_data: dict, shade_type: ShadeType, request: AioRequest
    ) -> None:
        self.shade_type = shade_type
        super().__init__(request, self.api_endpoint, raw_data=raw_data)

    def is_supported(self, function: str) -> bool:
        """Return if api supports this function."""
        if self.api_version >= 3:
            return function in (MOTION_JOG, MOTION_VELOCITY, MOTION_STOP)
        elif self.api_version == 2:
            return function in (
                MOTION_JOG,
                MOTION_CALIBRATE,
                MOTION_FAVORITE,
                MOTION_STOP,
                FUNCTION_SET_POWER,
            )
        else:
            return function in (
                MOTION_JOG,
                MOTION_CALIBRATE,
                MOTION_FAVORITE,
                FUNCTION_SET_POWER,
            )

    @property
    def current_position(self) -> ShadePosition:
        """Return the current position of the shade as a percentage."""
        position = self.raw_to_structured(self._raw_data)
        position = self.get_additional_positions(position)
        return position

    @property
    def room_id(self) -> int:
        """Return the room id of the shade."""
        return self._raw_data.get(ATTR_ROOM_ID)

    @property
    def type_id(self) -> int:
        """Return the type id of the shade."""
        return self._raw_data.get(ATTR_TYPE)

    @property
    def type_name(self) -> str:
        """Return the type name of the shade."""
        for shade in self.shade_types:
            if shade.type == self.type_id:
                return shade.description
        return self.type_id

    @property
    def firmware(self) -> str | None:
        """Return firmware string for the shade."""
        if FIRMWARE not in self.raw_data:
            return None
        firmware = self.raw_data[FIRMWARE]
        return f"{firmware[FIRMWARE_REVISION]}.{firmware[FIRMWARE_SUB_REVISION]}.{firmware[FIRMWARE_BUILD]}"

    @property
    def url(self) -> str:
        """Return url for the shade."""
        return self._resource_path

    @property
    def open_position(self) -> ShadePosition:
        """Return the shade opened position"""
        return self._open_position

    @property
    def close_position(self) -> ShadePosition:
        """Return the shade closed position"""
        return self._close_position

    @property
    def open_position_tilt(self) -> ShadePosition:
        """Return the tilt opened position"""
        return self._open_position_tilt

    @property
    def close_position_tilt(self) -> ShadePosition:
        """Return the tilt closed position"""
        return self._close_position_tilt

    def percent_to_api(self, position: float, position_type: str) -> int | float:
        """Convert percentage based position to hunter douglas api position."""
        # get the possible maximum for the shade (some shades only allow 50% position)
        max_position_pct_mapping = {
            ATTR_PRIMARY: self.shade_limits.primary_max,
            ATTR_SECONDARY: self.shade_limits.secondary_max,
            ATTR_TILT: self.shade_limits.tilt_max,
        }

        max_position_pct = max_position_pct_mapping.get(position_type, 100)

        # ensure the position remains in range 0-100
        position = self.position_limit(position, position_type)

        # gen 3 takes 0.0 -> 1.0 (fractional perentage) - float
        if self.api_version >= 3:
            max_position_pct = max_position_pct / 100
            return round(position / 100 * max_position_pct, 2)

        # gen 2 requires conversion to 0-65335 - int
        max_position_pct = max_position_pct / 100 * MAX_POSITION_V2
        return int(position / 100 * max_position_pct)

    def api_to_percent(self, position: float, position_type: str) -> int:
        """Convert hunter douglas api based position to percentage based position."""
        # get the possible maximum for the shade (some shades only allow 50% position)
        max_position_pct_mapping = {
            ATTR_PRIMARY: self.shade_limits.primary_max,
            ATTR_SECONDARY: self.shade_limits.secondary_max,
            ATTR_TILT: self.shade_limits.tilt_max,
        }

        max_position_pct = max_position_pct_mapping.get(position_type, 100)

        # convert percentage based version of max positioning to api per version
        max_position_api = max_position_pct / 100
        if self.api_version < 3:
            max_position_api = MAX_POSITION_V2 * max_position_api

        percent = self.position_limit(round((position / max_position_api) * 100))
        return percent

    def structured_to_raw(self, data: ShadePosition) -> dict[str, Any]:
        """Convert structured ShadePosition to API relevant dict"""
        _LOGGER.debug("Structured Data %s: %s", self.name, data)

        if self.api_version >= 3:
            # Gen 3 raw data creation
            raw = {ATTR_POSITIONS: {}}
            for position_type in POSITIONS_V3:
                if getattr(data, position_type) is not None:
                    raw[ATTR_POSITIONS][position_type] = self.percent_to_api(
                        getattr(data, position_type), position_type
                    )

        else:
            # Gen 2 raw data creation
            position_data = {}
            if data.primary is not None:
                # primary is always in position 1
                position_data[ATTR_POSKIND1] = POSKIND_PRIMARY
                position_data[ATTR_POSITION1] = self.percent_to_api(
                    data.primary, ATTR_PRIMARY
                )
            if data.secondary is not None:
                poskind = ATTR_POSKIND2
                position = ATTR_POSITION2
                if data.primary is None:
                    # if no primary, secondary should be in position 1 (its a legacy thing)
                    poskind = ATTR_POSKIND1
                    position = ATTR_POSITION1
                position_data[poskind] = POSKIND_SECONDARY
                position_data[position] = self.percent_to_api(
                    data.secondary, ATTR_SECONDARY
                )
            if data.tilt is not None:
                if data.primary is not None and data.secondary is not None:
                    # if both primary and secondary exist than tilt cannot be sent
                    _LOGGER.debug(
                        "Legacy only accepts 2 positions. Tilt ignored %s", data
                    )
                elif data.primary is not None or data.secondary is not None:
                    # if primary or secondary exist move tilt to position 2 (its a legacy thing)
                    position_data[ATTR_POSKIND2] = POSKIND_TILT
                    position_data[ATTR_POSITION2] = self.percent_to_api(
                        data.tilt, ATTR_TILT
                    )
                else:
                    position_data[ATTR_POSKIND1] = POSKIND_TILT
                    position_data[ATTR_POSITION1] = self.percent_to_api(
                        data.tilt, ATTR_TILT
                    )

            raw = {ATTR_SHADE: {ATTR_ID: self.id, ATTR_POSITIONS: position_data}}

        _LOGGER.debug("Raw Conversion %s: %s", self.name, raw)
        return raw

    def raw_to_structured(self, shade_data: dict[int | str, Any]) -> ShadePosition:
        """Convert API dict info to structured ShadePosition dataclass"""
        _LOGGER.debug("Raw Data %s: %s", self.name, shade_data)

        if ATTR_POSITIONS not in shade_data:
            return ShadePosition()

        position_data = shade_data[ATTR_POSITIONS]

        position = ShadePosition()
        if self.api_version >= 3:
            for position_key in POSITIONS_V3:
                if position_key in position_data:
                    setattr(
                        position,
                        position_key,
                        self.api_to_percent(position_data[position_key], position_key),
                    )

        else:
            position_mapping = {
                POSKIND_PRIMARY: ATTR_PRIMARY,
                POSKIND_SECONDARY: ATTR_SECONDARY,
                POSKIND_TILT: ATTR_TILT,
            }

            for position_key, poskind_key in POSITIONS_V2:
                if poskind_key in position_data:
                    target_key = position_mapping.get(position_data[poskind_key])
                    setattr(
                        position,
                        target_key,
                        self.api_to_percent(position_data[position_key], target_key),
                    )

        _LOGGER.debug("Structured Conversion %s: %s", self.name, position)
        return position

    def _create_shade_data(self, position_data=None, room_id=None):
        """Create a shade data object to be sent to the hub"""
        if self.api_version >= 3:
            return {"positions": position_data}

        base = {ATTR_SHADE: {ATTR_ID: self.id}}
        if position_data:
            base[ATTR_SHADE][ATTR_POSITIONS] = position_data
        if room_id:
            base[ATTR_SHADE][ATTR_ROOM_ID] = room_id
        return base

    async def move_raw(self, position_data: dict):
        """Move the shade to a set position using raw data"""
        _LOGGER.debug("Shade %s move to: %s", self.name, position_data)
        data = self._create_shade_data(position_data=position_data)
        return await self._move(data)

    async def _move(self, position_data: dict):
        params = {}
        resource_path = self._resource_path
        if self.api_version >= 3:
            # IDs are required in request params for gen 3.
            params = {"ids": self.id}
            resource_path = join_path(self.base_path, "positions")
        result = await self.request.put(
            resource_path, data=position_data, params=params
        )
        return result

    async def move(self, position_data: ShadePosition) -> ShadePosition:
        """Move the shade to a set position"""
        _LOGGER.debug("Shade %s move to: %s", self.name, position_data)
        data = self.structured_to_raw(position_data)
        await self._move(data)
        return self.current_position

    def get_additional_positions(self, positions: ShadePosition) -> ShadePosition:
        """Returns additonal positions not reported by the hub"""
        return positions

    async def open(self):
        """Open the shade"""
        return await self.move(position_data=self.open_position)

    async def close(self):
        """Close the shade"""
        return await self.move(position_data=self.close_position)

    def position_limit(self, position: int, position_type: str = ""):
        """Limit values that can be calculated."""
        # determine the absolute position for the particular shade
        limits = {
            ATTR_PRIMARY: (
                self.shade_limits.primary_min,
                self.shade_limits.primary_max,
            ),
            ATTR_SECONDARY: (
                self.shade_limits.secondary_min,
                self.shade_limits.secondary_max,
            ),
            ATTR_TILT: (self.shade_limits.tilt_min, self.shade_limits.tilt_max),
        }

        min_limit, max_limit = limits.get(position_type, (0, 100))

        return min(max(min_limit, position), max_limit)

    async def _motion(self, motion):
        if self.api_version >= 3:
            path = join_path(self._resource_path, "motion")
            cmd = {"motion": motion}
        else:
            path = self._resource_path
            cmd = {"shade": {"motion": motion}}
        await self.request.put(path, cmd)

    async def jog(self):
        """Jog the shade."""
        await self._motion(MOTION_JOG)

    async def calibrate(self):
        """Calibrate the shade."""
        await self._motion(MOTION_CALIBRATE)

    async def favorite(self):
        """Move the shade to the defined favorite position."""
        await self._motion(MOTION_FAVORITE)

    async def stop(self):
        """Stop the shade."""
        if not self.is_supported(MOTION_STOP):
            _LOGGER.error("Method not supported")
            return

        if self.api_version >= 3:
            await self.request.put(
                join_path(self.base_path, MOTION_STOP), params={"ids": self.id}
            )
        else:
            await self._motion(MOTION_STOP)

    async def add_shade_to_room(self, room_id):
        """Add shade to room."""
        data = self._create_shade_data(room_id=room_id)
        return await self.request.put(self._resource_path, data)

    async def refresh(self):
        """Query the hub and the actual shade to get the most recent shade
        data. Including current shade position."""
        try:
            _LOGGER.debug("Refreshing position of: %s", self.name)
            raw_data = await self.request.get(self._resource_path, {"refresh": "true"})
            # Gen <= 2 API has raw data under shade key.  Gen >= 3 API this is flattened.
            self._raw_data = raw_data.get(ATTR_SHADE, raw_data)
        except PvApiMaintenance:
            _LOGGER.debug("Hub undergoing maintenance. Please try again")
        return

    async def refresh_battery(self):
        """Query the hub and request the most recent battery state."""
        try:
            raw_data = await self.request.get(
                self._resource_path, {"updateBatteryLevel": "true"}
            )
            # Gen <= 2 API has raw data under shade key.  Gen >= 3 API this is flattened.
            self._raw_data = raw_data.get(ATTR_SHADE, raw_data)
        except PvApiMaintenance:
            _LOGGER.debug("Hub undergoing maintenance. Please try again")
        return

    def has_battery_info(self) -> bool:
        """Confirm if the shade has battery info."""
        if self.api_version >= 3:
            return bool(SHADE_BATTERY_STATUS in self.raw_data)
        return bool(SHADE_BATTERY_STRENGTH in self.raw_data)

    def is_battery_powered(self) -> bool:
        """Confirm if the shade is battery or hardwired."""
        attr = ATTR_POWER_TYPE if self.api_version >= 3 else ATTR_BATTERY_KIND
        return bool(self.raw_data.get(attr) != BATTERY_KIND_HARDWIRED)

    def supported_power_sources(self) -> list[str]:
        """List supported power sources."""
        return [POWERTYPE_HARDWIRED, POWERTYPE_BATTERY, POWERTYPE_RECHARGABLE]

    def get_power_source(self) -> str:
        """Get from the hub the type of power source."""
        version_map = POWERTYPE_MAP_V3 if self.api_version >= 3 else POWERTYPE_MAP_V2
        attr = ATTR_POWER_TYPE if self.api_version >= 3 else ATTR_BATTERY_KIND
        powertype_map = {v: k for k, v in version_map.items()}

        raw_num = self.raw_data.get(attr)
        battery_type = powertype_map.get(raw_num, None)
        _LOGGER.debug("Mapping power source %s to %s", raw_num, battery_type)
        return battery_type

    async def set_power_source(self, power_source):
        """Update the hub with the type of power source."""
        if not self.is_supported(FUNCTION_SET_POWER):
            _LOGGER.error("Method not supported")
            return

        if power_source not in (supported := self.supported_power_sources()):
            _LOGGER.error("Unsupported Power Source. Accepted values: %s", supported)
            return

        version_map = POWERTYPE_MAP_V3 if self.api_version >= 3 else POWERTYPE_MAP_V2
        attr = ATTR_POWER_TYPE if self.api_version >= 3 else ATTR_BATTERY_KIND
        await self.request.put(
            self._resource_path,
            data={"shade": {attr: version_map.get(power_source)}},
        )

    def get_battery_strength(self) -> int:
        """Get battery strength from raw_data and return as a percentage."""
        power_levels = {
            4: 100,  # 4 is hardwired
            3: 100,  # 3 = 100% to 51% power remaining
            2: 50,  # 2 = 50% to 21% power remaining
            1: 20,  # 1 = 20% or less power remaining
            0: 0,  # 0 = No power remaining
        }
        battery_status = self.raw_data[SHADE_BATTERY_STATUS]
        return power_levels.get(battery_status, 0)

    def has_signal_strength(self) -> bool:
        """Confirm if the shade has signal data."""
        return bool(ATTR_SIGNAL_STRENGTH in self.raw_data)

    def get_signal_strength(self) -> int | str:
        """Get signal strength from raw_data.

        :v3 is RSSI
        :v2 is calculated as a percentage
        """
        if self.api_version >= 3:
            return self.raw_data[ATTR_SIGNAL_STRENGTH]
        return round(
            self.raw_data[ATTR_SIGNAL_STRENGTH] / ATTR_SIGNAL_STRENGTH_MAX * 100
        )

    async def get_current_position_raw(self, refresh=True) -> dict:
        """Return the current shade position.

        :param refresh: If True it queries the hub for the latest info.
        :return: Dictionary with position data.
        """
        if refresh:
            await self.refresh()
        position = self._raw_data.get(ATTR_POSITIONS)
        return position

    async def get_current_position(self, refresh=True) -> ShadePosition:
        """Return the current shade position.

        :param refresh: If True it queries the hub for the latest info.
        :return: Dictionary with position data.
        """
        await self.get_current_position_raw(refresh)
        return self.raw_to_structured(self._raw_data)


class BaseShadeTilt(BaseShade):
    """A shade with move and tilt at bottom capabilities."""

    # even for shades that can 180° tilt, this would just result in
    # two closed positions. 90° will always be the open position
    _open_position_tilt = ShadePosition(tilt=MID_POSITION)
    _close_position_tilt = ShadePosition(tilt=MIN_POSITION)

    async def tilt_raw(self, position_data):
        """Tilt the shade to a set position using raw data"""
        _LOGGER.debug("Shade %s tilt to: %s", self.name, position_data)
        data = self._create_shade_data(position_data=position_data)
        return await self._move(data)

    async def tilt(self, position_data: ShadePosition):
        """Tilt the shade to a set position"""
        _LOGGER.debug("Shade %s move to: %s", self.name, position_data)
        data = self.structured_to_raw(position_data)
        await self._move(data)
        return self.current_position

    async def tilt_open(self):
        """Tilt to close position."""
        return await self.tilt(position_data=self.open_position_tilt)

    async def tilt_close(self):
        """Tilt to close position"""
        return await self.tilt(position_data=self.close_position_tilt)

    def get_additional_positions(self, positions: ShadePosition) -> ShadePosition:
        """Returns additonal positions not reported by the hub"""
        if positions.primary and positions.tilt is None:
            positions.tilt = MIN_POSITION
        elif positions.tilt and positions.primary is None:
            positions.primary = MIN_POSITION
        return positions


class ShadeBottomUp(BaseShade):
    """Type 0 - Up Down Only.

    A simple open/close shade.
    """

    shade_types = (
        ShadeType(1, "Designer Roller"),
        ShadeType(4, "Roman"),
        ShadeType(5, "Bottom Up"),
        ShadeType(6, "Duette"),
        ShadeType(10, "Duette and Applause SkyLift"),
        ShadeType(31, "Vignette"),
        ShadeType(32, "Vignette"),
        ShadeType(42, "M25T Roller Blind"),
        ShadeType(49, "AC Roller"),
        ShadeType(52, "Banded Shades"),
        ShadeType(84, "Vignette"),
    )

    capability = ShadeCapability(
        0,
        PowerviewCapabilities(
            primary=True,
        ),
        "Bottom Up",
    )

    _open_position = ShadePosition(primary=MAX_POSITION)
    _close_position = ShadePosition(primary=MIN_POSITION)


class ShadeBottomUpTiltOnClosed180(BaseShadeTilt):
    """Type 0 - Up Down tiltOnClosed 180°.

    A shade with move and tilt at when closed capabilities.
    These are believed to be an oversight by the HD Powerview team and the
    only model without a distinct capability code.
    """

    shade_types = (ShadeType(44, "Twist"),)

    # via json these have capability 0
    # overriding to 1 to trick HA into providing tilt functionality
    # only difference is these have 180 tilt
    capability = ShadeCapability(
        1,
        PowerviewCapabilities(
            primary=True,
            tilt_onclosed=True,
            tilt_180=True,
        ),
        "Bottom Up Tilt 180°",
    )

    _open_position = ShadePosition(primary=MAX_POSITION)
    _close_position = ShadePosition(primary=MIN_POSITION)

    _open_position_tilt = ShadePosition(tilt=MID_POSITION)
    _close_position_tilt = ShadePosition(tilt=MIN_POSITION)


class ShadeBottomUpTiltOnClosed90(BaseShadeTilt):
    """Type 1 - Up Down tiltOnClosed 90°.

    A shade with move and tilt at bottom capabilities with only a 90° tilt.
    """

    shade_types = (
        ShadeType(18, "Pirouette"),
        ShadeType(23, "Silhouette"),
        ShadeType(43, "Facette"),
    )

    capability = ShadeCapability(
        1,
        PowerviewCapabilities(
            primary=True,
            tilt_onclosed=True,
            tilt_90=True,
        ),
        "Bottom Up Tilt 90°",
    )

    shade_limits = ShadeLimits(tilt_max=MID_POSITION)

    _open_position = ShadePosition(primary=MAX_POSITION)
    _close_position = ShadePosition(primary=MIN_POSITION)

    _open_position_tilt = ShadePosition(tilt=MID_POSITION)
    _close_position_tilt = ShadePosition(tilt=MIN_POSITION)


class ShadeBottomUpTiltAnywhere(BaseShadeTilt):
    """Type 2 - Up Down tiltAnywhere 180°.

    A shade with move and tilt anywhere capabilities.
    """

    shade_types = (
        ShadeType(51, "Venetian, Tilt Anywhere"),
        ShadeType(62, "Venetian, Tilt Anywhere"),
    )

    capability = ShadeCapability(
        2,
        PowerviewCapabilities(
            primary=True,
            tilt_anywhere=True,
            tilt_180=True,
        ),
        "Bottom Up Tilt 180°",
    )

    _open_position = ShadePosition(primary=MAX_POSITION, tilt=MID_POSITION)
    _close_position = ShadePosition(primary=MIN_POSITION, tilt=MIN_POSITION)

    _open_position_tilt = ShadePosition(tilt=MID_POSITION)
    _close_position_tilt = ShadePosition(tilt=MIN_POSITION)


class ShadeVertical(ShadeBottomUp):
    """Type 3 - Vertical Open Close

    A vertical shade with open/close only
    Same capabilities as type 0 (no tilt) but vertical.
    """

    shade_types = (
        ShadeType(26, "Skyline Panel, Left Stack"),
        ShadeType(27, "Skyline Panel, Right Stack"),
        ShadeType(28, "Skyline Panel, Split Stack"),
        ShadeType(69, "Curtain, Left Stack"),
        ShadeType(70, "Curtain, Right Stack"),
        ShadeType(71, "Curtain, Split Stack"),
    )

    capability = ShadeCapability(
        3,
        PowerviewCapabilities(
            primary=True,
            vertical=True,
        ),
        "Vertical",
    )


class ShadeVerticalTiltAnywhere(ShadeBottomUpTiltAnywhere):
    """Type 4 - Vertical tiltAnywhere 180°

    A vertical shade with open/close and tilt anywhere
    Same capabilities as type 2 but vertical.
    """

    shade_types = (
        ShadeType(54, "Vertical Slats, Left Stack"),
        ShadeType(55, "Vertical Slats, Right Stack"),
        ShadeType(56, "Vertical Slats, Split Stack"),
    )

    capability = ShadeCapability(
        4,
        PowerviewCapabilities(
            primary=True,
            tilt_anywhere=True,
            tilt_180=True,
            vertical=True,
        ),
        "Vertical Tilt Anywhere",
    )


class ShadeTiltOnly(BaseShadeTilt):
    """Type 5 - Tilt Only 180°

    A shade with tilt anywhere capabilities only.
    """

    shade_types = (ShadeType(66, "Palm Beach Shutters"),)

    capability = ShadeCapability(
        5,
        PowerviewCapabilities(
            tilt_anywhere=True,
            tilt_180=True,
        ),
        "Tilt Only 180°",
    )

    _open_position = ShadePosition()
    _close_position = ShadePosition()

    _open_position_tilt = ShadePosition(tilt=MID_POSITION)
    _close_position_tilt = ShadePosition(tilt=MIN_POSITION)

    async def move(self, position_data=None):
        _LOGGER.error("Move unsupported. Position request(%s) ignored", position_data)
        return

    def get_additional_positions(self, positions: ShadePosition) -> ShadePosition:
        """Returns additonal positions not reported by the hub"""
        return positions


class ShadeTopDown(BaseShade):
    """Type 6 - Top Down Only

    A shade with top down capabilities only.
    """

    shade_types = (ShadeType(7, "Top Down"),)

    capability = ShadeCapability(
        6,
        PowerviewCapabilities(
            primary=True,
            primary_inverted=True,
        ),
        "Top Down",
    )

    _open_position = ShadePosition(primary=MIN_POSITION)
    _close_position = ShadePosition(primary=MAX_POSITION)


class ShadeTopDownBottomUp(BaseShade):
    """Type 7 - Top Down Bottom Up

    A shade with top down bottom up capabilities.
    """

    shade_types = (
        ShadeType(8, "Duette, Top Down Bottom Up"),
        ShadeType(9, "Duette DuoLite, Top Down Bottom Up"),
        ShadeType(33, "Duette Architella, Top Down Bottom Up"),
        ShadeType(47, "Pleated, Top Down Bottom Up"),
    )

    capability = ShadeCapability(
        7,
        PowerviewCapabilities(
            primary=True,
            secondary=True,
        ),
        "Top Down Bottom Up",
    )

    _open_position = ShadePosition(primary=MAX_POSITION, secondary=MIN_POSITION)
    _close_position = ShadePosition(primary=MIN_POSITION, secondary=MIN_POSITION)

    def get_additional_positions(self, positions: ShadePosition) -> ShadePosition:
        """Returns additonal positions not reported by the hub"""
        if positions.primary is None:
            positions.primary = MIN_POSITION
        if positions.secondary is None:
            positions.secondary = MIN_POSITION
        return positions


class ShadeDualOverlapped(BaseShade):
    """Type 8 - Dual Shade Overlapped

    A shade with a front sheer and rear blackout shade.
    """

    shade_types = (
        ShadeType(65, "Vignette Duolite"),
        ShadeType(79, "Duolite Lift"),
    )

    capability = ShadeCapability(
        8,
        PowerviewCapabilities(
            primary=True,
            secondary=True,
            secondary_overlapped=True,
        ),
        "Dual Shade Overlapped",
    )

    _open_position = ShadePosition(primary=MAX_POSITION)
    _close_position = ShadePosition(secondary=MIN_POSITION)

    def get_additional_positions(self, positions: ShadePosition) -> ShadePosition:
        """Returns additonal positions not reported by the hub"""
        if positions.primary:
            if positions.secondary is None:
                positions.secondary = MAX_POSITION
            if positions.tilt is None:
                positions.tilt = MIN_POSITION
        elif positions.secondary:
            if positions.primary is None:
                positions.primary = MIN_POSITION
            if positions.tilt is None:
                positions.tilt = MIN_POSITION
        elif positions.tilt:
            if positions.primary is None:
                positions.primary = MIN_POSITION
            if positions.secondary is None:
                positions.secondary = MAX_POSITION
        return positions


class ShadeDualOverlappedTilt90(BaseShadeTilt):
    """Type 9 - Dual Shade Overlapped with tiltOnClosed

    A shade with a front sheer and rear blackout shade.
    Tilt on these is unique in that it requires the rear shade open and front shade closed.
    """

    shade_types = (ShadeType(38, "Silhouette Duolite"),)

    capability = ShadeCapability(
        9,
        PowerviewCapabilities(
            primary=True,
            secondary=True,
            secondary_overlapped=True,
            tilt_90=True,
            tilt_onclosed=True,
        ),
        "Dual Shade Overlapped Tilt 90°",
    )

    shade_limits = ShadeLimits(tilt_max=MID_POSITION)

    _open_position = ShadePosition(primary=MAX_POSITION)
    _close_position = ShadePosition(secondary=MIN_POSITION)

    _open_position_tilt = ShadePosition(tilt=MID_POSITION)
    _close_position_tilt = ShadePosition(tilt=MIN_POSITION)

    def get_additional_positions(self, positions: ShadePosition) -> ShadePosition:
        """Returns additonal positions not reported by the hub"""
        if positions.primary:
            if positions.secondary is None:
                positions.secondary = MAX_POSITION
            if positions.tilt is None:
                positions.tilt = MIN_POSITION
        elif positions.secondary:
            if positions.primary is None:
                positions.primary = MIN_POSITION
            if positions.tilt is None:
                positions.tilt = MIN_POSITION
        elif positions.tilt:
            if positions.primary is None:
                positions.primary = MIN_POSITION
            if positions.secondary is None:
                positions.secondary = MAX_POSITION
        return positions


class ShadeDualOverlappedTilt180(ShadeDualOverlappedTilt90):
    """Type 10 - Dual Shade Overlapped with tiltOnClosed

    A shade with a front sheer and rear blackout shade.
    Tilt on these is unique in that it requires the rear shade open and front shade closed.
    """

    shade_types = ()

    capability = ShadeCapability(
        10,
        PowerviewCapabilities(
            primary=True,
            secondary=True,
            secondary_overlapped=True,
            tilt_180=True,
            tilt_onclosed=True,
        ),
        "Dual Shade Overlapped Tilt 180°",
    )

    shade_limits = ShadeLimits(tilt_max=MAX_POSITION)


def factory(raw_data: dict, request: AioRequest):
    """Class factory to create different types of shades
    depending on shade type."""

    if ATTR_SHADE in raw_data:
        raw_data = raw_data.get(ATTR_SHADE)

    raw_type = raw_data.get(ATTR_TYPE)

    def find_type(shade: BaseShade):
        for type_def in shade.shade_types:
            if type_def.type == raw_type:
                return shade(raw_data, type_def, request)
        return None

    shade_capability = raw_data.get(ATTR_CAPABILITIES)

    def find_capability(shade: BaseShade):
        if shade.capability.type == shade_capability:
            return shade(raw_data, shade, request)
        return None

    classes = [
        ShadeBottomUp,
        ShadeBottomUpTiltOnClosed90,
        ShadeBottomUpTiltOnClosed180,  # to ensure capability match order here is important
        ShadeBottomUpTiltAnywhere,
        ShadeVerticalTiltAnywhere,
        ShadeVertical,
        ShadeTiltOnly,
        ShadeTopDown,
        ShadeTopDownBottomUp,
        ShadeDualOverlapped,
        ShadeDualOverlappedTilt90,
        ShadeDualOverlappedTilt180,
    ]

    for cls in classes:
        # class check is more concise as we have tested positioning
        _shade = find_type(cls)
        if _shade:
            _LOGGER.debug("Match type       : %s - %s", _shade, raw_data)
            return _shade

    for cls in classes:
        # fallback to a capability check - this should future proof new shades
        # type 0 that contain tilt would not be caught here
        _shade = find_capability(cls)
        if _shade:
            _LOGGER.debug("Match capability : %s - %s", _shade, raw_data)
            return _shade

    _LOGGER.debug("Shade unmatched  : %s - %s", BaseShade, raw_data)
    return BaseShade(raw_data, BaseShade.shade_types[0], request)
