# from aiopvapi.helpers.constants import ATTR_TYPE, MIN_POSITION, \
#     ATTR_POSKIND2, ATTR_POSKIND1, ATTR_TYPES, \
#     ATTR_ALLOWED_POSITIONS, ATTR_OPEN_POSITION, ATTR_POSITION1, MAX_POSITION, \
#     ATTR_POSITION2, ATTR_CLOSE_POSITION, ATTR_COMMAND, ATTR_MOVE, ATTR_TILT, \
#     ATTR_POSITION
#
# DEFAULT_TYPE = {
#     ATTR_TYPE: 'bottom_up',
#     ATTR_ALLOWED_POSITIONS: [
#         {ATTR_POSITION: {ATTR_POSKIND1: 1}, ATTR_COMMAND: ATTR_MOVE}],
#     ATTR_OPEN_POSITION: {
#         ATTR_POSITION1: MAX_POSITION,
#         ATTR_POSKIND1: 1
#     },
#     ATTR_CLOSE_POSITION: {
#         ATTR_POSITION1: MIN_POSITION,
#         ATTR_POSKIND1: 1
#     },
#     ATTR_TYPES: (42, 6)
# }
#
# SHADE_TYPES = [
#     {
#         ATTR_TYPE: 'tdbu',
#         ATTR_ALLOWED_POSITIONS: [
#             {ATTR_POSITION: {ATTR_POSKIND1: 1, ATTR_POSKIND2: 2},
#              ATTR_COMMAND: ATTR_MOVE}],
#         ATTR_OPEN_POSITION: {
#             ATTR_POSITION1: MAX_POSITION,
#             ATTR_POSITION2: MIN_POSITION,
#             ATTR_POSKIND1: 1,
#             ATTR_POSKIND2: 2
#         },
#         ATTR_CLOSE_POSITION: {
#             ATTR_POSITION1: MIN_POSITION,
#             ATTR_POSITION2: MIN_POSITION,
#             ATTR_POSKIND1: 1,
#             ATTR_POSKIND2: 2
#         },
#         ATTR_TYPES: (8,)
#     }, DEFAULT_TYPE
#     ,
#     {
#         ATTR_TYPE: 'bottom_up_tilt',
#         ATTR_ALLOWED_POSITIONS: [
#             {ATTR_POSITION: {ATTR_POSKIND1: 1},
#              ATTR_COMMAND: ATTR_MOVE},
#             {ATTR_POSITION: {ATTR_POSKIND1: 3},
#              ATTR_COMMAND: ATTR_TILT}
#         ],
#         ATTR_OPEN_POSITION: {
#             ATTR_POSITION1: MAX_POSITION,
#             ATTR_POSKIND1: 1
#         },
#         ATTR_CLOSE_POSITION: {
#             ATTR_POSITION1: MIN_POSITION,
#             ATTR_POSKIND1: 1
#         },
#         ATTR_TYPES: (44,)
#     },
#     {
#         ATTR_TYPE: 'move_tilt_anywhere',
#         ATTR_ALLOWED_POSITIONS: [
#             {ATTR_POSITION: {ATTR_POSKIND1: 1, ATTR_POSKIND2: 3},
#              ATTR_COMMAND: ATTR_MOVE}]
#         ,
#         ATTR_OPEN_POSITION: {
#             ATTR_POSKIND1: 1,
#             ATTR_POSITION1: MAX_POSITION,
#             ATTR_POSKIND2: 3,
#             ATTR_POSITION2: MAX_POSITION,
#         },
#         ATTR_CLOSE_POSITION: {
#             ATTR_POSKIND1: 1,
#             ATTR_POSITION1: MIN_POSITION,
#             ATTR_POSKIND2: 3,
#             ATTR_POSITION2: MIN_POSITION
#         },
#         ATTR_TYPES: (62,)
#     }
# ]
