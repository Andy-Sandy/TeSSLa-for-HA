import voluptuous as vol
from typing import Any
from homeassistant.core import HomeAssistant
from homeassistant import config_entries

from .const import DOMAIN

ENTITY_INPUT = "ENTITY_input"


async def validate_input(hass: HomeAssistant, data: dict) -> dict[str, Any]:
    """Validate the user input"""
    return {"title": data["entity"]}


class TesslaFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a My Component config flow."""

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
                vol.Required(ENTITY_INPUT): str,
                vol.Inclusive(
                    "entity_ids",
                    "step1",
                    default=entities[0],
                ): vol.All(vol.Coerce(str), vol.In(entities)),
                vol.Inclusive(
                    "text", "step1", description="Enter some text", default=""
                ): str,
            }
        )

        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=data_schema)
        errors = {}

        if user_input is not None:
            info = validate_input(self.hass, user_input)
            return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(step_id="user", data_schema=data_schema)
