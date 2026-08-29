import logging
from io import BytesIO

from homeassistant.components.image import ImageEntity
from homeassistant.core import callback
from PIL import Image

from . import DOMAIN, EVENT_MAP_UPDATED
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the mirrored Q10 map image."""
    entity_id = entry.data.get("entity_id")
    if not entity_id:
        return

    async_add_entities(
        [RoborockQ10MirroredMapImage(hass, entity_id)]
    )


class RoborockQ10MirroredMapImage(ImageEntity):
    """Display the Q10 map mirrored horizontally."""

    _attr_has_entity_name = True
    _attr_content_type = "image/png"
    _attr_translation_key = "mirrored_map"

    def __init__(self, hass, vacuum_entity_id):
        """Initialize the mirrored Q10 map image."""
        self.hass = hass
        ImageEntity.__init__(self, hass)
        self._vacuum_entity_id = vacuum_entity_id

        object_id = vacuum_entity_id.split(".", 1)[1]

        self._attr_unique_id = f"{vacuum_entity_id}_mirrored_map"
        self.entity_id = f"image.{object_id}_mirrored_map"
        self._cached_image = None

    async def async_added_to_hass(self):
        """Register for Q10 map updates."""
        _LOGGER.debug("Q10 MIRRORED MAP async_added_to_hass")
        await super().async_added_to_hass()
        from homeassistant.helpers import entity_registry as er
        registry = er.async_get(self.hass)
        vacuum_entry = registry.async_get(self._vacuum_entity_id)
        _LOGGER.debug(
            "Q10 MIRRORED MAP VACUUM REGISTRY: %s",
            vacuum_entry,
        )
        _LOGGER.debug(
            "Q10 MIRRORED MAP VACUUM DEVICE_ID: %s",
            vacuum_entry.device_id if vacuum_entry else None,
        )
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

        self._update_image()

    @callback
    def _handle_map_updated(self, event):
        """Update the image when the Q10 map changes."""
        _LOGGER.debug(
            "Q10 MIRRORED MAP EVENT: %s / erwartet: %s",
            event.data.get("entity_id"),
            self._vacuum_entity_id,
        )
        if event.data.get("entity_id") == self._vacuum_entity_id:
            self._update_image()

    def _update_image(self):
        """Create a horizontally mirrored PNG."""
        image_content = (
            self.hass.data.get(DOMAIN, {})
            .get("maps", {})
            .get(self._vacuum_entity_id)
        )

        if image_content is None:
            return
        _LOGGER.debug(
            "Q10 MIRRORED MAP IMAGE FOUND: %s bytes",
            len(image_content),
        )

        with Image.open(BytesIO(image_content)) as image:
            mirrored = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            mirrored = mirrored.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

            output = BytesIO()
            mirrored.save(output, format="PNG")

            self._cached_image = output.getvalue()

        self.async_write_ha_state()

    async def async_image(self):
        """Return the mirrored map image."""
        return self._cached_image
