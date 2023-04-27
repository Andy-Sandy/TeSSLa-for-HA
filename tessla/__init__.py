"""The TeSSLa integration."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN


_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config):
    """Set up the tessla integration."""
    hass.data[DOMAIN] = {}
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up TeSSLa from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    _LOGGER.warning(f"ConfigEntry {entry.data}")
    # TODO:
    # Forward this information to sensor.py async_setup_entry
    return True


# TODO:
# Add async_unload_entry function
