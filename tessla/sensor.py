import time
import threading
import subprocess
import logging
import datetime
import os

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.event import async_track_state_change

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, add_entities):
    """Set up the tessla platform"""
    # Start the TeSSLa interpreter process with the given specification file.
    # the spec file needs to be correctly updated before starting the process
    # Path to tessla files
    tessla_spec_file = os.path.join(
        "homeassistant", "components", "tessla", "specification.tessla"
    )

    tessla_jar_file = os.path.join(
        "homeassistant", "components", "tessla", "tessla.jar"
    )

    tessla_process = subprocess.Popen(
        ["java", "-jar", tessla_jar_file, "interpreter", tessla_spec_file],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1,  # Linebuffer!
        universal_newlines=True,
    )
    _LOGGER.info("Tessla started")

    _LOGGER.warning(f"Config entry said: {config_entry.data}")

    # TODO: Config flow:
    # 1) Get the data from the config entry
    data = config_entry.data
    # 2) Create a list of the the entities with corresponding stream names.
    stream_names = []
    for key in data:
        if key == "stream_name_input":
            stream_name = data[key]
            stream_names.append(stream_name)
    _LOGGER.warning(f"Stream names: {stream_names}")

    input_entities = []
    for key in data:
        if key == "entity_input":
            input_entity = data[key]
            input_entities.append(input_entity)

    # Zip the two lists together to create a list of tuples
    stream_entity_pairs = list(zip(stream_names, input_entities))

    _LOGGER.warning(f"Stream-entity pairs: {stream_entity_pairs}")

    # 3) Add entities in HA.
    # 4) Refactor the code below by removing all hardcoded stuff, everything should be set up from the config entry
    # 5) Get the specification from the config entry and write it to the specification.tessla file

    def tlogger():
        for e in tessla_process.stderr:
            _LOGGER.error(f"Tessla failed: {e}")

    threading.Thread(target=tlogger).start()

    # Hardcoded for testing/example
    ts = TesslaSensor(hass, tessla_process)
    add_entities([ts])

    # Create a separate thread to read and print the TeSSLa output.
    # DON'T START IT YET to avoid race condition
    ts.set_output_thread(
        threading.Thread(target=TesslaReader(hass, tessla_process).output)
    )

    async def _async_state_changed(entity_id, old_state, new_state):
        if new_state is None:
            return

        utc_timestamp = new_state.last_changed

        timestamp = round(
            datetime.datetime.fromisoformat(str(utc_timestamp)).timestamp() * 1000
        )

        tessla_process.stdin.write(f"{timestamp}: x = {int(new_state.state)}\n")
        _LOGGER.warning(f"Tessla notified, value: {new_state}")

    # Register a state change listener for the "sensor.random_sensor" entity
    # TODO: do this for every entity in the config_entry
    for entity in input_entities:
        _LOGGER.warning(f"Entity: {entity}")
        async_track_state_change(hass, entity, _async_state_changed)


class TesslaSensor(SensorEntity):
    """The tesslasensor class"""

    _attr_should_poll = False

    def __init__(self, hass, process):
        self._state = "-1"
        self._hass = hass
        self.tessla = process
        self.j = 1
        self.t = None
        self.running = False

    def set_output_thread(self, t):
        """Set the output thread"""
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
    """The tesslareader class"""

    def __init__(self, hass, tessla):
        self.tessla = tessla
        self.hass = hass

    def output(self):
        """Handles the tessla output"""
        _LOGGER.info("Waiting for Tessla output.")
        # TODO: Replace this with the list from the config entry
        ostreams = {"number": "mapped name1", "diff": "mapped name2"}

        for line in self.tessla.stdout:
            _LOGGER.info(f"Tessla said: {line.strip()}.")
            parts = line.strip().split(" = ")
            if len(parts) != 2:
                _LOGGER.warning("Invalid output format from Tessla: %s", line.strip())
                continue
            output_name = parts[0].split(": ")[1]
            # Only do something if the output has been configured
            if output_name in ostreams:
                value = parts[1]
                entity_id = f"{DOMAIN}.{ostreams[output_name]}"
                entity_state = value.strip()
                self.hass.states.set(entity_id, entity_state)

                _LOGGER.warning("Created new entity: %s=%s", entity_id, entity_state)
            else:
                _LOGGER.warning("Ignored event (No mapping for this output stream))")
