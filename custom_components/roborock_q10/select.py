import logging

from homeassistant.components.select import SelectEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.components.vacuum import DATA_COMPONENT
from homeassistant.const import EntityCategory
_LOGGER = logging.getLogger(__name__)

from roborock.data.b01_q10.b01_q10_code_mappings import (
    B01_Q10_DP,
    YXWaterLevel,
    YXCleanLine,
)


WATER_LEVELS = {
    "Aus": YXWaterLevel.OFF,
    "Niedrig": YXWaterLevel.LOW,
    "Mittel": YXWaterLevel.MEDIUM,
    "Hoch": YXWaterLevel.HIGH,
}


CLEAN_LINES = {
    "Schnell": YXCleanLine.FAST,
    "Täglich": YXCleanLine.DAILY,
    "Fein": YXCleanLine.FINE,
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

    async_add_entities([
        RoborockQ10WaterLevelSelect(vacuum),
        RoborockQ10CleanLineSelect(vacuum),
        RoborockQ10AutoBoostSwitch(vacuum),
    ])


class RoborockQ10WaterLevelSelect(SelectEntity):
    _attr_entity_category = EntityCategory.CONFIG
    _attr_name = "Wasserfluss"
    _attr_icon = "mdi:water"
    _attr_options = list(WATER_LEVELS)

    def __init__(self, vacuum):
        self._vacuum = vacuum
        self._attr_unique_id = f"{vacuum.entity_id}_water_level"

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        self.async_on_remove(
            self._vacuum.coordinator.api.status.add_update_listener(
                self.async_write_ha_state
            )
        )

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


class RoborockQ10CleanLineSelect(SelectEntity):
    _attr_entity_category = EntityCategory.CONFIG
    _attr_name = "Reinigungsart"
    _attr_icon = "mdi:format-line-spacing"
    _attr_options = list(CLEAN_LINES)

    def __init__(self, vacuum):
        self._vacuum = vacuum
        self._attr_unique_id = f"{vacuum.entity_id}_clean_line"

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        self.async_on_remove(
            self._vacuum.coordinator.api.status.add_update_listener(
                self.async_write_ha_state
            )
        )

    @property
    def current_option(self):
        line = self._vacuum.coordinator.api.status.clean_line

        if line is None:
            return None

        for name, mapped_line in CLEAN_LINES.items():
            if mapped_line == line:
                return name

        return None

    async def async_select_option(self, option):
        line = CLEAN_LINES[option]

        _LOGGER.error("Q10 CLEAN_LINE TEST: option=%s code=%s", option, line.code)

        _LOGGER.error("Q10 SEND CLEAN_LINE: dp=%s code=%s", B01_Q10_DP.CLEAN_LINE, line.code); _LOGGER.error("Q10 COMMAND OBJECT: %r", self._vacuum.coordinator.api.command)

        await self._vacuum.coordinator.api.command.send(
            B01_Q10_DP.CLEAN_LINE,
            params=line.code,
        )

        await self._vacuum.coordinator.api.refresh()
        self.async_write_ha_state()


class RoborockQ10AutoBoostSwitch(SwitchEntity):
    _attr_entity_category = EntityCategory.CONFIG
    _attr_name = "Auto Boost"
    _attr_icon = "mdi:fan-auto"

    def __init__(self, vacuum):
        self._vacuum = vacuum
        self._attr_unique_id = f"{vacuum.entity_id}_auto_boost_switch"

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        self.async_on_remove(
            self._vacuum.coordinator.api.status.add_update_listener(
                self.async_write_ha_state
            )
        )

    @property
    def is_on(self):
        return self._vacuum.coordinator.api.status.auto_boost is True

    async def async_turn_on(self, **kwargs):
        await self._vacuum.coordinator.api.command.send(
            B01_Q10_DP.AUTO_BOOST,
            params=1,
        )
        await self._vacuum.coordinator.api.refresh()

    async def async_turn_off(self, **kwargs):
        await self._vacuum.coordinator.api.command.send(
            B01_Q10_DP.AUTO_BOOST,
            params=0,
        )
        await self._vacuum.coordinator.api.refresh()
