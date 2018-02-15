"""Hub class acting as the base for the PowerView API."""

from aiopvapi.helpers.api_base import ApiBase


class Hub(ApiBase):
    api_path = 'api'

    def __init__(self, request):
        super().__init__(request, self.api_path)
