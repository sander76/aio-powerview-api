"""Powerview data models"""

from dataclasses import dataclass
from collections.abc import Iterable
from typing import Any
from aiopvapi.resources.shade import BaseShade
from aiopvapi.hub import Hub
from aiopvapi.resources.scene import Scene
from aiopvapi.resources.automation import Automation
from aiopvapi.resources.room import Room


@dataclass
class PowerviewData:
    """
    Powerview data in raw and processed form

    :raw - raw json from the hub

    :processed - Class Object grouped by id
    """

    raw: Iterable[dict[str | int, Any]]
    processed: dict[str, BaseShade | Hub | Automation | Scene | Room]
