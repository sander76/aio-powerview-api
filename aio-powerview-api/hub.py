
    #

class Hub():
    def __init__(self, hub_ip_address):
        self.ip_address = hub_ip_address
        self._base_path = "http://{}/api".format(hub_ip_address)
        self._scenes_path = "{}/scenes".format(self._base_path)
        self._shades_path = "{}/shades".format(self._base_path)
        self._rooms_path = "{}/rooms".format(self._base_path)
        self._user_path = "{}/userdata/".format(self._base_path)
        self._times_path = "{}/times".format(self._base_path)

        self.all_shades = []

