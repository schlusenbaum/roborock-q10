"""Button platform for Roborock Q10."""

from homeassistant.components.button import ButtonEntity
from homeassistant.components.vacuum import DATA_COMPONENT
from homeassistant.exceptions import HomeAssistantError



async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Q10 refresh button."""
    entity_id = entry.data.get("entity_id")

    if not entity_id:
        return

    async_add_entities(
        [
            RoborockQ10RefreshButton(
                hass,
                entity_id,
                entry.entry_id,
            ),
            RoborockQ10CleanSelectedRoomButton(
                hass,
                entity_id,
                entry.entry_id,
            ),
        ]
    )
    
class RoborockQ10RefreshButton(ButtonEntity):
    """Request a fresh map push from a Roborock Q10."""

    _attr_has_entity_name = True
    _attr_name = "Karte aktualisieren"
    _attr_icon = "mdi:map-refresh"

    def __init__(self, hass, vacuum_entity_id, config_entry_id):
        self._config_entry_id = config_entry_id
        self.hass = hass
        self._vacuum_entity_id = vacuum_entity_id
        object_id = vacuum_entity_id.split(".", 1)[1]
        self.entity_id = f"button.{object_id}_karte_aktualisieren"
        self._attr_unique_id = f"{vacuum_entity_id}_refresh_map"

    async def async_added_to_hass(self):
        """Attach button to the existing vacuum device."""
        await super().async_added_to_hass()

        from homeassistant.helpers import entity_registry as er

        registry = er.async_get(self.hass)

        vacuum_entry = registry.async_get(self._vacuum_entity_id)

        if vacuum_entry and vacuum_entry.device_id:
            registry.async_update_entity(
                self.entity_id,
                device_id=vacuum_entry.device_id,
            )

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


class RoborockQ10CleanSelectedRoomButton(ButtonEntity):
    """Clean the selected Q10 room."""

    _attr_has_entity_name = True
    _attr_name = "Ausgewählte Räume reinigen"
    _attr_icon = "mdi:floor-plan"

    def __init__(self, hass, vacuum_entity_id, config_entry_id):
        self.hass = hass
        self._vacuum_entity_id = vacuum_entity_id
        self._config_entry_id = config_entry_id

        object_id = vacuum_entity_id.split(".", 1)[1]
        self.entity_id = f"button.{object_id}_ausgewaehlten_raum_reinigen"
        self._attr_unique_id = f"{vacuum_entity_id}_clean_selected_room"

    async def async_added_to_hass(self):
        """Attach button to the existing vacuum device."""
        await super().async_added_to_hass()

        from homeassistant.helpers import entity_registry as er

        registry = er.async_get(self.hass)
        vacuum_entry = registry.async_get(self._vacuum_entity_id)

        if vacuum_entry and vacuum_entry.device_id:
            registry.async_update_entity(
                self.entity_id,
                device_id=vacuum_entry.device_id,
            )

    async def async_press(self):
        """Start cleaning the selected room."""
        await self.hass.services.async_call(
            "roborock_q10",
            "clean_rooms",
            {
                "entity_id": self._vacuum_entity_id,
            },
        )
