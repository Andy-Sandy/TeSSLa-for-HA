import voluptuous as vol
from typing import Any
from homeassistant.core import HomeAssistant
from homeassistant import config_entries

from .const import DOMAIN

ENTITY_INPUT = "entity_input"
STREAM_NAME_INPUT = "stream_name_input"
TESLA_SPEC_INPUT = "tesla_spec_input"

# TODO:
# 1) Add the ability to configure multiple entities with corresponding stream names
# 2) Add headings and hints to fields in config flow


async def validate_input(hass: HomeAssistant, data: dict) -> dict[str, Any]:
    """Validate the user input"""
    return {"title": data[STREAM_NAME_INPUT]}


class TesslaFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a TeSSLa config flow."""

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        entities = []
        for entity in self.hass.states.async_all():
            if entity.entity_id.startswith("sensor.") or entity.entity_id.startswith(
                "binary_sensor."
            ):
                entities.append(entity.entity_id)
        entities.sort()

        data_schema = vol.Schema(
            {
                vol.Required(STREAM_NAME_INPUT, default=""): str,
                vol.Required(ENTITY_INPUT, default=entities[0]): vol.In(entities),
                vol.Required(TESLA_SPEC_INPUT, default=""): str,
            }
        )

        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=data_schema)

        errors = {}
        if user_input is not None:
            info = await validate_input(self.hass, user_input)
            return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(step_id="user", data_schema=data_schema)
