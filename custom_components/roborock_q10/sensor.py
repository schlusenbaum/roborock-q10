"""Sensor platform for the Roborock Q10 map catalog."""

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.vacuum import DATA_COMPONENT
from homeassistant.core import callback

from . import DOMAIN, EVENT_MAP_UPDATED


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Q10 map catalog sensor."""
    entity_id = entry.data.get("entity_id")

    if not entity_id:
        return

    async_add_entities([RoborockQ10MapCatalogSensor(hass, entity_id)])


class RoborockQ10MapCatalogSensor(SensorEntity):
    """Display known Q10 maps and their rooms."""

    _attr_has_entity_name = True
    _attr_name = "Kartenübersicht"
    _attr_icon = "mdi:map-legend"

    def __init__(self, hass, vacuum_entity_id):
        self.hass = hass
        self._vacuum_entity_id = vacuum_entity_id
        object_id = vacuum_entity_id.split(".", 1)[1]
        self.entity_id = f"sensor.{object_id}_kartenuebersicht"
        self._attr_unique_id = f"{vacuum_entity_id}_map_catalog"

    @property
    def native_value(self):
        """Return the number of known maps."""
        return len(self._catalog())

    @property
    def extra_state_attributes(self):
        """Return map and room metadata."""
        maps = []

        for item in sorted(
            self._catalog().values(),
            key=lambda entry: entry["map_id"],
        ):
            rooms = item.get("rooms", [])
            maps.append(
                {
                    "map_id": item["map_id"],
                    "size": f'{item["width"]} × {item["height"]}',
                    "room_count": len(rooms),
                    "rooms": [room["name"] for room in rooms],
                }
            )

        return {"maps": maps}

    async def async_added_to_hass(self):
        """Update whenever a Q10 map packet is received."""
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
        if event.data.get("entity_id") == self._vacuum_entity_id:
            self.async_write_ha_state()

    def _catalog(self):
        return (
            self.hass.data.get(DOMAIN, {})
            .get("map_catalog", {})
            .get(self._vacuum_entity_id, {})
        )
