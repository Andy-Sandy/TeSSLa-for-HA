import time
import threading
import subprocess
import logging

from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_state_change

tessla_spec_file = "specification.tessla"
tessla_jar_file = "tessla.jar"

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    # Start the TeSSLa interpreter process with the given specification file.
    tessla_process = subprocess.Popen(
        ["java", "-jar", tessla_jar_file, "interpreter", tessla_spec_file],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    _LOGGER.debug("Tessla started")
    async_add_entities([MySensor(hass, tessla_process)])


class MySensor(Entity):
    def __init__(self, hass, process):
        self._state = None
        self._hass = hass
        self.tessla = process
        self.j = 1

        # Create a separate thread to read and print the TeSSLa output.
        output_thread = threading.Thread(target=self.vs2, argument=[self])
        output_thread.start()

        # Register a state change listener for the "sensor.random_sensor" entity
        async_track_state_change(
            hass, "sensor.random_sensor", self._async_state_changed
        )

    @property
    def name(self):
        return "tessla"

    @property
    def state(self):
        return self._state

    def vs2(me):
        i = 0
        while True:
            line = f"{i}\n"
            _LOGGER.debug(f"vs: {i}")
            me._state = str(i)
            me.schedule_update_ha_state()
            i = i + 1
            time.sleep(1)

    def vs(self):
        process = self.tessla
        while True:
            line = process.stdout.readline()
            if not line:
                break
            print(line.strip())
            self._state = line.strip()
            self.async_schedule_update_ha_state()

    async def _async_state_changed(self, entity_id, old_state, new_state):
        if new_state is None:
            return
        # self.tessla.stdin.write(f"{self.j}: x = {self.j}\n")
        # self.tessla.stdin.flush()
        self.j = self.j + 1
