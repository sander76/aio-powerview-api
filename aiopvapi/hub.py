"""Hub class acting as the base for the PowerView API."""
import logging

from aiopvapi.helpers.api_base import ApiBase
from aiopvapi.helpers.constants import (
    HUB_NAME,
    CONFIG,
    FIRMWARE,
    FIRMWARE_MAINPROCESSOR,
    FIRMWARE_NAME,
    FIRMWARE_BUILD,
    FIRMWARE_REVISION,
    FIRMWARE_SUB_REVISION,
    NETWORK_STATUS,
    SERIAL_NUMBER_IN_USERDATA,
    DEFAULT_LEGACY_MAINPROCESSOR,
    USER_DATA,
)
from aiopvapi.helpers.tools import (
    get_base_path,
    join_path,
    base64_to_unicode,
)

LOGGER = logging.getLogger(__name__)


class UserData(ApiBase):
    # Legacy use for version 1 and 2 of API.
    api_path = "userdata"

    def __init__(self, request):
        super().__init__(request, self.api_path)
        self.hub_name = None
        self.ip = None
        self.ssid = None
        self.firmware = None
        self._raw = None

    def parse(self, raw):
        """Convert raw incoming to class attributes."""
        self._raw = raw
        self.hub_name = self._parse(USER_DATA, HUB_NAME, converter=base64_to_unicode)
        self.ip = self._parse(USER_DATA, "ip")
        self.ssid = self._parse(USER_DATA, "ssid")
        self.firmware = self._parse(USER_DATA, FIRMWARE)

    def _parse(self, *keys, converter=None):
        try:
            val = self._raw
            for key in keys:
                val = val[key]
        except KeyError as err:
            LOGGER.error(err)
            return None
        if converter:
            return converter(val)
        return val

    async def update_user_data(self):
        _raw = await self.request.get(self._base_path)
        LOGGER.debug("Raw user data: {}".format(_raw))
        self.parse(_raw)


class Version:
    """PowerView versioning scheme class."""

    def __init__(self, build, revision, sub_revision, name=None):
        self._build = build
        self._revision = revision
        self._sub_revision = sub_revision
        self._name = name

    def __repr__(self):
        return "BUILD: {} REVISION: {} SUB_REVISION: {}".format(
            self._build, self._revision, self._sub_revision
        )

    def __eq__(self, other):
        return str(self) == str(other)


class Hub(ApiBase):
    def __init__(self, request):
        api_version = request.api_version
        if api_version >= 3:
            initial = "gateway"
        else:
            initial = "api"

        super().__init__(request, initial)
        self._main_processor_version = None
        self._radio_version = None
        self.user_data = UserData(request)
        self.hub_name = None
        self.ip = None
        self.ssid = None
        self.mac_address = None
        self.serial_number = None
        self.main_processor_info = None
        self._raw = None

    def _parse(self, *keys, converter=None, data=None):
        val = data if data else self._raw
        try:
            for key in keys:
                val = val[key]
        except KeyError as err:
            LOGGER.error(err)
            return None
        if converter:
            return converter(val)
        return val

    @property
    def main_processor_version(self):
        return self._main_processor_version

    @property
    def radio_version(self):
        return self._radio_version

    @property
    def name(self):
        return self.hub_name

    async def query_firmware(self):
        """
        Query the firmware versions.  If API version is not set yet, get the API version first.
        """
        api_version = self.request.api_version

        if not api_version:
            await self.request.set_api_version()
            api_version = self.request.api_version
            if api_version >= 3:
                initial = "gateway"
            else:
                initial = "api"
            self._base_path = get_base_path(self.request.hub_ip, initial)

        if api_version >= 3:
            await self._query_firmware_g3()
        else:
            await self._query_firmware_g2()

    async def _query_firmware_g2(self):
        await self.user_data.update_user_data()
        self.ip = self.user_data.ip
        self.ssid = self.user_data.ssid
        self.hub_name = self.user_data.hub_name
        _fw = self.user_data.firmware
        _version = await self.request.get(join_path(self._base_path, "/fwversion"))

        if _fw:
            _main = _fw.get("mainProcessor")
            if _main:
                self._main_processor_version = self._make_version(_main)
                self.main_processor_info = _main
            else:
                # Legacy devices
                fwversion = await self.request.get(
                    join_path(self._base_path, "/fwversion")
                )
                resources = await fwversion.get_resources()

                if FIRMWARE in resources:
                    self.main_processor_info = resources[FIRMWARE][
                        FIRMWARE_MAINPROCESSOR
                    ]
                else:
                    self.main_processor_info = DEFAULT_LEGACY_MAINPROCESSOR

            _radio = _fw.get("radio")
            if _radio:
                self._radio_version = self._make_version(_radio)

    async def _query_firmware_g3(self):
        self._raw = await self.request.get(self._base_path)
        _main = self._parse(CONFIG, FIRMWARE, "mainProcessor")
        if _main:
            self._main_processor_version = self._make_version(_main)
        self.main_processor_info = self._parse(CONFIG, FIRMWARE, FIRMWARE_MAINPROCESSOR)
        _radios = self._parse(CONFIG, FIRMWARE, "radios")
        if _radios:
            self._radio_version = []
            for _radio in _radios:
                self._radio_version.append(self._make_version(_radio))

        self.ip = self._parse(CONFIG, NETWORK_STATUS, "ipAddress")
        self.mac_address = self._parse(CONFIG, NETWORK_STATUS, "primaryMacAddress")
        self.ssid = self._parse(CONFIG, NETWORK_STATUS, "ssid")
        self.serial_number = self._parse(CONFIG, SERIAL_NUMBER_IN_USERDATA)

        self.hub_name = self.mac_address
        if HUB_NAME not in self._parse(CONFIG):
            # Get gateway name from home API until it is in the gateway API
            home = await self.request.get(get_base_path(self.request.hub_ip, "home"))
            self.hub_name = home["gateways"][0]["name"]

    def _make_version(self, data: dict):
        version = Version(
            data[FIRMWARE_BUILD],
            data[FIRMWARE_REVISION],
            data[FIRMWARE_SUB_REVISION],
            data.get(FIRMWARE_NAME),
        )
        return version

    async def query_user_data(self):
        await self.user_data.update_user_data()
