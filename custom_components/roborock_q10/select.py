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


async def async_setup_platform(
    hass,
    config,
    async_add_entities,
    discovery_info=None,
):
    entity_id = discovery_info["entity_id"]
    vacuum = hass.data[DATA_COMPONENT].get_entity(entity_id)

    if vacuum is None:
        return

    async_add_entities([RoborockQ10WaterLevelSelect(vacuum)])


class RoborockQ10WaterLevelSelect(SelectEntity):
    _attr_entity_category = EntityCategory.CONFIG
    _attr_name = "Wasserfluss"
    _attr_icon = "mdi:water"
    _attr_options = list(WATER_LEVELS)

    def __init__(self, vacuum):
        self._vacuum = vacuum
        self._attr_unique_id = f"{vacuum.entity_id}_water_level"

    @property
    def current_option(self):
        level = self._vacuum.coordinator.api.status.water_level

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
