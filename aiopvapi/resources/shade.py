import logging
from collections import namedtuple

from aiopvapi.helpers.aiorequest import AioRequest
from aiopvapi.helpers.api_base import ApiResource
from aiopvapi.helpers.constants import (
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
    MIN_POSITION,
    MAX_VANE,
)

_LOGGER = logging.getLogger(__name__)

shade_type = namedtuple("shade_type", ["shade_type", "description"])
capability = namedtuple("type", "functionality", "description")


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

    _shade = find_type(ShadeTdbu)
    if _shade:
        return _shade

    _shade = find_type(ShadeBottomUp)
    if _shade:
        return _shade

    _shade = find_type(ShadeBottomUpTilt)
    if _shade:
        return _shade

    _shade = find_type(ShadeBottomUpTiltAnywhere)
    if _shade:
        return _shade

    _shade = find_type(Silhouette)
    if _shade:
        return _shade

    return BaseShade(raw_data, BaseShade.shade_types[0], request)


class BaseShade(ApiResource):
    api_path = "api/shades"
    shade_types = (shade_type(0, "undefined type"),)
    capabilities = capability("-1", "undefined", "undefined")
    open_position = {ATTR_POSITION1: MAX_POSITION, ATTR_POSKIND1: 1}
    close_position = {ATTR_POSITION1: MIN_POSITION, ATTR_POSKIND1: 1}
    open_position_tilt = {}
    close_position_tilt = {}
    allowed_positions = ()

    can_move = True
    can_tilt = False

    def __init__(self, raw_data: dict, shade_type: shade_type, request: AioRequest):
        self.shade_type = shade_type
        super().__init__(request, self.api_path, raw_data)

    def _create_shade_data(self, position_data=None, room_id=None):
        """Create a shade data object to be sent to the hub"""
        base = {ATTR_SHADE: {ATTR_ID: self.id}}
        if position_data:
            base[ATTR_SHADE][ATTR_POSITION_DATA] = position_data
        if room_id:
            base[ATTR_SHADE][ATTR_ROOM_ID] = room_id
        return base

    async def _move(self, position_data):
        result = await self.request.put(self._resource_path, data=position_data)
        return result

    async def move(self, position_data):
        if self.can_move is False:
            _LOGGER.error("Move not supported.")
            return
        data = self._create_shade_data(position_data=position_data)
        return await self._move(data)

    async def tilt(self, position_data):
        if self.can_tilt is False:
            _LOGGER.error("Tilt not supported.")
            return
        data = self._create_shade_data(position_data=position_data)
        return await self._move(data)

    async def open(self):
        return await self.move(position_data=self.open_position)

    async def close(self):
        return await self.move(position_data=self.close_position)

    async def jog(self):
        """Jog the shade."""
        await self.request.put(self._resource_path, {"shade": {"motion": "jog"}})

    async def calibrate(self):
        """Calibrate the shade."""
        await self.request.put(self._resource_path, {"shade": {"motion": "calibrate"}})

    async def stop(self):
        """Stop the shade."""
        return await self.request.put(self._resource_path, {"shade": {"motion": "stop"}})

    async def tilt_open(self):
        """Tilt vanes to close position."""
        return await self.tilt(position_data=self.open_position_tilt)

    async def tilt_close(self):
        """Tilt vanes to close position"""
        return await self.tilt(position_data=self.close_position_tilt)

    async def add_shade_to_room(self, room_id):
        data = self._create_shade_data(room_id=room_id)
        return await self.request.put(self._resource_path, data)

    async def refresh(self):
        """Query the hub and the actual shade to get the most recent shade
        data. Including current shade position."""
        raw_data = await self.request.get(self._resource_path, {"refresh": "true"})

        self._raw_data = raw_data[ATTR_SHADE]

    async def refreshBattery(self):
        """Query the hub and request the most recent battery state."""
        raw_data = await self.request.get(self._resource_path, {"updateBatteryLevel": "true"})

        self._raw_data = raw_data[ATTR_SHADE]

    async def get_current_position(self, refresh=True) -> dict:
        """Return the current shade position.

        :param refresh: If True it queries the hub for the latest info.
        :return: Dictionary with position data.
        """
        if refresh:
            await self.refresh()
        position = self._raw_data.get(ATTR_POSITION_DATA)
        return position


class ShadeBottomUp(BaseShade):
    """A simple open/close shade."""
    shade_types = (
        shade_type(4, "Roman"),
        shade_type(5, "Bottom Up"),
        shade_type(6, "Duette"),
        shade_type(42, "M25T Roller Blind"),
        shade_type(49, "AC Roller"),
    )

    capabilities = capability(0, "Primary", "Bottom Up")

    open_position = {ATTR_POSITION1: MAX_POSITION, ATTR_POSKIND1: 1}
    close_position = {ATTR_POSITION1: MIN_POSITION, ATTR_POSKIND1: 1}

    allowed_positions = (
        {ATTR_POSITION: {ATTR_POSKIND1: 1}, ATTR_COMMAND: ATTR_MOVE},
    )


class ShadeBottomUpTilt(BaseShade):
    """A shade with move and tilt at bottom capabilities."""
    shade_types = (
        shade_type(44, "Twist"),
    )

    capabilities = capability(
        0, "Primary + TiltOnClosed + Tilt180", "Bottom Up Tilt 180°")

    can_tilt = True

    open_position = {ATTR_POSITION1: MAX_POSITION, ATTR_POSKIND1: 1}
    close_position = {ATTR_POSITION1: MIN_POSITION, ATTR_POSKIND1: 1}

    open_position_tilt = {ATTR_POSKIND1: 3, ATTR_POSITION1: MAX_POSITION}
    close_position_tilt = {ATTR_POSKIND1: 3, ATTR_POSITION1: MIN_POSITION}

    allowed_positions = (
        {ATTR_POSITION: {ATTR_POSKIND1: 1}, ATTR_COMMAND: ATTR_MOVE},
        {ATTR_POSITION: {ATTR_POSKIND1: 3}, ATTR_COMMAND: ATTR_TILT},
    )


class Silhouette(ShadeBottomUpTilt):
    """A shade with move and tilt at bottom capabilities with a smaller limit."""
    shade_types = (
        shade_type(18, "Silhouette"),
        shade_type(23, "Silhouette"),
        shade_type(43, "Facette"),
    )

    capabilities = capability(
        1, "Primary + TiltOnClosed + Tilt90", "Bottom Up Tilt 90°")

    open_position_tilt = {ATTR_POSKIND1: 3, ATTR_POSITION1: MAX_VANE}
    close_position_tilt = {ATTR_POSKIND1: 3, ATTR_POSITION1: MIN_POSITION}


class ShadeBottomUpTiltAnywhere(BaseShade):
    """A shade with move and tilt anywhere capabilities."""
    shade_types = (
        shade_type(62, "Venetian, Tilt anywhere"),
        shade_type(51, "Venetian, Tilt anywhere"),
    )

    capabilities = capability(
        2, "Primary + TiltAnywhere + Tilt180", "Bottom Up Tilt 180°")

    can_tilt = True

    open_position = {
        ATTR_POSKIND1: 1,
        ATTR_POSITION1: MAX_POSITION,
        ATTR_POSKIND2: 3,
        ATTR_POSITION2: MAX_POSITION,
    }

    close_position = {
        ATTR_POSKIND1: 1,
        ATTR_POSITION1: MIN_POSITION,
        ATTR_POSKIND2: 3,
        ATTR_POSITION2: MIN_POSITION,
    }

    open_position_tilt = {ATTR_POSKIND1: 3, ATTR_POSITION1: MAX_POSITION}
    close_position_tilt = {ATTR_POSKIND1: 3, ATTR_POSITION1: MIN_POSITION}

    allowed_positions = (
        {ATTR_POSITION: {ATTR_POSKIND1: 1, ATTR_POSKIND2: 3}, ATTR_COMMAND: ATTR_MOVE},
        {ATTR_POSITION: {ATTR_POSKIND1: 3}, ATTR_COMMAND: ATTR_TILT},
    )


class ShadeVerticalTilt(ShadeBottomUpTilt):
    """A simple open/close vertical shade."""
    # same ability as capability 1 but vertical
    shade_types = (
        shade_type(70, "Curtain Right Stack"),
        shade_type(71, "Curtain Split Stack"),
        shade_type(55, "Vertical Slats Right Stack"),
        shade_type(56, "Vertical Slats Split Stack"),
    )

    capabilities = capability(
        3, "Primary + TiltOnClosed + Tilt180", "Vertical")


class ShadeVerticalTiltInvert(ShadeBottomUpTilt):
    """A simple open/close vertical shade."""
    # inversion of left shade required
    shade_types = (
        shade_type(54, "Vertical Slats Left Stack"),
        shade_type(69, "Curtain Left Stack"),
    )

    capabilities = capability(
        3, "Primary + TiltOnClosed + Tilt180 + VaneInverted", "Vertical")

    invert_vane = True

    open_position_tilt = {ATTR_POSKIND1: 3, ATTR_POSITION1: MIN_POSITION}
    close_position_tilt = {ATTR_POSKIND1: 3, ATTR_POSITION1: MAX_POSITION}


class ShadeVerticalTiltAnywhere(ShadeBottomUpTiltAnywhere):
    """A shade with move and tilt anywhere capabilities."""
    # currently no known shades
    # assuming same capability as type 2 but vertical
    shade_types = (
    )

    capabilities = capability(
        4, "Primary + TiltAnywhere + Tilt180", "Vertical Tilt 180°")


class ShadeTiltOnly(BaseShade):
    """A shade with tilt anywhere capabilities only."""
    # currently no known shades
    shade_types = (
    )

    capabilities = capability(5, "TiltAnywhere + Tilt180", "Tilt Only 180°")

    can_move = False
    can_tilt = True

    open_position = {}
    close_position = {}

    open_position_tilt = {ATTR_POSKIND1: 3, ATTR_POSITION1: MAX_POSITION}
    close_position_tilt = {ATTR_POSKIND1: 3, ATTR_POSITION1: MIN_POSITION}

    allowed_positions = (
        {ATTR_POSITION: {ATTR_POSKIND1: 3}, ATTR_COMMAND: ATTR_TILT},
    )


class ShadeTopDown(BaseShade):
    """A simple top/down shade."""
    shade_types = (
        shade_type(7, "Top Down"),
    )

    capabilities = capability(6, "Primary + PrimaryInverted", "Top Down")

    invert_primary = True

    open_position = {ATTR_POSITION1: MIN_POSITION, ATTR_POSKIND1: 1}
    close_position = {ATTR_POSITION1: MAX_POSITION, ATTR_POSKIND1: 1}

    allowed_positions = (
        {ATTR_POSITION: {ATTR_POSKIND1: 1}, ATTR_COMMAND: ATTR_MOVE},
    )


class ShadeTdbu(BaseShade):
    """A shade with top down bottom up capabilities."""
    shade_types = (
        shade_type(8, "Duette Top Down Bottom Up"),
        shade_type(9, "Duette DuoLite Top Down Bottom Up"),
        shade_type(47, "Pleated Top Down Bottom Up"),
    )

    capabilities = capability(
        7, "Primary + Secondary + TopDown", "Top Down Bottom Up")

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


    shade_types = (
        shade_type(62, "Venetian, tilt anywhere"),
        shade_type(54, "Vertical blind, Left stack"),
        shade_type(55, "Vertical blind, Right stack"),
        shade_type(56, "Vertical blind, Split stack"),
    )

    open_position = {
        ATTR_POSKIND1: 1,
        ATTR_POSITION1: MAX_POSITION,
        ATTR_POSKIND2: 3,
        ATTR_POSITION2: MAX_POSITION,
    }
    close_position = {
        ATTR_POSKIND1: 1,
        ATTR_POSITION1: MIN_POSITION,
        ATTR_POSKIND2: 3,
        ATTR_POSITION2: MIN_POSITION,
    }
    allowed_positions = (
        {ATTR_POSITION: {ATTR_POSKIND1: 1, ATTR_POSKIND2: 3}, ATTR_COMMAND: ATTR_MOVE},
        {ATTR_POSITION: {ATTR_POSKIND1: 3}, ATTR_COMMAND: ATTR_TILT},
    )

    can_tilt = True

    async def tilt_close(self):
        """Tilt vanes to close position"""
        return await self.move({ATTR_POSKIND1: 3, ATTR_POSITION1: MIN_POSITION})

    async def tilt_open(self):
        """Tilt vanes to close position."""
        return await self.move({ATTR_POSKIND1: 3, ATTR_POSITION1: MAX_POSITION})
