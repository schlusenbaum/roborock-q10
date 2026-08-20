"""Button platform for Roborock Q10."""

from homeassistant.components.button import ButtonEntity
from homeassistant.components.vacuum import DATA_COMPONENT
from homeassistant.exceptions import HomeAssistantError



async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Q10 refresh button."""
    entity_id = (discovery_info or {}).get("entity_id")

    if not entity_id:
        return

    async_add_entities([RoborockQ10RefreshButton(hass, entity_id)])


class RoborockQ10RefreshButton(ButtonEntity):
    """Request a fresh map push from a Roborock Q10."""

    _attr_has_entity_name = True
    _attr_name = "Karte aktualisieren"
    _attr_icon = "mdi:map-refresh"

    def __init__(self, hass, vacuum_entity_id):
        self.hass = hass
        self._vacuum_entity_id = vacuum_entity_id
        object_id = vacuum_entity_id.split(".", 1)[1]
        self.entity_id = f"button.{object_id}_karte_aktualisieren"
        self._attr_unique_id = f"{vacuum_entity_id}_refresh_map"

    async def async_press(self):
        """Request the Q10 to push its current map."""
        entity = self.hass.data[DATA_COMPONENT].get_entity(
            self._vacuum_entity_id
        )

        if entity is None:
            raise HomeAssistantError(
                f"Vacuum entity not found: {self._vacuum_entity_id}"
            )

        await entity.coordinator.api.refresh()
