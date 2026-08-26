from homeassistant import config_entries
from homeassistant.components.vacuum import DATA_COMPONENT
from homeassistant.components.roborock.vacuum import RoborockQ10Vacuum
from homeassistant.core import callback
import voluptuous as vol
from . import DOMAIN

class RoborockQ10ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title=user_input["entity_id"], data=user_input)

        component = self.hass.data.get(DATA_COMPONENT)
        entities = []
        if component is not None:
            for entity in component.entities:
                if isinstance(entity, RoborockQ10Vacuum):
                    entity_id = getattr(entity, "entity_id", None)
                    if entity_id:
                        entities.append(entity_id)

        entities.sort()

        if not entities:
            return self.async_abort(reason="no_vacuum")

        return self.async_show_form(step_id="user", data_schema=vol.Schema({vol.Required("entity_id"): vol.In(entities)}))
