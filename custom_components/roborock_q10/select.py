from homeassistant.components.select import SelectEntity
from homeassistant.components.vacuum import DATA_COMPONENT
from homeassistant.const import EntityCategory

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
    entity_id = entry.data.get("entity_id")

    if not entity_id:
        return

    async_add_entities(
        [
            RoborockQ10WaterLevelSelect(
                hass,
                entity_id,
                entry.entry_id,
            )
        ]
    )


class RoborockQ10WaterLevelSelect(SelectEntity):

    _attr_entity_category = EntityCategory.CONFIG
    _attr_name = "Wasserfluss"
    _attr_icon = "mdi:water"
    _attr_options = list(WATER_LEVELS)

    def __init__(self, hass, vacuum_entity_id, config_entry_id):
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
