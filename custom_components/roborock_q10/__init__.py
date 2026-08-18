import asyncio

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.components.vacuum import DATA_COMPONENT
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import discovery


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

        import logging
        logging.getLogger("custom_components.roborock_q10").warning(
            EVENT_MAP_UPDATED,
            {"entity_id": entity_id},
        )

    listeners[entity_id] = entity.coordinator.api.map.add_update_listener(
        map_updated
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

    websocket_api.async_register_command(hass, websocket_get_rooms)

    async def load_select(event):
        await discovery.async_load_platform(
            hass,
            "select",
            DOMAIN,
            {"entity_id": "vacuum.roborock_q10_s5"},
            config,
        )

    hass.bus.async_listen_once("homeassistant_started", load_select)

    return True
