import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, DEFAULT_NAME

DATA_SCHEMA = vol.Schema(
    {
        vol.Optional("entity_id"): str,
        vol.Optional("text"): str,
    }
)


class TesslaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Tessla"""

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        errors = {}
        if user_input is not None:
            # Validate the input
            entity_id = user_input.get("entity_id")
            text = user_input.get("text")

            # Store the input in the data that is passed to the setup method
            self.data = {
                "entity_id": entity_id,
                "text": text,
            }

            # Return the input as the options to be used by the setup method
            return self.async_create_entry(title=DEFAULT_NAME, data=self.data)

        # Show the configuration form to the user
        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return the options flow for this handler."""
        return TesslaOptionsFlow(config_entry)


class TesslaOptionsFlow(config_entries.OptionsFlow):
    """Options flow for your_component_name."""

    def __init__(self, config_entry):
        """Initialize the options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Handle the initialization of the options flow."""
        if user_input is not None:
            # Update the data with the user's input
            self.config_entry.options.update(user_input)
            return self.async_create_entry(title="", data=self.config_entry.options)

        # Show the options form to the user
        return self.async_show_form(step_id="init", data_schema=DATA_SCHEMA, errors={})
