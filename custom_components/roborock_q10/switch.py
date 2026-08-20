"""Switch platform for Roborock Q10."""

from datetime import timedelta
import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.components.vacuum import DATA_COMPONENT
from homeassistant.const import STATE_ON
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.restore_state import RestoreEntity

_LOGGER = logging.getLogger(__name__)
_REFRESH_INTERVAL = timedelta(minutes=15)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the periodic Q10 refresh switch."""
    entity_id = (discovery_info or {}).get("entity_id")

    if not entity_id:
        return

    async_add_entities([RoborockQ10PeriodicRefreshSwitch(hass, entity_id)])


class RoborockQ10PeriodicRefreshSwitch(RestoreEntity, SwitchEntity):
    """Enable periodic Q10 map refreshes."""

    _attr_has_entity_name = True
    _attr_name = "Automatische Kartenaktualisierung"
    _attr_icon = "mdi:refresh-auto"

    def __init__(self, hass, vacuum_entity_id):
        self.hass = hass
        self._vacuum_entity_id = vacuum_entity_id
        self._remove_interval = None
        object_id = vacuum_entity_id.split(".", 1)[1]
        self.entity_id = (
            f"switch.{object_id}_automatische_kartenaktualisierung"
        )
        self._attr_unique_id = f"{vacuum_entity_id}_periodic_map_refresh"
        self._attr_is_on = False

    async def async_added_to_hass(self):
        """Restore the previous switch state."""
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()
        self._attr_is_on = (
            last_state is not None and last_state.state == STATE_ON
        )

        if self._attr_is_on:
            self._start_interval()

    async def async_will_remove_from_hass(self):
        """Cancel the scheduled refresh."""
        self._stop_interval()
        await super().async_will_remove_from_hass()

    async def async_turn_on(self, **kwargs):
        """Enable a refresh every 15 minutes."""
        self._attr_is_on = True
        self._start_interval()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Disable periodic refreshes."""
        self._attr_is_on = False
        self._stop_interval()
        self.async_write_ha_state()

    def _start_interval(self):
        if self._remove_interval is None:
            self._remove_interval = async_track_time_interval(
                self.hass,
                self._async_refresh,
                _REFRESH_INTERVAL,
            )

    def _stop_interval(self):
        if self._remove_interval is not None:
            self._remove_interval()
            self._remove_interval = None

    async def _async_refresh(self, _now):
        """Request a fresh map push."""
        entity = self.hass.data[DATA_COMPONENT].get_entity(
            self._vacuum_entity_id
        )

        if entity is None:
            _LOGGER.warning(
                "Q10 PERIODIC REFRESH SKIPPED: entity_id=%s",
                self._vacuum_entity_id,
            )
            return

        try:
            await entity.coordinator.api.refresh()
        except Exception as err:
            _LOGGER.warning(
                "Q10 PERIODIC REFRESH FAILED: entity_id=%s error=%s",
                self._vacuum_entity_id,
                err,
            )
        else:
            _LOGGER.warning(
                "Q10 PERIODIC REFRESH: entity_id=%s",
                self._vacuum_entity_id,
            )
