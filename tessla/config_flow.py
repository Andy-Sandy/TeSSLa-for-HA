import voluptuous as vol
from typing import Any
from homeassistant.core import HomeAssistant
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN

ENTITY_INPUT_1 = "entity_input_1"
ENTITY_INPUT_2 = "entity_input_2"
STREAM_NAME_INPUT_1 = "stream_name_input_1"
STREAM_NAME_INPUT_2 = "stream_name_input_2"
TESSLA_SPEC_INPUT = "tessla_spec_input"

# TODO:
# 1) Add the ability to configure multiple entities with corresponding stream names


async def validate_input(hass: HomeAssistant, data: dict) -> dict[str, Any]:
    """Validate the user input"""
    return {"title": data[STREAM_NAME_INPUT_1]}


class TesslaFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a TeSSLa config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        entities = []
        for entity in self.hass.states.async_all():
            entities.append(entity.entity_id)
        entities.sort()

        data_schema = vol.Schema(
            {
                vol.Required(STREAM_NAME_INPUT_1): str,
                vol.Required(STREAM_NAME_INPUT_2): str,
                vol.Required(ENTITY_INPUT_1): vol.In(entities),
                vol.Required(ENTITY_INPUT_2): vol.In(entities),
                vol.Required(TESSLA_SPEC_INPUT): str,
            }
        )

        errors = {}
        if user_input is not None:
            info = await validate_input(self.hass, user_input)
            return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(step_id="user", data_schema=data_schema)
