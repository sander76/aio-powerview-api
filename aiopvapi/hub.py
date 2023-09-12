"""Hub class acting as the base for the PowerView API."""
import logging
from aiopvapi.helpers.aiorequest import PvApiConnectionError

from aiopvapi.helpers.api_base import ApiBase
from aiopvapi.helpers.constants import (
    FUNCTION_IDENTIFY,
    FUNCTION_REBOOT,
    FWVERSION,
    HUB_MODEL_MAPPING,
    HUB_NAME,
    CONFIG,
    FIRMWARE,
    FIRMWARE_MAINPROCESSOR,
    FIRMWARE_NAME,
    FIRMWARE_BUILD,
    FIRMWARE_REVISION,
    FIRMWARE_SUB_REVISION,
    NETWORK_STATUS,
    SERIAL_NUMBER,
    MAC_ADDRESS,
    DEFAULT_LEGACY_MAINPROCESSOR,
    USER_DATA,
)
from aiopvapi.helpers.tools import (
    get_base_path,
    join_path,
    base64_to_unicode,
)

_LOGGER = logging.getLogger(__name__)


class Version:
    """PowerView versioning scheme class."""

    def __init__(self, revision, sub_revision, build, name=None) -> None:
        self._revision = revision
        self._sub_revision = sub_revision
        self._build = build
        self._name = name

    def __repr__(self):
        return "REVISION: {} SUB_REVISION: {} BUILD: {} ".format(
            self._revision, self._sub_revision, self._build
        )

    @property
    def name(self) -> str:
        """Return the name of the device"""
        return self._name

    @property
    def api(self) -> str:
        """
        Return the hardware build of the device.
        This correlates to the api version
        """
        return self._revision

    @property
    def sw_version(self) -> str | None:
        """Version in Home Assistant friendly format"""
        return f"{self._revision}.{self._sub_revision}.{self._build}"

    def __eq__(self, other):
        return str(self) == str(other)


class Hub(ApiBase):
    """Powerview Hub Class"""

    def __init__(self, request) -> None:
        super().__init__(request, self.api_endpoint)
        self._main_processor_version: Version | None = None
        self._radio_version: list[Version] | None = None
        self._raw_firmware: dict | None = None
        self._raw_data: dict | None = None
        self.hub_name = None
        self.ip = None
        self.ssid = None
        self.mac_address = None
        self.serial_number = None
        self.main_processor_info = None

    def is_supported(self, function: str) -> bool:
        """Confirm availble features based on api version"""
        if self.api_version is not None and self.api_version >= 3:
            return function in (FUNCTION_REBOOT, FUNCTION_IDENTIFY)
        return False

    @property
    def role(self) -> str | None:
        """Return the role of the hub in the current system"""
        if self.api_version is None or self.api_version <= 2:
            return "Primary"

        multi_gateway = self._parse(CONFIG, "mgwStatus", "running")
        gateway_primary = self._parse(CONFIG, "mgwConfig", "primary")

        if multi_gateway is False or (multi_gateway and gateway_primary):
            return "Primary"
        return "Secondary"

    @property
    def firmware(self) -> str | None:
        """Return the current firmware version"""
        return self.main_processor_version.sw_version

    @property
    def model(self) -> str | None:
        """Return the freindly name for the model of the hub"""
        return HUB_MODEL_MAPPING.get(
            self.main_processor_version.name, self.main_processor_version.name
        )

    @property
    def hub_address(self) -> str | None:
        """Return the address of the hub"""
        return self.ip

    @property
    def main_processor_version(self) -> Version | None:
        """Return the main processor version"""
        return self._main_processor_version

    @property
    def radio_version(self) -> Version | None:
        """Return the radio version"""
        return self._radio_version

    @property
    def name(self) -> str | None:
        """The name of the device"""
        return self.hub_name

    @property
    def url(self) -> str:
        """Returns the url of the hub

        Used in Home Assistant as configuration url
        """
        if self.api_version >= 3:
            return self.base_path
        return join_path(self.base_path, "shades")

    async def reboot(self) -> None:
        """Reboot the hub"""
        if not self.is_supported("reboot"):
            _LOGGER.error("Method not supported")
            return

        url = get_base_path(self.request.hub_ip, join_path("gateway", "reboot"))
        await self.request.post(url)

    async def identify(self, interval: int = 10) -> None:
        """Identify the hub"""
        if not self.is_supported("identify"):
            _LOGGER.error("Method not supported")
            return

        url = get_base_path(self.request.hub_ip, join_path("gateway", "identify"))
        await self.request.get(url, params={"time": interval})

    async def query_firmware(self):
        """
        Query the firmware versions.  If API version is not set yet, get the API version first.
        """
        await self.detect_api_version()
        if self.api_version >= 3:
            await self._query_firmware_g3()
        else:
            await self._query_firmware_g2()
        _LOGGER.debug("Raw hub data: %s", self._raw_data)

    async def _query_firmware_g2(self):
        # self._raw_data = await self.request.get(join_path(self._base_path, "userdata"))
        self._raw_data = await self.request_raw_data()

        _main = self._parse(USER_DATA, FIRMWARE, FIRMWARE_MAINPROCESSOR)
        if not _main:
            # do some checking for legacy v1 failures
            _fw = await self.request.get(join_path(self.base_path, FWVERSION))
            # _fw = await self.request.get(join_path(self._base_path, FWVERSION))
            if FIRMWARE in _fw:
                _main = self._parse(FIRMWARE, FIRMWARE_MAINPROCESSOR, data=_fw)
            else:
                _main = DEFAULT_LEGACY_MAINPROCESSOR
                # if we are failing here lets drop api version down
                # used in HA as v1 do not support stop
                self.request.api_version = 1
                _LOGGER.debug("Powerview api version changed to %s", self.api_version)

        if _main:
            self._main_processor_version = self._make_version(_main)
        self.main_processor_info = _main

        _radio = self._parse(USER_DATA, FIRMWARE, "radio")
        if _radio:
            # gen 3 has multiple radios, this keeps hub consistent as a list
            self._radio_version = [self._make_version(_radio)]

        self.ip = self._parse(USER_DATA, "ip")
        self.ssid = self._parse(USER_DATA, "ssid")
        self.mac_address = self._parse(USER_DATA, MAC_ADDRESS)
        self.serial_number = self._parse(USER_DATA, SERIAL_NUMBER)

        self.hub_name = self._parse(USER_DATA, HUB_NAME, converter=base64_to_unicode)

    async def _query_firmware_g3(self):
        # self._raw_data = await self.request.get(gateway)
        self._raw_data = await self.request_raw_data()

        _main = self._parse(CONFIG, FIRMWARE, FIRMWARE_MAINPROCESSOR)
        if _main:
            self._main_processor_version = self._make_version(_main)
        self.main_processor_info = _main

        _radios = self._parse(CONFIG, FIRMWARE, "radios")
        if _radios:
            self._radio_version = []
            for _radio in _radios:
                self._radio_version.append(self._make_version(_radio))

        self.ip = self._parse(CONFIG, NETWORK_STATUS, "ipAddress")
        self.ssid = self._parse(CONFIG, NETWORK_STATUS, "ssid")
        self.mac_address = self._parse(CONFIG, NETWORK_STATUS, "primaryMacAddress")
        self.serial_number = self._parse(CONFIG, SERIAL_NUMBER)

        self.hub_name = self.mac_address
        if HUB_NAME not in self._parse(CONFIG):
            # Get gateway name from home API until it is in the gateway API
            home = await self.request_home_data()
            # Find the hub based on the serial number or MAC
            hub = None
            for gateway in home["gateways"]:
                if gateway.get("serial") == self.serial_number:
                    self.hub_name = gateway.get("name")
                    break
                if gateway.get("mac") == self.mac_address:
                    self.hub_name = gateway.get("name")
                    break

            if hub is None:
                _LOGGER.debug(f"Hub with serial {self.serial_number} not found.")

    def _make_version(self, data: dict) -> Version:
        return Version(
            data[FIRMWARE_REVISION],
            data[FIRMWARE_SUB_REVISION],
            data[FIRMWARE_BUILD],
            data.get(FIRMWARE_NAME),
        )

    def _make_version_data_from_str(self, fwVersion: str, name: str = None) -> dict:
        # Split the version string into components
        components = fwVersion.split(".")

        if len(components) != 3:
            raise ValueError("Invalid version format: {}".format(fwVersion))

        revision, sub_revision, build = map(int, components)

        version_data = {
            FIRMWARE_REVISION: revision,
            FIRMWARE_SUB_REVISION: sub_revision,
            FIRMWARE_BUILD: build,
            FIRMWARE_NAME: name,
        }

        return version_data

    async def request_raw_data(self):
        """
        Raw data update request. Allows patching of data for testing
        """
        await self.detect_api_version()
        data_url = join_path(self.base_path, "userdata")
        if self.api_version is not None and self.api_version >= 3:
            data_url = get_base_path(self.request.hub_ip, "gateway")
        return await self.request.get(data_url)

    async def request_home_data(self):
        """
        Raw data update request. Allows patching of data for testing
        """
        await self.detect_api_version()
        data_url = join_path(self.base_path, "userdata")
        if self.api_version is not None and self.api_version >= 3:
            data_url = self.base_path
        return await self.request.get(data_url)
    async def detect_api_version(self):
        """
        Set the API generation based on what the gateway responds to.
        """
        if not self.api_version:
            self._raw_firmware = await self.request_raw_firmware()
            _main = None
            if USER_DATA in self._raw_firmware:
                _main = self._parse(
                    USER_DATA, FIRMWARE, FIRMWARE_MAINPROCESSOR, data=self._raw_firmware
                )
            elif CONFIG in self._raw_firmware:
                _main = self._parse(
                    CONFIG, FIRMWARE, FIRMWARE_MAINPROCESSOR, data=self._raw_firmware
                )
            elif FIRMWARE in self._raw_firmware:
                _main = self._parse(
                    FIRMWARE, FIRMWARE_MAINPROCESSOR, data=self._raw_firmware
                )
            elif "fwVersion" in self._raw_firmware:
                _main = self._make_version_data_from_str(
                    self._raw_firmware.get("fwVersion"), "Powerview Generation 3"
                )

            if _main:
                self._main_processor_version = self._make_version(_main)
                self.request.api_version = self._main_processor_version.api
                _LOGGER.error(self._main_processor_version.api)

        if not self.api_version:
            _LOGGER.error(self._raw_firmware)
