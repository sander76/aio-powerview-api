from audioop import avg
import logging
from collections import namedtuple
from dataclasses import dataclass

from aiopvapi.helpers.aiorequest import AioRequest
from aiopvapi.helpers.api_base import ApiResource
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
    ATTR_POSITION,
    ATTR_COMMAND,
    ATTR_MOVE,
    ATTR_TILT,
    MAX_POSITION,
    MID_POSITION,
    MIN_POSITION,
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
        ShadeBottomUpTiltOnClosed180, #to ensure capability match order here is important
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
    api_path = "api/shades"
    shade_types = (shade_type(0, "undefined type"),)
    capability = capability("-1", ShadeCapabilities(primary=True), "undefined")
    open_position = {ATTR_POSITION1: MAX_POSITION, ATTR_POSKIND1: 1}
    close_position = {ATTR_POSITION1: MIN_POSITION, ATTR_POSKIND1: 1}
    open_position_tilt = {}
    close_position_tilt = {}
    allowed_positions = ()

    shade_limits = ShadeLimits()

    def __init__(self, raw_data: dict, shade_type: shade_type, request: AioRequest):
        self.shade_type = shade_type
        super().__init__(request, self.api_path, raw_data)

    def _create_shade_data(self, position_data=None, room_id=None):
        """Create a shade data object to be sent to the hub"""
        base = {ATTR_SHADE: {ATTR_ID: self.id}}
        if position_data:
            base[ATTR_SHADE][ATTR_POSITION_DATA] = self.clamp(position_data)
        if room_id:
            base[ATTR_SHADE][ATTR_ROOM_ID] = room_id
        return base

    async def _move(self, position_data):
        result = await self.request.put(self._resource_path, data=position_data)
        return result

    async def move(self, position_data):
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

    def clamp(self, position_data):
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

    async def jog(self):
        """Jog the shade."""
        await self.request.put(self._resource_path, {"shade": {"motion": "jog"}})

    async def calibrate(self):
        """Calibrate the shade."""
        await self.request.put(self._resource_path, {"shade": {"motion": "calibrate"}})

    async def favourite(self):
        """Move the shade to the defined favourite position."""
        await self.request.put(self._resource_path, {"shade": {"motion": "heart"}})

    async def stop(self):
        """Stop the shade."""
        return await self.request.put(self._resource_path, {"shade": {"motion": "stop"}})

    async def add_shade_to_room(self, room_id):
        data = self._create_shade_data(room_id=room_id)
        return await self.request.put(self._resource_path, data)

    async def refresh(self):
        """Query the hub and the actual shade to get the most recent shade
        data. Including current shade position."""
        raw_data = await self.request.get(self._resource_path, {"refresh": "true"})

        self._raw_data = raw_data[ATTR_SHADE]

    async def refresh_battery(self):
        """Query the hub and request the most recent battery state."""
        raw_data = await self.request.get(self._resource_path, {"updateBatteryLevel": "true"})

        self._raw_data = raw_data[ATTR_SHADE]

    async def set_power_source(self, type):
        """Update the hub with the type of power source."""
        if type not in [1, 2, 3]:
            _LOGGER.error("Unsupported Power Type. Accepted values are 1, 2 & 3")
            return
        await self.request.put(self._resource_path, data={"shade": {"batteryKind": type}})

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
    open_position_tilt = {ATTR_POSITION1: MID_POSITION, ATTR_POSKIND1: 3}
    close_position_tilt = {ATTR_POSITION1: MIN_POSITION, ATTR_POSKIND1: 3}

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
        shade_type(31, "Vignette"),
        shade_type(42, "M25T Roller Blind"),
        shade_type(49, "AC Roller"),
    )

    capability = capability(
        0,
        ShadeCapabilities(
            primary=True,
        ),
        "Bottom Up",
    )

    open_position = {ATTR_POSITION1: MAX_POSITION, ATTR_POSKIND1: 1}
    close_position = {ATTR_POSITION1: MIN_POSITION, ATTR_POSKIND1: 1}

    allowed_positions = (
        {ATTR_POSITION: {ATTR_POSKIND1: 1}, ATTR_COMMAND: ATTR_MOVE},
    )


class ShadeBottomUpTiltOnClosed180(BaseShadeTilt):
    """Type 0 - Up Down tiltOnClosed 180°.

    A shade with move and tilt at when closed capabilities.
    These are believed to be an oversight by the HD Powerview team and the
    only model without a distinct capability code.
    """

    shade_types = (
        shade_type(44, "Twist"),
    )

    capability = capability(
        1, #via json these have capability 0, setting 1 to trick HA into providing tilt functionality
        ShadeCapabilities(
            primary=True,
            tiltOnClosed=True,
            tilt180=True,
        ),
        "Bottom Up Tilt 180°",
    )

    open_position = {ATTR_POSITION1: MAX_POSITION, ATTR_POSKIND1: 1}
    close_position = {ATTR_POSITION1: MIN_POSITION, ATTR_POSKIND1: 1}

    open_position_tilt = {ATTR_POSITION1: MID_POSITION, ATTR_POSKIND1: 3}
    close_position_tilt = {ATTR_POSITION1: MIN_POSITION, ATTR_POSKIND1: 3}

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

    open_position = {ATTR_POSITION1: MAX_POSITION, ATTR_POSKIND1: 1}
    close_position = {ATTR_POSITION1: MIN_POSITION, ATTR_POSKIND1: 1}

    open_position_tilt = {ATTR_POSITION1: MID_POSITION, ATTR_POSKIND1: 3}
    close_position_tilt = {ATTR_POSITION1: MIN_POSITION, ATTR_POSKIND1: 3}

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

    open_position = {
        ATTR_POSKIND1: 1,
        ATTR_POSITION1: MAX_POSITION,
        ATTR_POSKIND2: 3,
        ATTR_POSITION2: MID_POSITION,
    }

    close_position = {
        ATTR_POSKIND1: 1,
        ATTR_POSITION1: MIN_POSITION,
        ATTR_POSKIND2: 3,
        ATTR_POSITION2: MIN_POSITION,
    }

    open_position_tilt = {ATTR_POSITION1: MID_POSITION, ATTR_POSKIND1: 3}
    close_position_tilt = {ATTR_POSITION1: MIN_POSITION, ATTR_POSKIND1: 3}

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
        shade_type(26, "Skyline, Left Stack"),
        shade_type(27, "Skyline, Right Stack"),
        shade_type(28, "Skyline, Split Stack"),
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

    shade_types = (
        shade_type(66, "Palm Beach Shutters"),
    )

    capability = capability(
        5,
        ShadeCapabilities(
            tiltAnywhere=True,
            tilt180=True,
        ),
        "Tilt Only 180°",
    )

    open_position = {}
    close_position = {}

    open_position_tilt = {ATTR_POSITION1: MID_POSITION, ATTR_POSKIND1: 3}
    close_position_tilt = {ATTR_POSITION1: MIN_POSITION, ATTR_POSKIND1: 3}

    allowed_positions = (
        {ATTR_POSITION: {ATTR_POSKIND1: 3}, ATTR_COMMAND: ATTR_TILT},
    )

    async def move(self):
        _LOGGER.error("Move not supported.")
        return


class ShadeTopDown(BaseShade):
    """Type 6 - Top Down Only

    A shade with top down capabilities only.
    """

    shade_types = (
        shade_type(7, "Top Down"),
    )

    capability = capability(
        6,
        ShadeCapabilities(
            primary=True,
            primaryInverted=True,
        ),
        "Top Down",
    )

    open_position = {ATTR_POSITION1: MIN_POSITION, ATTR_POSKIND1: 1}
    close_position = {ATTR_POSITION1: MAX_POSITION, ATTR_POSKIND1: 1}

    allowed_positions = (
        {ATTR_POSITION: {ATTR_POSKIND1: 1}, ATTR_COMMAND: ATTR_MOVE},
    )


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

    open_position = {
        ATTR_POSITION1: MAX_POSITION,
        ATTR_POSITION2: MIN_POSITION,
        ATTR_POSKIND1: 1,
        ATTR_POSKIND2: 2,
    }

    close_position = {
        ATTR_POSITION1: MIN_POSITION,
        ATTR_POSITION2: MIN_POSITION,
        ATTR_POSKIND1: 1,
        ATTR_POSKIND2: 2,
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

    open_position = {ATTR_POSITION1: MAX_POSITION, ATTR_POSKIND1: 1}
    close_position = {ATTR_POSITION1: MIN_POSITION, ATTR_POSKIND1: 2}

    allowed_positions = (
        {ATTR_POSITION: {ATTR_POSKIND1: 1}, ATTR_COMMAND: ATTR_MOVE},
        {ATTR_POSITION: {ATTR_POSKIND1: 2}, ATTR_COMMAND: ATTR_MOVE},
    )


class ShadeDualOverlappedTilt90(BaseShadeTilt):
    """Type 9 - Dual Shade Overlapped with tiltOnClosed

    A shade with a front sheer and rear blackout shade.
    Tilt on these is unique in that it requires the rear shade open and front shade closed.
    """

    shade_types = (
        shade_type(38, "Silhouette Duolite"),
    )

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

    open_position = {ATTR_POSITION1: MAX_POSITION, ATTR_POSKIND1: 1}
    close_position = {ATTR_POSITION1: MIN_POSITION, ATTR_POSKIND1: 2}

    open_position_tilt = {ATTR_POSITION2: MID_POSITION, ATTR_POSKIND1: 3}
    close_position_tilt = {ATTR_POSITION2: MIN_POSITION, ATTR_POSKIND1: 3}

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

    shade_types = (
    )

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
