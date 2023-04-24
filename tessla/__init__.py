"""The TeSSLa integration."""
from .const import DOMAIN


async def async_setup(hass, config):
    """Set up the tessla integration."""
    hass.data[DOMAIN] = {}
    return True
