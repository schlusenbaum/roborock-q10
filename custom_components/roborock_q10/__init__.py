import asyncio
import logging

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.components.vacuum import DATA_COMPONENT
from homeassistant.core import HomeAssistant, EVENT_STATE_CHANGED
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import discovery
from .diagnostics import diagnose

_LOGGER = logging.getLogger(__name__)


DOMAIN = "roborock_q10"
WS_GET_ROOMS = "roborock_q10/get_rooms"
EVENT_MAP_UPDATED = "roborock_q10_map_updated"

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


def _register_q10_packet_listener(hass, entity):
    """Store decoded Q10 map packets without modifying the Roborock core."""
    listeners = hass.data.setdefault(DOMAIN, {}).setdefault(
        "packet_listeners", {}
    )

    entity_id = entity.entity_id

    if entity_id in listeners:
        return

    api = entity.coordinator.api
    original_handle_message = api._handle_message

    def wrapped_handle_message(message):
        from roborock.map.b01_q10_map_parser import Q10MapPacket

        if isinstance(message, Q10MapPacket):
            _LOGGER.debug(
                "Q10 PACKET RECEIVED map_id=%s rooms=%s",
                message.map_id,
                len(message.rooms),
            )
            maps = hass.data.setdefault(DOMAIN, {}).setdefault(
                "maps", {}
            ).setdefault(entity_id, {})

            maps[str(message.map_id)] = {
                "map_id": message.map_id,
                "width": message.width,
                "height": message.height,
                "grid": bytes(message.grid),
                "rooms": [
                    {
                        "id": room.id,
                        "name": room.name,
                        "raw_name": room.raw_name,
                        "pixel_value": room.pixel_value,
                    }
                    for room in message.rooms
                ],
            }

            _LOGGER.debug(
                "Q10 MAP EVENT FIRE: %s",
                entity_id,
            )

            hass.bus.async_fire(
                EVENT_MAP_UPDATED,
                {"entity_id": entity_id},
            )

        return original_handle_message(message)

    api._handle_message = wrapped_handle_message
    listeners[entity_id] = original_handle_message


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

        _LOGGER.debug("Q10 MAP UPDATE CALLBACK ausgelöst")

        now = hass.loop.time()

        if now - last_fire < 1.0:
            return

        last_fire = now

        image_content = entity.coordinator.api.map.image_content
        _LOGGER.debug(
            "Q10 MAP IMAGE CONTENT: %s bytes",
            len(image_content) if image_content is not None else None,
        )

        if image_content is not None:
            hass.data.setdefault(DOMAIN, {}).setdefault("maps", {})[
                entity_id
            ] = image_content

            hass.bus.async_fire(
                EVENT_MAP_UPDATED,
                {"entity_id": entity_id},
            )

        map_packet = getattr(entity.coordinator.api.map, "_map_packet", None)
        map_id = getattr(map_packet, "map_id", None)
        rooms = entity.coordinator.api.map.rooms or []
        _LOGGER.debug(
            "Q10 MAP UPDATE ROOMS: %s",
            [(room.id, room.name) for room in rooms],
        )

        hass.data.setdefault(DOMAIN, {}).setdefault("rooms", {})[
            entity_id
        ] = [
            {
                "id": room.id,
                "name": room.name,
                "map_id": map_id,
                "pixel_value": room.pixel_value,
                "pixel_count": room.pixel_count,
            }
            for room in rooms
        ]

    listeners[entity_id] = entity.coordinator.api.map.add_update_listener(
        map_updated
    )
    _LOGGER.debug(
        "Q10 MAP LISTENER REGISTRIERT: %s",
        entity_id,
    )

async def handle_get_rooms(call):
    import logging


    entity_id = call.data["entity_id"]
    entity = call.hass.data[DATA_COMPONENT].get_entity(entity_id)

    if entity is None:
        raise ValueError(f"Entity not found: {entity_id}")



    _LOGGER.debug(
        "Q10 GET_ROOMS: entity=%s gefunden",
        entity_id,
    )

    _register_map_listener(call.hass, entity)

    rooms = entity.coordinator.api.map.rooms or []

    if not rooms:
        await entity.coordinator.api.refresh()
        for _ in range(25):
            rooms = entity.coordinator.api.map.rooms or []
            if rooms:
                break
            await asyncio.sleep(0.2)

    rooms = [
        {
            "id": room.id,
            "name": room.name,
        }
        for room in rooms
    ]

    call.hass.data.setdefault(DOMAIN, {}).setdefault("rooms", {})[entity_id] = rooms

    _LOGGER.debug(
        "Q10 GET_ROOMS: liefert %s Räume: %s",
        len(rooms),
        rooms,
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

    if entity is not None:
        _register_q10_packet_listener(hass, entity)

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


async def handle_clean_rooms(hass, call):
    """Start cleaning selected Q10 rooms."""
    import logging


    entity_id = call.data["entity_id"]

    room_ids = [
        int(room_id)
        for room_id in call.data.get("room_ids", [])
    ]

    entity = hass.data[DATA_COMPONENT].get_entity(entity_id)

    if entity is None:
        raise ValueError(f"Entity not found: {entity_id}")

    room_names = call.data.get("room_names", [])

    if not room_ids and not room_names:
        selected_rooms = (
            hass.data.get(DOMAIN, {})
            .get("selected_rooms", {})
            .get(entity_id, [])
        )

        _LOGGER.debug(
            "Q10 CLEAN SELECTED ROOMS: %s -> %s",
            entity_id,
            selected_rooms,
        )

        if selected_rooms:
            room_names = selected_rooms

    if room_names:
        rooms = entity.coordinator.api.map.rooms or []

        name_to_id = {
            room.name: room.id
            for room in rooms
        }

        for name in room_names:
            if name not in name_to_id:
                raise ValueError(
                    f"Unknown Q10 room name: {name}. Available: {list(name_to_id)}"
                )

            room_ids.append(name_to_id[name])

    known_rooms = (
        hass.data.get(DOMAIN, {})
        .get("rooms", {})
        .get(entity_id, [])
    )

    if known_rooms:
        known_ids = {int(room["id"]) for room in known_rooms}
        unknown_ids = [
            room_id for room_id in room_ids
            if room_id not in known_ids
        ]

        if unknown_ids:
            raise ValueError(
                f"Unknown Q10 room id(s): {unknown_ids}. Available: {sorted(known_ids)}"
            )

    await entity.coordinator.api.vacuum.clean_segments(room_ids)


async def handle_select_rooms(hass, call):
    """Store selected Q10 rooms for later cleaning."""
    entity_id = call.data["entity_id"]
    room_names = call.data.get("room_names", [])

    entity = hass.data[DATA_COMPONENT].get_entity(entity_id)

    if entity is None:
        raise ValueError(f"Entity not found: {entity_id}")

    rooms = entity.coordinator.api.map.rooms or []

    available = {room.name for room in rooms}

    unknown = [
        name for name in room_names
        if name not in available
    ]

    if unknown:
        raise ValueError(
            f"Unknown Q10 room name(s): {unknown}. Available: {sorted(available)}"
        )

    hass.data.setdefault(DOMAIN, {}).setdefault(
        "selected_rooms", {}
    )[entity_id] = room_names

    hass.bus.async_fire(
        "roborock_q10_selected_rooms_updated",
        {
            "entity_id": entity_id,
        },
    )

    _LOGGER.debug(
        "Q10 SELECTED ROOMS: %s -> %s",
        entity_id,
        room_names,
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

        _LOGGER.debug("Q10 DIAGNOSTICS [%s]: %s", mode, result)

    hass.services.async_register(
        DOMAIN,
        "diagnose",
        handle_diagnose,
        schema=vol.Schema({
            vol.Required("entity_id"): cv.entity_id,
            vol.Optional("mode", default="map"): str,
        }),
    )

    hass.services.async_register(
        DOMAIN,
        "get_rooms",
        handle_get_rooms,
        schema=vol.Schema({
            vol.Required("entity_id"): cv.entity_id,
        }),
    )

    async def select_rooms_service(call):
        await handle_select_rooms(hass, call)

    hass.services.async_register(
        DOMAIN,
        "select_rooms",
        select_rooms_service,
        schema=vol.Schema({
            vol.Required("entity_id"): cv.entity_id,
            vol.Required("room_names"): [str],
        }),
    )

    async def clean_rooms_service(call):
        _LOGGER.debug("Q10 SERVICE CALLBACK ERREICHT: %s", call.data)
        await handle_clean_rooms(hass, call)

    hass.services.async_register(
        DOMAIN,
        "clean_rooms",
        clean_rooms_service,
        schema=vol.Schema({
            vol.Required("entity_id"): cv.entity_id,
            vol.Optional("room_ids", default=[]): [int],
            vol.Optional("room_names", default=[]): [str],
        }),
    )

    websocket_api.async_register_command(hass, websocket_get_rooms)
    websocket_api.async_register_command(hass, websocket_diagnostics)

    return True


async def async_setup_entry(hass, entry):
    _LOGGER.debug(
        "Q10 SETUP_ENTRY ERREICHT: %s",
        entry.entry_id,
    )

    entity_id = entry.data.get("entity_id")

    if not entity_id:
        return True

    await hass.config_entries.async_forward_entry_setups(
        entry,
        ["switch", "sensor", "select", "button", "image"],
    )

    for _ in range(25):
        entity = hass.data[DATA_COMPONENT].get_entity(entity_id)

        if entity is not None:
            _register_map_listener(hass, entity)
            await entity.coordinator.api.refresh()
            break

        await asyncio.sleep(0.2)

    return True


async def async_unload_entry(hass, entry):
    return True
