import asyncio

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.components.vacuum import DATA_COMPONENT
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import discovery
from .diagnostics import diagnose


DOMAIN = "roborock_q10"
WS_GET_ROOMS = "roborock_q10/get_rooms"
EVENT_MAP_UPDATED = "roborock_q10_map_updated"


def _room_data(entity):
    api = entity.coordinator.api
    rooms = api.map.rooms or []
    map_data = api.map.map_data

    if not rooms or map_data is None or map_data.image.data is None:
        return []

    import colorsys

    image = map_data.image.data.convert("RGB")
    pixels = image.load()
    width, height = image.size

    sorted_rooms = sorted(rooms, key=lambda room: room.pixel_value)

    colors = {}
    for index, room in enumerate(sorted_rooms):
        rgb = colorsys.hsv_to_rgb(
            (index * 0.139) % 1.0,
            0.5,
            0.95,
        )
        colors[room.pixel_value] = tuple(int(value * 255) for value in rgb)

    result = []

    for room in rooms:
        color = colors.get(room.pixel_value)

        if color is None:
            continue

        points = [
            (x, y)
            for y in range(height)
            for x in range(width)
            if pixels[x, y] == color
        ]

        if not points:
            continue

        result.append(
            {
                "id": str(room.id),
                "name": room.name,
                "x": round(sum(x for x, _ in points) / len(points)),
                "y": round(sum(y for _, y in points) / len(points)),
                "map_width": width,
            }
        )

    return result


def _register_map_listener(hass, entity):
    """Register one throttled listener for this Q10 map."""
    listeners = hass.data.setdefault(DOMAIN, {}).setdefault("listeners", {})

    entity_id = entity.entity_id

    if entity_id in listeners:
        return

    last_fire = 0.0

    def map_updated():
        nonlocal last_fire

        now = hass.loop.time()

        if now - last_fire < 1.0:
            return

        last_fire = now

        image_content = entity.coordinator.api.map.image_content

        if image_content is not None:
            hass.data.setdefault(DOMAIN, {}).setdefault("maps", {})[
                entity_id
            ] = image_content

        rooms = entity.coordinator.api.map.rooms or []

        hass.data.setdefault(DOMAIN, {}).setdefault("rooms", {})[
            entity_id
        ] = [
            {
                "id": room.id,
                "name": room.name,
                "pixel_value": room.pixel_value,
                "pixel_count": room.pixel_count,
            }
            for room in rooms
        ]

    listeners[entity_id] = entity.coordinator.api.map.add_update_listener(
        map_updated
    )

WS_DIAGNOSTICS = "roborock_q10/diagnostics"


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_DIAGNOSTICS,
        vol.Required("entity_id"): cv.entity_id,
        vol.Optional("mode", default="map"): str,
    }
)
@websocket_api.async_response
async def websocket_diagnostics(hass, connection, msg):
    component = hass.data[DATA_COMPONENT]
    entity = component.get_entity(msg["entity_id"])

    if entity is None:
        connection.send_error(
            msg["id"],
            "entity_not_found",
            "Vacuum entity not found",
        )
        return

    if msg["mode"] != "map":
        connection.send_error(
            msg["id"],
            "unknown_mode",
            f"Unknown diagnostic mode: {msg['mode']}",
        )
        return

    connection.send_result(
        msg["id"],
        diagnose_map(entity),
    )

@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_GET_ROOMS,
        vol.Required("entity_id"): cv.entity_id,
    }
)
@websocket_api.async_response
async def websocket_get_rooms(hass, connection, msg):
    component = hass.data[DATA_COMPONENT]
    entity = component.get_entity(msg["entity_id"])

    if entity is None:
        connection.send_error(
            msg["id"],
            "entity_not_found",
            "Vacuum entity not found",
        )
        return

    _register_map_listener(hass, entity)

    rooms = _room_data(entity)

    if not rooms:
        await entity.coordinator.api.refresh()

        for _ in range(25):
            rooms = _room_data(entity)

            if rooms:
                break

            await asyncio.sleep(0.2)

    connection.send_result(
        msg["id"],
        {
            "entity_id": msg["entity_id"],
            "rooms": rooms,
        },
    )


async def async_setup(hass: HomeAssistant, config) -> bool:
    """Set up the Roborock Q10 helper."""
    component = hass.data.setdefault(DOMAIN, {})

    hass.data[DOMAIN]["listeners"] = {}

    async def handle_diagnose(call):
        entity_id = call.data["entity_id"]
        mode = call.data.get("mode", "map")
        entity = hass.data[DATA_COMPONENT].get_entity(entity_id)

        if entity is None:
            raise ValueError(f"Entity not found: {entity_id}")

        result = await diagnose(entity, mode, hass)

        import logging
        logging.getLogger("custom_components.roborock_q10").warning(
            "Q10 DIAGNOSTICS [%s]: %s", mode, result
        )

    hass.services.async_register(
        DOMAIN,
        "diagnose",
        handle_diagnose,
        schema=vol.Schema({
            vol.Required("entity_id"): cv.entity_id,
            vol.Optional("mode", default="map"): str,
        }),
    )

    websocket_api.async_register_command(hass, websocket_get_rooms)
    websocket_api.async_register_command(hass, websocket_diagnostics)

    return True


async def async_setup_entry(hass, entry):
    entity_id = entry.data.get("entity_id")
    if entity_id:
        await discovery.async_load_platform(
            hass,
            "select",
            DOMAIN,
            {"entity_id": entity_id},
            {},
        )
    return True


async def async_unload_entry(hass, entry):
    return True
