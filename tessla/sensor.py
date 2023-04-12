import logging
import subprocess
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

ATTRIBUTION = "Data provided by Tessla"


def setup_platform(hass, config, add_entities, discovery_info=None):
    sensors = []

    command = [
        "java",
        "-jar",
        "/workspaces/core-dev/homeassistant/components/tessla/tessla.jar",
        "interpreter",
        "/workspaces/core-dev/homeassistant/components/tessla/specification.tessla",
        "/workspaces/core-dev/homeassistant/components/tessla/trace.input",
    ]

    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        _LOGGER.error("Error executing command: %s", e)
        return

    for line in output.decode().splitlines():
        stream_name, value = line.strip().split(" = ")

        sensors.append(TesslaSensor(stream_name, value))

    add_entities(sensors)


class TesslaSensor(Entity):
    def __init__(self, stream_name, value):
        self._state = value
        self._name = f"Tessla Sensor - {stream_name}"
        self._attributes = {ATTR_ATTRIBUTION: ATTRIBUTION}

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def device_state_attributes(self):
        return self._attributes

    def update(self):
        pass
