"""The Tessla custom component."""
import subprocess

DOMAIN = "tessla_custom"


async def async_setup(hass, config):
    """Set up the Tessla custom component."""
    # Set up your component here

    # Run TeSSLa
    command = "java -jar tessla.jar interpreter specification.tessla trace.input"

    # store the output
    output = subprocess.run(command)
    return True
