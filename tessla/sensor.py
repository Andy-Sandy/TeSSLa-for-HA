import time
import threading
import subprocess
import logging
import os

# from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.event import async_track_state_change
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN

# Path to tessla files
tessla_spec_file = os.path.join(
    "homeassistant", "components", "tessla", "specification.tessla"
)
tessla_jar_file = os.path.join("homeassistant", "components", "tessla", "tessla.jar")

_LOGGER = logging.getLogger(__name__)

# Start the TeSSLa interpreter process with the given specification file.
tessla_process = subprocess.Popen(
    ["java", "-jar", tessla_jar_file, "interpreter", tessla_spec_file],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    bufsize=1,  # Linebuffer!
    universal_newlines=True,
)


# TODO: Config flow:
# 1) Get the list of entities from the config entry
# 2) Create a new sensor with this list of entities (update the init method of mysensor to allow this)
# 3) In the sensor class add a track_state_change listener to each entity in the list
# 4) Update the state_changed method to send the correct input to tessla
# 5) Get the specification from the config entry and write it to the speceification.tessla file


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the sensor platform."""


def setup_platform(hass, config, add_entities, discovery_info=None):
    _LOGGER.info("Tessla started")

    def tlogger():
        for e in tessla_process.stderr:
            _LOGGER.error(f"Tessla failed: {e}")

    threading.Thread(target=tlogger).start()
    ms = TesslaSensor(hass, tessla_process)
    add_entities([ms])
    # Create a separate thread to read and print the TeSSLa output.
    # DON'T START IT YET to avoid race condition
    ms.set_output_thread(threading.Thread(target=ms.output))


class TesslaSensor(SensorEntity):
    _attr_should_poll = False

    def __init__(self, hass, process):
        self._state = "-1"
        self._hass = hass
        self.tessla = process
        self.j = 1
        self.t = None
        self.running = False

        # Register a state change listener for the "sensor.random_sensor" entity
        async_track_state_change(
            hass, "sensor.random_sensor", self._async_state_changed
        )

    def set_output_thread(self, t):
        self.t = t

    @property
    def name(self):
        return "tessla"

    @property
    def state(self):
        if not self.running and self.t is not None:
            self.t.start()
            self.running = True
            self._state = "Running"
        return self._state

    def output(self):
        _LOGGER.info("Waiting for Tessla output.")

        for line in self.tessla.stdout:
            _LOGGER.info(f"Tessla said: {line.strip()}.")
            parts = line.strip().split(" = ")
            if len(parts) != 2:
                _LOGGER.warning("Invalid output format from Tessla: %s", line.strip())
                continue
            output_name = parts[0].split(": ")[1]
            value = parts[1]
            entity_id = f"{DOMAIN}.{output_name.lower().replace(' ', '_')}"
            entity_state = value.strip()
            self.hass.states.set(entity_id, entity_state)
            self.schedule_update_ha_state()
            _LOGGER.info("Created new entity: %s=%s", entity_id, entity_state)

    async def _async_state_changed(self, entity_id, old_state, new_state):
        if new_state is None:
            return
        self.tessla.stdin.write(f"{self.j}: x = {int(new_state.state)}\n")
        _LOGGER.info(f"Tessla notified, value: {new_state}")
        self.j = self.j + 1
