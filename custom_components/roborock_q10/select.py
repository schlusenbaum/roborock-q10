import logging

from homeassistant.components.select import SelectEntity
from homeassistant.components.vacuum import DATA_COMPONENT
from homeassistant.const import EntityCategory
from homeassistant.core import callback

from . import DOMAIN, EVENT_MAP_UPDATED

_LOGGER = logging.getLogger(__name__)

from roborock.data.b01_q10.b01_q10_code_mappings import (
    B01_Q10_DP,
    YXWaterLevel,
)


WATER_LEVELS = {
    "Aus": YXWaterLevel.OFF,
    "Niedrig": YXWaterLevel.LOW,
    "Mittel": YXWaterLevel.MEDIUM,
    "Hoch": YXWaterLevel.HIGH,
}


async def async_setup_entry(hass, entry, async_add_entities):
    _LOGGER.debug("Q10 SELECT SETUP ENTRY")
    entity_id = entry.data.get("entity_id")

    if not entity_id:
        return

    _LOGGER.debug("Q10 SELECT ADD ENTITIES")

    async_add_entities(
        [
            RoborockQ10WaterLevelSelect(
                hass,
                entity_id,
                entry.entry_id,
            ),
            RoborockQ10RoomSelect(
                hass,
                entity_id,
                entry.entry_id,
            ),
        ]
    )


class RoborockQ10WaterLevelSelect(SelectEntity):

    _attr_entity_category = EntityCategory.CONFIG
    _attr_name = "Wasserfluss"
    _attr_icon = "mdi:water"
    _attr_options = list(WATER_LEVELS)

    def __init__(self, hass, vacuum_entity_id, config_entry_id):
        _LOGGER.debug(
            "Q10 ROOM SELECT INIT: %s",
            vacuum_entity_id,
        )
        self.hass = hass
        self._vacuum_entity_id = vacuum_entity_id
        self._config_entry_id = config_entry_id
        self._attr_unique_id = f"{vacuum_entity_id}_water_level"

    @property
    def _vacuum(self):
        return self.hass.data[DATA_COMPONENT].get_entity(
            self._vacuum_entity_id
        )

    @property
    def device_info(self):
        return {
            "identifiers": {
                ("roborock", "28ZcwX5EXBeo0jly70p9oF")
            },
        }

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

        vacuum = self._vacuum

        if vacuum is not None:
            self.async_on_remove(
                vacuum.coordinator.api.status.add_update_listener(
                    self.async_write_ha_state
                )
            )

    @property
    def current_option(self):
        vacuum = self._vacuum

        if vacuum is None:
            return None

        level = vacuum.coordinator.api.status.water_level

        if level is None:
            return None

        for name, mapped_level in WATER_LEVELS.items():
            if mapped_level == level:
                return name

        return None

    async def async_select_option(self, option):
        level = WATER_LEVELS[option]

        await self._vacuum.coordinator.api.command.send(
            B01_Q10_DP.WATER_LEVEL,
            params=level.code,
        )

        await self._vacuum.coordinator.api.refresh()
        self.async_write_ha_state()



class RoborockQ10RoomSelect(SelectEntity):
    """Select a Q10 room for cleaning."""

    _attr_name = "Reinigungsraum"
    _attr_icon = "mdi:floor-plan"

    def __init__(self, hass, vacuum_entity_id, config_entry_id):
        self.hass = hass
        self._vacuum_entity_id = vacuum_entity_id
        self._config_entry_id = config_entry_id
        self._attr_unique_id = f"{vacuum_entity_id}_clean_room"
        self._attr_current_option = None

    @property
    def _vacuum(self):
        return self.hass.data[DATA_COMPONENT].get_entity(
            self._vacuum_entity_id
        )

    @property
    def device_info(self):
        return {
            "identifiers": {
                ("roborock", self._vacuum_entity_id)
            },
        }

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
        if event.data.get("entity_id") == self._vacuum_entity_id:
            self.async_write_ha_state()

    @property
    def options(self):
        vacuum = self._vacuum

        if vacuum is None:
            return ["Alle"]

        rooms = vacuum.coordinator.api.map.rooms or []

        return ["Alle"] + [room.name for room in rooms]

    @property
    def current_option(self):
        return self._attr_current_option

    async def async_select_option(self, option):
        if option == "Alle":
            self._attr_current_option = None
        else:
            self._attr_current_option = option

        self.hass.data.setdefault(DOMAIN, {}).setdefault(
            "selected_rooms", {}
        )[self._vacuum_entity_id] = self._attr_current_option

        _LOGGER.debug(
            "Q10 SELECTED ROOM: %s -> %s",
            self._vacuum_entity_id,
            self._attr_current_option,
        )

        self.async_write_ha_state()
