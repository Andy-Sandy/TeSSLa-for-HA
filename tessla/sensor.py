import logging
import subprocess
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

ATTRIBUTION = "Data provided by Tessla"


def setup_platform(hass, config, add_entities, discovery_info=None):
    existing_sensors = {
        entity.name: entity
        for entity in hass.states.all()
        if entity.domain == "sensor" and entity.name.startswith("Tessla Sensor")
    }
    sensors = []
    added_streams = set()

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
        timestamp, stream_name = stream_name.split(":")
        timestamp = int(timestamp)

        if stream_name in existing_sensors:
            sensor = existing_sensors[f"Tessla Sensor - {stream_name}"]
        elif stream_name in added_streams:
            sensor = sensors[list(added_streams).index(stream_name)]
        else:
            sensor_name = f"Tessla Sensor - {stream_name}"
            sensor = TesslaSensor(sensor_name)
            added_streams.add(stream_name)
            sensors.append(sensor)
            add_entities([sensor])

        sensor.update_state(value)
        sensor.update_attribute("timestamp", timestamp)

    for sensor in sensors:
        sensor.schedule_update_ha_state()


class TesslaSensor(Entity):
    def __init__(self, name):
        self._state = None
        self._name = name
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

    def update_state(self, state):
        self._state = state

    def update_attribute(self, name, value):
        self._attributes[name] = value

    def update(self):
        if self.hass is not None:
            self.schedule_update_ha_state()

    def schedule_update_ha_state(self):
        if self.hass is not None:
            super().schedule_update_ha_state()
