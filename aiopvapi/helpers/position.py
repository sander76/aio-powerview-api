from aiopvapi.helpers.constants import ATTR_TYPES, \
    ATTR_POSKIND1, ATTR_POSITION1, ATTR_POSKIND2, ATTR_OPEN_POSITION, \
    ATTR_CLOSE_POSITION, ATTR_ALLOWED_POSITIONS, \
    ATTR_COMMAND, ATTR_MOVE, ATTR_POSITION
from aiopvapi.helpers.shade_types import SHADE_TYPES, DEFAULT_TYPE


class Position:
    def __init__(self, shade_type, raw_position_data=None):
        self._raw_data = None
        self.shade_type = shade_type
        self._open_data = None
        self._close_data = None
        self.behaviour_data = None
        self._init_data()
        self.refresh(raw_position_data)

    def _init_data(self):
        for _type in SHADE_TYPES:
            if self.shade_type in _type[ATTR_TYPES]:
                self.behaviour_data = _type
                break
        else:
            self.behaviour_data = DEFAULT_TYPE
        self._open_data = self.behaviour_data.get(ATTR_OPEN_POSITION)
        self._close_data = self.behaviour_data.get(ATTR_CLOSE_POSITION)
        for _allowed_position in self.behaviour_data[ATTR_ALLOWED_POSITIONS]:
            _val = _allowed_position[ATTR_COMMAND]
            if _val == ATTR_MOVE:
                self._move_data = _allowed_position[ATTR_POSITION]

    def refresh(self, raw_data):
        if raw_data is not None:
            self._raw_data = raw_data

    def get_move_data(self, position1, position2):
        if self._move_data.get(ATTR_POSKIND1):
            if position1:
                self._move_data[ATTR_POSITION1] = position1
        if self._move_data.get(ATTR_POSKIND2):
            if position2:
                self._move_data[ATTR_POSITION1] = position2
        return self._move_data

    # @property
    # def can_tilt(self):
    #     return self._poskind2 == 3
    #
    # @property
    # def has_secondary(self):
    #     return self._poskind2 == 2

    @property
    def open_data(self):
        return self._open_data

    @property
    def close_data(self):
        return self._close_data

        # def _position_data_allowed(self, position_data):
        #     poskind1 = position_data.get(ATTR_POSKIND1)
        #     poskind2 = position_data.get(ATTR_POSKIND2)
        #     _check = {}
        #     if poskind1:
        #         _check[ATTR_POSKIND1] = poskind1
        #     if poskind2:
        #         _check[ATTR_POSKIND2] = poskind2
        #     if _check in self.behaviour_data[ATTR_ALLOWED_POSITIONS]:
        #         return True
        #     return False

        # def get_move_data(self, position_dict):
        #     position1 = position_dict.get(ATTR_POSITION1)
        #     position2 = position_dict.get(ATTR_POSITION2)
        #     poskind1 = position_dict.get(ATTR_POSKIND1)
        #     poskind2 = position_dict.get(ATTR_POSKIND2)
        #     _position = {}
        #     if self.behaviour_data.get(ATTR_POSKIND1):
        #         if position1 is None:
        #             position1 = self._raw_data.get(ATTR_POSITION1)
        #         _position[ATTR_POSKIND1] = self.behaviour_data.get(ATTR_POSKIND1)
        #         _position[ATTR_POSITION1] = position1
        #     if self.behaviour_data.get(ATTR_POSKIND2):
        #         if position2 is None:
        #             position2 = self._raw_data.get(ATTR_POSITION2)
        #         _position[ATTR_POSKIND2] = self.behaviour_data.get(ATTR_POSKIND2)
        #         _position[ATTR_POSITION2] = position2
        #     return _position
