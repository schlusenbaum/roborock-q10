"""Sensor platform for the Roborock Q10 map catalog."""

import logging

_LOGGER = logging.getLogger(__name__)

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.vacuum import DATA_COMPONENT
from homeassistant.core import callback

from . import DOMAIN, EVENT_MAP_UPDATED

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Q10 map catalog sensor."""
    entity_id = entry.data.get("entity_id")

    if not entity_id:
        return

    async_add_entities([
        RoborockQ10RoomsSensor(hass, entity_id),
        RoborockQ10SelectedRoomsSensor(hass, entity_id),
    ])


class RoborockQ10RoomsSensor(SensorEntity):
    _attr_has_entity_name = True
    _attr_icon = "mdi:floor-plan"

    def __init__(self, hass, vacuum_entity_id):
        self.hass = hass
        self._vacuum_entity_id = vacuum_entity_id
        object_id = vacuum_entity_id.split(".", 1)[1]
        self.entity_id = f"sensor.{object_id}_rooms"
        self._attr_translation_key = "rooms"
        self._attr_unique_id = f"{vacuum_entity_id}_rooms"

    @property
    def native_value(self):
        return len(self._rooms())

    @property
    def extra_state_attributes(self):
        return {"rooms": self._rooms()}

    async def async_added_to_hass(self):
        await super().async_added_to_hass()

        from homeassistant.helpers import entity_registry as er

        registry = er.async_get(self.hass)
        vacuum_entry = registry.async_get(self._vacuum_entity_id)

        if vacuum_entry and vacuum_entry.device_id:
            registry.async_update_entity(
                self.entity_id,
                device_id=vacuum_entry.device_id,
            )

        self.async_on_remove(
            self.hass.bus.async_listen(
                EVENT_MAP_UPDATED,
                self._handle_map_updated,
            )
        )

    @callback
    def _handle_map_updated(self, event):
        _LOGGER.debug(
            "Q10 SENSOR MAP EVENT: %s / erwartet: %s",
            event.data.get("entity_id"),
            self._vacuum_entity_id,
        )
        if event.data.get("entity_id") == self._vacuum_entity_id:
            self.async_write_ha_state()

    def _rooms(self):
        return (
            self.hass.data.get(DOMAIN, {})
            .get("rooms", {})
            .get(self._vacuum_entity_id, [])
        )


class RoborockQ10SelectedRoomsSensor(SensorEntity):
    """Show selected Q10 cleaning rooms."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:format-list-checks"

    def __init__(self, hass, vacuum_entity_id):
        self.hass = hass
        self._vacuum_entity_id = vacuum_entity_id

        object_id = vacuum_entity_id.split(".", 1)[1]
        self.entity_id = f"sensor.{object_id}_selected_rooms"
        self._attr_translation_key = "selected_rooms"
        self._attr_unique_id = f"{vacuum_entity_id}_selected_rooms"

    @property
    def native_value(self):
        return ", ".join(self._rooms())

    @property
    def extra_state_attributes(self):
        return {
            "rooms": self._rooms(),
        }

    def _rooms(self):
        rooms = (
            self.hass.data.get(DOMAIN, {})
            .get("selected_rooms", {})
            .get(self._vacuum_entity_id, [])
        )

        if isinstance(rooms, str):
            return [rooms]

        return list(rooms)

    async def async_added_to_hass(self):
        await super().async_added_to_hass()

        from homeassistant.helpers import entity_registry as er

        registry = er.async_get(self.hass)
        vacuum_entry = registry.async_get(self._vacuum_entity_id)

        if vacuum_entry and vacuum_entry.device_id:
            registry.async_update_entity(
                self.entity_id,
                device_id=vacuum_entry.device_id,
            )

        self.async_on_remove(
            self.hass.bus.async_listen(
                "roborock_q10_selected_rooms_updated",
                self._handle_update,
            )
        )

    @callback
    def _handle_update(self, event):
        if event.data.get("entity_id") == self._vacuum_entity_id:
            self.async_write_ha_state()
