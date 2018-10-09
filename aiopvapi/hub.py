"""Hub class acting as the base for the PowerView API."""
import logging

from aiopvapi.helpers.api_base import ApiBase
from aiopvapi.helpers.tools import join_path, base64_to_unicode

LOGGER = logging.getLogger(__name__)


class UserData(ApiBase):
    api_path = "api/userdata"

    def __init__(self, request):
        super().__init__(request, self.api_path)
        self.hub_name = None
        self.ip = None
        self.ssid = None
        self._raw = None

    def parse(self, raw):
        """Convert raw incoming to class attributes."""
        self._raw = raw
        self.hub_name = self._parse("userData", "hubName", converter=base64_to_unicode)
        self.ip = self._parse("userData", "ip")
        self.ssid = self._parse("userData", "ssid")

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
    api_path = "api"

    def __init__(self, request):
        super().__init__(request, self.api_path)
        self._main_processor_version = None
        self._radio_version = None
        self.user_data = UserData(request)

    @property
    def main_processor_version(self):
        return self._main_processor_version

    @property
    def radio_version(self):
        return self._radio_version

    @property
    def name(self):
        return self.user_data.hub_name

    @property
    def ip(self):
        return self.user_data.ip

    async def query_firmware(self):
        """Query the firmware versions."""

        _version = await self.request.get(join_path(self._base_path, "/fwversion"))
        _fw = _version.get("firmware")
        if _fw:
            _main = _fw.get("mainProcessor")
            if _main:
                self._main_processor_version = self._make_version(_main)
            _radio = _fw.get("radio")
            if _radio:
                self._radio_version = self._make_version(_radio)

    def _make_version(self, data: dict):
        version = Version(
            data["build"], data["revision"], data["subRevision"], data.get("name")
        )
        return version

    async def query_user_data(self):
        await self.user_data.update_user_data()
