from audioop import avg
import logging
from collections import namedtuple
from dataclasses import dataclass

from aiopvapi.helpers.aiorequest import AioRequest
from aiopvapi.helpers.api_base import ApiResource
from aiopvapi.helpers.tools import join_path
from aiopvapi.helpers.constants import (
    ATTR_CAPABILITIES,
    ATTR_POSITION_DATA,
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
    ATTR_POSITION,
    ATTR_COMMAND,
    ATTR_MOVE,
    ATTR_TILT,
    ATTR_BATTERY_KIND,
    ATTR_POWER_TYPE,
    MAX_POSITION,
    MID_POSITION,
    MIN_POSITION,
    MAX_POSITION_V2,
    POSKIND_PRIMARY,
    POSKIND_SECONDARY,
    POSKIND_VANE,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class ShadeCapabilities:
    """Represents the capabilities available for shade."""

    primary: bool = False
    secondary: bool = False
    tilt90: bool = False
    tilt180: bool = False
    tiltOnClosed: bool = False
    tiltAnywhere: bool = False
    tiltOnSecondaryClosed: bool = False
    primaryInverted: bool = False
    secondaryInverted: bool = False
    secondaryOverlapped: bool = False
    vertical: bool = False


@dataclass
class ShadeLimits:
    """Represents the limits of a shade."""

    primary_min: int = MIN_POSITION
    primary_max: int = MAX_POSITION
    secondary_min: int = MIN_POSITION
    secondary_max: int = MAX_POSITION
    tilt_min: int = MIN_POSITION
    tilt_max: int = MAX_POSITION


shade_type = namedtuple("shade_type", ["shade_type", "description"])
capability = namedtuple("capability", ["type", "capabilities", "description"])


def factory(raw_data, request):
    """Class factory to create different types of shades
    depending on shade type."""

    if ATTR_SHADE in raw_data:
        raw_data = raw_data.get(ATTR_SHADE)

    shade_type = raw_data.get(ATTR_TYPE)

    def find_type(shade):
        for tp in shade.shade_types:
            if tp.shade_type == shade_type:
                return shade(raw_data, tp, request)
        return None

    shade_capability = raw_data.get(ATTR_CAPABILITIES)

    def find_capability(shade):
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


class BaseShade(ApiResource):
    api_path = "shades"
    shade_types = (shade_type(0, "undefined type"),)
    capability = capability("-1", ShadeCapabilities(primary=True), "undefined")
    _open_position = {ATTR_PRIMARY: MAX_POSITION}
    _close_position = {ATTR_PRIMARY: MIN_POSITION}
    _open_position_tilt = {}
    _close_position_tilt = {}
    allowed_positions = ()

    shade_limits = ShadeLimits()

    def __init__(self, raw_data: dict, shade_type: shade_type, request: AioRequest):
        self.shade_type = shade_type

        super().__init__(request, self.api_path, raw_data=raw_data)

    @property
    def open_position(self):
        return self.convert_to_v2(self._open_position)

    @property
    def close_position(self):
        return self.convert_to_v2(self._close_position)

    @property
    def open_position_tilt(self):
        return self.convert_to_v2(self._open_position_tilt)

    @property
    def close_position_tilt(self):
        return self.convert_to_v2(self._close_position_tilt)

    def convert_to_v2(self, attrs: dict):
        if self.request.api_version >= 3:
            return attrs

        result = {}
        # Start with position 1
        position = ATTR_POSITION1
        kind = ATTR_POSKIND1
        for key, val in attrs.items():
            val = int(val * MAX_POSITION_V2)
            if key == ATTR_PRIMARY:
                result[position] = val
                result[kind] = 1
            elif key == ATTR_SECONDARY:
                # Secondary is always in position 2
                result[ATTR_POSITION2] = val
                result[ATTR_POSKIND2] = 2
            elif key == ATTR_TILT:
                result[position] = val
                result[kind] = 3
            else:
                result[key] = val
            # Advance positions for next iteration
            position = ATTR_POSITION2
            kind = ATTR_POSKIND2
        return result

    def _create_shade_data(self, position_data=None, room_id=None):
        """Create a shade data object to be sent to the hub"""
        if self.request.api_version >= 3:
            return {"positions": self.clamp_v3(position_data)}

        base = {ATTR_SHADE: {ATTR_ID: self.id}}
        if position_data:
            base[ATTR_SHADE][ATTR_POSITION_DATA] = self.clamp_v2(position_data)
        if room_id:
            base[ATTR_SHADE][ATTR_ROOM_ID] = room_id
        return base

    async def _move(self, position_data):
        params = {}
        base_path = self._resource_path
        if self.request.api_version >= 3:
            # IDs are required in request params for gen 3.
            params = {"ids": self.id}
            base_path = self._base_path
        result = await self.request.put(
            f"{base_path}/positions", data=position_data, params=params
        )
        return result

    async def move(self, position_data):
        _LOGGER.debug("Shade %s move to: %s", self.name, position_data)
        data = self._create_shade_data(position_data=position_data)
        return await self._move(data)

    async def open(self):
        return await self.move(position_data=self.open_position)

    async def close(self):
        return await self.move(position_data=self.close_position)

    def position_limit(self, value, poskind):
        if poskind == POSKIND_PRIMARY:
            min = self.shade_limits.primary_min
            max = self.shade_limits.primary_max
        elif poskind == POSKIND_SECONDARY:
            min = self.shade_limits.secondary_min
            max = self.shade_limits.secondary_max
        elif poskind == POSKIND_VANE:
            min = self.shade_limits.tilt_min
            max = self.shade_limits.tilt_max
        if min <= value <= max:
            return value
        if value < min:
            return min
        else:
            return max

    def clamp_v2(self, position_data):
        """Prevent impossible positions being sent."""
        if (position1 := position_data.get(ATTR_POSITION1)) is not None:
            position_data[ATTR_POSITION1] = self.position_limit(
                position1, position_data[ATTR_POSKIND1]
            )
        if (position2 := position_data.get(ATTR_POSITION2)) is not None:
            position_data[ATTR_POSITION2] = self.position_limit(
                position2, position_data[ATTR_POSKIND2]
            )
        return position_data

    def clamp_v3(self, position_data):
        """Prevent impossible positions being sent."""
        for key, val in position_data.items():
            position_data[key] = self.position_limit(val, POSKIND_PRIMARY)
        return position_data

    async def _motion(self, motion):
        if self.request.api_version >= 3:
            path = self._resource_path + "/motion"
            cmd = {"motion": motion}
        else:
            path = self._resource_path
            cmd = {"shade": {"motion": motion}}
        await self.request.put(path, cmd)

    async def jog(self):
        """Jog the shade."""
        await self._motion("jog")

    async def calibrate(self):
        """Calibrate the shade."""
        await self._motion("calibrate")

    async def favorite(self):
        """Move the shade to the defined favorite position."""
        await self._motion("heart")

    async def stop(self):
        """Stop the shade."""
        if self.request.api_version >= 3:
            await self.request.put(
                join_path(self._base_path, "stop"), params={"ids": self.id}
            )
        else:
            await self._motion("stop")

    async def add_shade_to_room(self, room_id):
        data = self._create_shade_data(room_id=room_id)
        return await self.request.put(self._resource_path, data)

    async def refresh(self):
        """Query the hub and the actual shade to get the most recent shade
        data. Including current shade position."""
        raw_data = await self.request.get(self._resource_path, {"refresh": "true"})
        if isinstance(raw_data, bool):
            _LOGGER.debug(
                "No data available, hub undergoing maintenance. Please try again"
            )
            return
        # Gen <= 2 API has raw data under shade key.  Gen >= 3 API this is flattened.
        self._raw_data = raw_data.get(ATTR_SHADE, raw_data)

    async def refresh_battery(self):
        """Query the hub and request the most recent battery state."""
        raw_data = await self.request.get(
            self._resource_path, {"updateBatteryLevel": "true"}
        )
        if isinstance(raw_data, bool):
            _LOGGER.debug(
                "No data available, hub undergoing maintenance. Please try again"
            )
            return
        self._raw_data = raw_data.get(ATTR_SHADE, raw_data)

    def get_power_source(self):
        """Get from the hub the type of power source."""
        attr = ATTR_POWER_TYPE if self.request.api_version >= 3 else ATTR_BATTERY_KIND
        return self.raw_data.get(attr)

    async def set_power_source(self, type):
        """Update the hub with the type of power source."""
        if type not in [1, 2, 3]:
            _LOGGER.error("Unsupported Power Type. Accepted values are 1, 2 & 3")
            return
        await self.request.put(
            self._resource_path, data={"shade": {"batteryKind": type}}
        )

    async def get_current_position(self, refresh=True) -> dict:
        """Return the current shade position.

        :param refresh: If True it queries the hub for the latest info.
        :return: Dictionary with position data.
        """
        if refresh:
            await self.refresh()
        position = self._raw_data.get(ATTR_POSITION_DATA)
        return position


class BaseShadeTilt(BaseShade):
    """A shade with move and tilt at bottom capabilities."""

    # even for shades that can 180° tilt, this would just result in
    # two closed positions. 90° will always be the open position
    _open_position_tilt = {ATTR_TILT: MID_POSITION}
    _close_position_tilt = {ATTR_TILT: MIN_POSITION}

    async def tilt(self, position_data):
        data = self._create_shade_data(position_data=position_data)
        return await self._move(data)

    async def tilt_open(self):
        """Tilt to close position."""
        return await self.tilt(position_data=self.open_position_tilt)

    async def tilt_close(self):
        """Tilt to close position"""
        return await self.tilt(position_data=self.close_position_tilt)


class ShadeBottomUp(BaseShade):
    """Type 0 - Up Down Only.

    A simple open/close shade.
    """

    shade_types = (
        shade_type(1, "Designer Roller"),
        shade_type(4, "Roman"),
        shade_type(5, "Bottom Up"),
        shade_type(6, "Duette"),
        shade_type(10, "Duette and Applause SkyLift"),
        shade_type(31, "Vignette"),
        shade_type(32, "Vignette"),
        shade_type(42, "M25T Roller Blind"),
        shade_type(49, "AC Roller"),
        shade_type(84, "Vignette"),
    )

    capability = capability(
        0,
        ShadeCapabilities(
            primary=True,
        ),
        "Bottom Up",
    )

    _open_position = {ATTR_PRIMARY: MAX_POSITION}
    _close_position = {ATTR_PRIMARY: MIN_POSITION}

    allowed_positions = ({ATTR_POSITION: {ATTR_POSKIND1: 1}, ATTR_COMMAND: ATTR_MOVE},)


class ShadeBottomUpTiltOnClosed180(BaseShadeTilt):
    """Type 0 - Up Down tiltOnClosed 180°.

    A shade with move and tilt at when closed capabilities.
    These are believed to be an oversight by the HD Powerview team and the
    only model without a distinct capability code.
    """

    shade_types = (shade_type(44, "Twist"),)

    # via json these have capability 0
    # overriding to 1 to trick HA into providing tilt functionality
    # only difference is these have 180 tilt
    capability = capability(
        1,
        ShadeCapabilities(
            primary=True,
            tiltOnClosed=True,
            tilt180=True,
        ),
        "Bottom Up Tilt 180°",
    )

    _open_position = {ATTR_PRIMARY: MAX_POSITION}
    _close_position = {ATTR_PRIMARY: MIN_POSITION}

    _open_position_tilt = {ATTR_TILT: MID_POSITION}
    _close_position_tilt = {ATTR_TILT: MIN_POSITION}

    allowed_positions = (
        {ATTR_POSITION: {ATTR_POSKIND1: 1}, ATTR_COMMAND: ATTR_MOVE},
        {ATTR_POSITION: {ATTR_POSKIND1: 3}, ATTR_COMMAND: ATTR_TILT},
    )


class ShadeBottomUpTiltOnClosed90(BaseShadeTilt):
    """Type 1 - Up Down tiltOnClosed 90°.

    A shade with move and tilt at bottom capabilities with only a 90° tilt.
    """

    shade_types = (
        shade_type(18, "Pirouette"),
        shade_type(23, "Silhouette"),
        shade_type(43, "Facette"),
    )

    capability = capability(
        1,
        ShadeCapabilities(
            primary=True,
            tiltOnClosed=True,
            tilt90=True,
        ),
        "Bottom Up Tilt 90°",
    )

    shade_limits = ShadeLimits(tilt_max=MID_POSITION)

    _open_position = {ATTR_PRIMARY: MAX_POSITION}
    _close_position = {ATTR_PRIMARY: MIN_POSITION}

    _open_position_tilt = {ATTR_TILT: MID_POSITION}
    _close_position_tilt = {ATTR_TILT: MIN_POSITION}

    allowed_positions = (
        {ATTR_POSITION: {ATTR_POSKIND1: 1}, ATTR_COMMAND: ATTR_MOVE},
        {ATTR_POSITION: {ATTR_POSKIND1: 3}, ATTR_COMMAND: ATTR_TILT},
    )


class ShadeBottomUpTiltAnywhere(BaseShadeTilt):
    """Type 2 - Up Down tiltAnywhere 180°.

    A shade with move and tilt anywhere capabilities.
    """

    shade_types = (
        shade_type(51, "Venetian, Tilt Anywhere"),
        shade_type(62, "Venetian, Tilt Anywhere"),
    )

    capability = capability(
        2,
        ShadeCapabilities(
            primary=True,
            tiltAnywhere=True,
            tilt180=True,
        ),
        "Bottom Up Tilt 180°",
    )

    _open_position = {
        ATTR_PRIMARY: MAX_POSITION,
        ATTR_TILT: MID_POSITION,
    }

    _close_position = {
        ATTR_PRIMARY: MIN_POSITION,
        ATTR_TILT: MIN_POSITION,
    }

    _open_position_tilt = {ATTR_TILT: MID_POSITION}
    _close_position_tilt = {ATTR_TILT: MIN_POSITION}

    allowed_positions = (
        {ATTR_POSITION: {ATTR_POSKIND1: 1, ATTR_POSKIND2: 3}, ATTR_COMMAND: ATTR_MOVE},
        {ATTR_POSITION: {ATTR_POSKIND1: 3}, ATTR_COMMAND: ATTR_TILT},
    )


class ShadeVertical(ShadeBottomUp):
    """Type 3 - Vertical Open Close

    A vertical shade with open/close only
    Same capabilities as type 0 (no tilt) but vertical.
    """

    shade_types = (
        shade_type(26, "Skyline Panel, Left Stack"),
        shade_type(27, "Skyline Panel, Right Stack"),
        shade_type(28, "Skyline Panel, Split Stack"),
        shade_type(69, "Curtain, Left Stack"),
        shade_type(70, "Curtain, Right Stack"),
        shade_type(71, "Curtain, Split Stack"),
    )

    capability = capability(
        3,
        ShadeCapabilities(
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
        shade_type(54, "Vertical Slats, Left Stack"),
        shade_type(55, "Vertical Slats, Right Stack"),
        shade_type(56, "Vertical Slats, Split Stack"),
    )

    capability = capability(
        4,
        ShadeCapabilities(
            primary=True,
            tiltAnywhere=True,
            tilt180=True,
            vertical=True,
        ),
        "Vertical Tilt Anywhere",
    )


class ShadeTiltOnly(BaseShadeTilt):
    """Type 5 - Tilt Only 180°

    A shade with tilt anywhere capabilities only.
    """

    shade_types = (shade_type(66, "Palm Beach Shutters"),)

    capability = capability(
        5,
        ShadeCapabilities(
            tiltAnywhere=True,
            tilt180=True,
        ),
        "Tilt Only 180°",
    )

    _open_position = {}
    _close_position = {}

    _open_position_tilt = {ATTR_TILT: MID_POSITION}
    _close_position_tilt = {ATTR_TILT: MIN_POSITION}

    allowed_positions = ({ATTR_POSITION: {ATTR_POSKIND1: 3}, ATTR_COMMAND: ATTR_TILT},)

    async def move(self):
        _LOGGER.error("Move not supported.")
        return


class ShadeTopDown(BaseShade):
    """Type 6 - Top Down Only

    A shade with top down capabilities only.
    """

    shade_types = (shade_type(7, "Top Down"),)

    capability = capability(
        6,
        ShadeCapabilities(
            primary=True,
            primaryInverted=True,
        ),
        "Top Down",
    )

    _open_position = {ATTR_PRIMARY: MIN_POSITION}
    _close_position = {ATTR_PRIMARY: MAX_POSITION}

    allowed_positions = ({ATTR_POSITION: {ATTR_POSKIND1: 1}, ATTR_COMMAND: ATTR_MOVE},)


class ShadeTopDownBottomUp(BaseShade):
    """Type 7 - Top Down Bottom Up

    A shade with top down bottom up capabilities.
    """

    shade_types = (
        shade_type(8, "Duette, Top Down Bottom Up"),
        shade_type(9, "Duette DuoLite, Top Down Bottom Up"),
        shade_type(33, "Duette Architella, Top Down Bottom Up"),
        shade_type(47, "Pleated, Top Down Bottom Up"),
    )

    capability = capability(
        7,
        ShadeCapabilities(
            primary=True,
            secondary=True,
        ),
        "Top Down Bottom Up",
    )

    _open_position = {
        ATTR_PRIMARY: MAX_POSITION,
        ATTR_SECONDARY: MIN_POSITION,
    }

    _close_position = {
        ATTR_PRIMARY: MIN_POSITION,
        ATTR_SECONDARY: MIN_POSITION,
    }

    allowed_positions = (
        {ATTR_POSITION: {ATTR_POSKIND1: 1, ATTR_POSKIND2: 2}, ATTR_COMMAND: ATTR_MOVE},
    )


class ShadeDualOverlapped(BaseShade):
    """Type 8 - Dual Shade Overlapped

    A shade with a front sheer and rear blackout shade.
    """

    shade_types = (
        shade_type(65, "Vignette Duolite"),
        shade_type(79, "Duolite Lift"),
    )

    capability = capability(
        8,
        ShadeCapabilities(
            primary=True,
            secondary=True,
            secondaryOverlapped=True,
        ),
        "Dual Shade Overlapped",
    )

    _open_position = {ATTR_PRIMARY: MAX_POSITION}
    _close_position = {ATTR_SECONDARY: MIN_POSITION}

    allowed_positions = (
        {ATTR_POSITION: {ATTR_POSKIND1: 1}, ATTR_COMMAND: ATTR_MOVE},
        {ATTR_POSITION: {ATTR_POSKIND1: 2}, ATTR_COMMAND: ATTR_MOVE},
    )


class ShadeDualOverlappedTilt90(BaseShadeTilt):
    """Type 9 - Dual Shade Overlapped with tiltOnClosed

    A shade with a front sheer and rear blackout shade.
    Tilt on these is unique in that it requires the rear shade open and front shade closed.
    """

    shade_types = (shade_type(38, "Silhouette Duolite"),)

    capability = capability(
        9,
        ShadeCapabilities(
            primary=True,
            secondary=True,
            secondaryOverlapped=True,
            tilt90=True,
            tiltOnClosed=True,
        ),
        "Dual Shade Overlapped Tilt 90°",
    )

    shade_limits = ShadeLimits(tilt_max=MID_POSITION)

    _open_position = {ATTR_PRIMARY: MAX_POSITION}
    _close_position = {ATTR_SECONDARY: MIN_POSITION}

    _open_position_tilt = {ATTR_TILT: MID_POSITION}
    _close_position_tilt = {ATTR_TILT: MIN_POSITION}

    allowed_positions = (
        {ATTR_POSITION: {ATTR_POSKIND1: 1}, ATTR_COMMAND: ATTR_MOVE},
        {ATTR_POSITION: {ATTR_POSKIND1: 2}, ATTR_COMMAND: ATTR_MOVE},
        {ATTR_POSITION: {ATTR_POSKIND1: 3}, ATTR_COMMAND: ATTR_TILT},
    )


class ShadeDualOverlappedTilt180(ShadeDualOverlappedTilt90):
    """Type 10 - Dual Shade Overlapped with tiltOnClosed

    A shade with a front sheer and rear blackout shade.
    Tilt on these is unique in that it requires the rear shade open and front shade closed.
    """

    shade_types = ()

    capability = capability(
        10,
        ShadeCapabilities(
            primary=True,
            secondary=True,
            secondaryOverlapped=True,
            tilt180=True,
            tiltOnClosed=True,
        ),
        "Dual Shade Overlapped Tilt 180°",
    )

    shade_limits = ShadeLimits(tilt_max=MAX_POSITION)
