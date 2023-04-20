import time
import threading
import subprocess

from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_state_change

tessla_spec_file = "specification.tessla"
tessla_jar_file = "tessla.jar"

# Start the TeSSLa interpreter process with the given specification file.
tessla_process = subprocess.Popen(
    ["java", "-jar", tessla_jar_file, "interpreter", tessla_spec_file],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    universal_newlines=True,
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    async_add_entities([MySensor(hass)])


class MySensor(Entity):
    def __init__(self, hass):
        self._state = None
        self._hass = hass

        # Create a separate thread to read and print the TeSSLa output.
        output_thread = threading.Thread(
            target=self.async_update, args=[tessla_process]
        )
        output_thread.start()
        output_thread.join()

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

    async def async_update(self, process):
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

    # Send some integer values to the TeSSLa process using its standard input stream.
    tessla_process.stdin.write("10: x = 2\n")
    tessla_process.stdin.flush()
    time.sleep(1)
    # tessla_process.stdin.write("11: x = 4\n")
    # tessla_process.stdin.flush()
    # time.sleep(1)
    # tessla_process.stdin.write("12: x = 6\n")
    # tessla_process.stdin.flush()

    # Close the input stream to signal that we're done sending input.
    # tessla_process.stdin.close()

    # Wait for the TeSSLa process to exit and for the output thread to finish.
    tessla_process.wait()
