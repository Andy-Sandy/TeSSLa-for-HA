import time
import threading
import subprocess
import logging
import datetime
import os

# from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change

from .const import DOMAIN

# Path to tessla files
tessla_spec_file = os.path.join(
    "homeassistant", "components", "tessla", "specification.tessla"
)
tessla_jar_file = os.path.join("homeassistant", "components", "tessla", "tessla.jar")

_LOGGER = logging.getLogger(__name__)

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
# 2) Get the specification from the config entry and write it to the speceification.tessla file
# This is for the config entry
async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_devices: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    tessla_data = hass.data[DOMAIN][config_entry.entry_id]
    _LOGGER.warning(f"ConfigEntry {config_entry.data}")
    all_entities = [MySensor(tessla_data, tessla_process)]
    async_add_devices(all_entities)


def setup_platform(hass, config, add_entities, discovery_info=None):
    # Start the TeSSLa interpreter process with the given specification file.
    # the spec file needs to be correctly updated before starting the process
    _LOGGER.info("Tessla started")

    def tlogger():
        for e in tessla_process.stderr:
            _LOGGER.error(f"Tessla failed: {e}")

    threading.Thread(target=tlogger).start()

    # TODO: for each sensor in the list retrieved from the config entry, make an entity in HA
    ms = MySensor(hass, tessla_process)
    add_entities([ms])
    # Create a separate thread to read and print the TeSSLa output.
    # DON'T START IT YET to avoid race condition
    ms.set_output_thread(
        threading.Thread(target=TesslaReader(hass, tessla_process).output)
    )

    async def _async_state_changed(entity_id, old_state, new_state):
        if new_state is None:
            return

        utc_timestamp = new_state.last_changed

        timestamp = round(
            datetime.datetime.fromisoformat(str(utc_timestamp)).timestamp() * 1000
        )

        tessla_process.stdin.write(
            # TODO: use time from new_state
            f"{timestamp}: x = {int(new_state.state)}\n"
        )
        _LOGGER.warning(f"Tessla notified, value: {new_state}")

    # Register a state change listener for the "sensor.random_sensor" entity
    # TODO: do this for every entity in the config_entry
    async_track_state_change(hass, "sensor.random_sensor", _async_state_changed)


args = [("x", "sensor.random")]


class MySensor(SensorEntity):
    _attr_should_poll = False

    def __init__(self, hass, process):
        self._state = "-1"
        self._hass = hass
        self.tessla = process
        self.j = 1
        self.t = None
        self.running = False

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


class TesslaReader:
    def __init__(self, hass, tessla):
        self.tessla = tessla
        self.hass = hass

    def output(self):
        _LOGGER.info("Waiting for Tessla output.")
        # TODO: Replace this with the list from the config entry
        ostreams = {"number": "volker", "diff": "Lyslo"}

        for line in self.tessla.stdout:
            _LOGGER.info(f"Tessla said: {line.strip()}.")
            parts = line.strip().split(" = ")
            if len(parts) != 2:
                _LOGGER.warning("Invalid output format from Tessla: %s", line.strip())
                continue
            output_name = parts[0].split(": ")[1]
            # only do something if the output has been configured
            if output_name in ostreams:
                value = parts[1]
                entity_id = f"{DOMAIN}.{ostreams[output_name]}"
                entity_state = value.strip()
                self.hass.states.set(entity_id, entity_state)

                _LOGGER.warning("Created new entity: %s=%s", entity_id, entity_state)
            else:
                _LOGGER.warning("Ignored event (No mapping for this output stream))")
